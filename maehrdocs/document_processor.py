"""
DocumentProcessor für MaehrDocs
Hauptklasse zur Verarbeitung von Dokumenten
"""

import os
import logging
import time

from maehrdocs.text_extractor import TextExtractor
from maehrdocs.openai_integration import OpenAIIntegration
from maehrdocs.file_operations import FileOperations
from maehrdocs.filename_generator import FilenameGenerator
from maehrdocs.duplicate_detector import DuplicateDetector

class DocumentProcessor:
    """
    Hauptklasse zur Verarbeitung von Dokumenten
    Koordiniert die Aktionen der verschiedenen Module
    """
    
    def __init__(self, config):
        """
        Initialisiert den DocumentProcessor mit der Konfiguration
        
        Args:
            config (dict): Konfiguration für die Dokumentenverarbeitung
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialisiere die Hilfsmodule
        self.text_extractor = TextExtractor()
        self.openai_integration = OpenAIIntegration(config)
        self.file_operations = FileOperations(config)
        self.filename_generator = FilenameGenerator(config)
        self.duplicate_detector = DuplicateDetector()
        
        # Optionen
        self.verbose = 0  # Ausführlichkeitsstufe (0=normal, 1=verbose, 2=debug)
        self.force = False  # Dateien überschreiben
    
    def process_document(self, file_path, dry_run=False, force=False):
        """
        Verarbeitet ein einzelnes Dokument
        
        Args:
            file_path (str): Pfad zur PDF-Datei
            dry_run (bool): Wenn True, werden keine Dateioperationen durchgeführt
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            dict: Ergebnis der Verarbeitung oder None bei Fehler
        """
        try:
            # Zeit messen
            start_time = time.time()
            
            # Lokale Force-Option setzen
            self.force = force
            
            # Log
            self.logger.info(f"Verarbeite Dokument: {file_path}")
            
            # Prüfe, ob die Datei existiert und eine gültige PDF ist
            if not self.text_extractor.is_valid_pdf(
                file_path, 
                max_size_mb=self.config.get('document_processing', {}).get('max_file_size_mb', 20)
            ):
                return None
            
            # Text aus PDF extrahieren
            text = self.text_extractor.extract_text_from_pdf(file_path)
            if not text:
                self.logger.error(f"Konnte keinen Text aus der PDF extrahieren: {file_path}")
                return None
            
            # OpenAI-API verwenden, um Metadaten zu extrahieren
            valid_doc_types = self.config.get('document_processing', {}).get('valid_doc_types', [])
            doc_info = self.openai_integration.analyze_document(text, valid_doc_types)
            if not doc_info:
                self.logger.error(f"Fehler bei der KI-Analyse des Dokuments: {file_path}")
                return None
            
            # Prüfe, ob das Dokument ein Duplikat ist
            is_duplicate, duplicate_path = self._check_for_duplicates(text, file_path)
            
            # Erzeuge einen neuen Dateinamen basierend auf den extrahierten Informationen
            new_filename = self.filename_generator.generate_filename(doc_info)
            if not new_filename:
                self.logger.error(f"Konnte keinen gültigen Dateinamen generieren: {file_path}")
                return None
            
            # Ergebnisbericht erstellen
            result = {
                "original_file": file_path,
                "extracted_info": doc_info,
                "new_filename": new_filename,
                "is_duplicate": is_duplicate,
                "duplicate_path": duplicate_path if is_duplicate else None,
                "processing_time": time.time() - start_time
            }
            
            # Wenn nicht im Simulationsmodus, führe die Dateioperationen aus
            if not dry_run:
                self._move_file(file_path, new_filename, is_duplicate, force)
            else:
                self.logger.info(f"[SIMULATION] Würde Datei verschieben: {file_path} -> {new_filename}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung von {file_path}: {str(e)}", exc_info=True)
            return None
    
    def _check_for_duplicates(self, text, file_path):
        """
        Prüft, ob das Dokument ein Duplikat eines bereits verarbeiteten Dokuments ist.
        
        Vergleicht den extrahierten Text mit den Texten bereits verarbeiteter Dokumente
        im Ausgabeordner und berechnet Ähnlichkeitswerte, um Duplikate zu erkennen.
        
        Args:
            text (str): Der extrahierte Text des Dokuments
            file_path (str): Pfad zur Originaldatei
            
        Returns:
            tuple: (is_duplicate, duplicate_path) - Ob es ein Duplikat ist und Pfad zum Original
        """
        # Standardwerte
        is_duplicate = False
        duplicate_path = None
        
        # Einstellungen aus der Konfiguration laden
        threshold = self.config.get('document_processing', {}).get('similarity_threshold', 0.85)
        check_output = self.config.get('duplicate_detection', {}).get('check_in_output_dir', True)
        
        # Wenn Duplikaterkennung deaktiviert ist, sofort zurückkehren
        if not self.config.get('duplicate_detection', {}).get('enabled', True):
            return is_duplicate, duplicate_path
        
        try:
            # Ausgabeordner, falls überprüft werden soll
            output_dir = self.config.get('paths', {}).get('output_dir', '')
            if check_output and os.path.exists(output_dir):
                # Dateien im Ausgabeordner durchsuchen
                for filename in os.listdir(output_dir):
                    if filename.lower().endswith('.pdf'):
                        compare_path = os.path.join(output_dir, filename)
                        
                        # Eigene Datei überspringen (bei erneutem Verarbeiten)
                        if os.path.samefile(file_path, compare_path):
                            continue
                        
                        # Text aus Vergleichsdatei extrahieren
                        compare_text = self.text_extractor.extract_text_from_pdf(compare_path)
                        if not compare_text:
                            continue
                        
                        # Ähnlichkeit berechnen
                        similarity = self.duplicate_detector.calculate_similarity(text, compare_text)
                        
                        # Log für Debugging
                        if self.verbose > 1:
                            self.logger.debug(f"Ähnlichkeit mit {filename}: {similarity:.4f}")
                        
                        # Wenn die Ähnlichkeit den Schwellenwert überschreitet
                        if similarity >= threshold:
                            is_duplicate = True
                            duplicate_path = compare_path
                            
                            # Log und Benachrichtigung
                            self.logger.warning(
                                f"DUPLICATE DETECTED: [Original: {filename}] "
                                f"[Duplicate: {os.path.basename(file_path)}] "
                                f"[Similarity: {similarity:.2f}]"
                            )
                            break
            
            return is_duplicate, duplicate_path
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Duplikatserkennung: {str(e)}")
            return False, None
    
    def _move_file(self, file_path, new_filename, is_duplicate, force=False):
        """
        Verschiebt die Datei in den entsprechenden Ordner (Ausgabe oder Papierkorb).
        
        Basierend darauf, ob die Datei als Duplikat erkannt wurde, wird sie entweder
        in den Ausgabeordner oder in den Papierkorb verschoben, wobei der neue Dateiname
        verwendet wird.
        
        Args:
            file_path (str): Pfad zur Originaldatei
            new_filename (str): Neuer Dateiname für die Datei
            is_duplicate (bool): Ob die Datei ein Duplikat ist
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if is_duplicate:
                # Datei in den Papierkorb verschieben
                target_dir = self.config.get('paths', {}).get('trash_dir', '')
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                # Zielpath mit "DUPLICATE_" Präfix
                duplicate_filename = "DUPLICATE_" + new_filename
                target_path = os.path.join(target_dir, duplicate_filename)
                
                # Datei verschieben
                self.file_operations.move_to_output(file_path, target_path, force)
                self.logger.info(f"Duplikat in Papierkorb verschoben: {duplicate_filename}")
            else:
                # Datei in den Ausgabeordner verschieben
                target_dir = self.config.get('paths', {}).get('output_dir', '')
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                target_path = os.path.join(target_dir, new_filename)
                
                # Datei verschieben
                self.file_operations.move_to_output(file_path, target_path, force)
                self.logger.info(f"Datei erfolgreich verarbeitet: {new_filename}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei: {str(e)}")
            return False