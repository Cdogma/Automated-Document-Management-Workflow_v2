"""
DocumentProcessor für MaehrDocs
Hauptklasse zur Verarbeitung von Dokumenten
"""

import os
import logging
import time

# Lokale Module importieren
from .text_extractor import TextExtractor
from .openai_integration import OpenAIIntegration
from .file_operations import FileOperations
from .filename_generator import FilenameGenerator
from .duplicate_detector import DuplicateDetector

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
        Prüft, ob ein ähnliches Dokument bereits existiert
        
        Args:
            text (str): Text des zu prüfenden Dokuments
            file_path (str): Pfad zur PDF-Datei
            
        Returns:
            tuple: (is_duplicate, duplicate_path)
        """
        # Hole alle PDFs aus dem Ausgabeordner
        output_files = self.file_operations.get_output_files(extension='.pdf')
        
        for existing_file_path in output_files:
            # Prüfe, ob es die gleiche Datei ist
            if os.path.samefile(file_path, existing_file_path):
                continue
            
            # Extrahiere Text aus der bestehenden Datei
            existing_text = self.text_extractor.extract_text_from_pdf(existing_file_path)
            
            if existing_text:
                # Berechne Ähnlichkeit
                similarity = self.duplicate_detector.calculate_similarity(text, existing_text)
                similarity_threshold = self.config.get('document_processing', {}).get('similarity_threshold', 0.85)
                
                if similarity >= similarity_threshold:
                    self.logger.info(
                        f"DUPLICATE DETECTED: [Original: {existing_file_path}] "
                        f"[Duplicate: {file_path}] [Similarity: {similarity:.2f}]"
                    )
                    return True, existing_file_path
        
        return False, None
    
    def _move_file(self, file_path, new_filename, is_duplicate, force=False):
        """
        Verschiebt die Datei basierend auf dem Analyseergebnis
        
        Args:
            file_path (str): Pfad zur PDF-Datei
            new_filename (str): Neuer Dateiname
            is_duplicate (bool): Ob die Datei ein Duplikat ist
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if is_duplicate and not (force or self.force):
                # Verschiebe die Datei in den Papierkorb
                new_path = self.file_operations.move_to_trash(file_path)
                return new_path is not None
            else:
                # Verschiebe die Datei in den Ausgabeordner mit neuem Namen
                new_path = self.file_operations.move_to_output(file_path, new_filename, force or self.force)
                return new_path is not None
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei: {str(e)}")
            return False
    
    def process_all_documents(self, dry_run=False, force=False):
        """
        Verarbeitet alle PDF-Dokumente im Eingangsordner
        
        Args:
            dry_run (bool): Wenn True, werden keine Dateioperationen durchgeführt
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            list: Liste der Verarbeitungsergebnisse
        """
        # Hole alle PDFs aus dem Eingangsordner
        input_files = self.file_operations.get_input_files(extension='.pdf')
        
        if not input_files:
            self.logger.info("Keine PDF-Dateien im Eingangsordner gefunden.")
            return []
        
        # Anzahl der Dateien
        num_files = len(input_files)
        self.logger.info(f"{num_files} PDF-Dateien im Eingangsordner gefunden.")
        
        # Ergebnisliste
        results = []
        
        # Zeitmessung
        start_time = time.time()
        
        # Verarbeite jede Datei
        for i, file_path in enumerate(input_files):
            self.logger.info(f"Verarbeite Datei {i+1}/{num_files}: {os.path.basename(file_path)}")
            
            # Verarbeite die Datei
            result = self.process_document(file_path, dry_run, force)
            
            if result:
                results.append(result)
                self.logger.info(f"Dokument verarbeitet: {os.path.basename(file_path)} → {result['new_filename']}")
            else:
                self.logger.warning(f"Fehler bei der Verarbeitung von {os.path.basename(file_path)}")
        
        # Gesamtzeit
        total_time = time.time() - start_time
        avg_time = total_time / num_files if num_files > 0 else 0
        
        # Zusammenfassung
        self.logger.info(f"Verarbeitung abgeschlossen: {len(results)}/{num_files} Dokumente erfolgreich verarbeitet.")
        self.logger.info(f"Gesamtzeit: {total_time:.2f} Sekunden, Durchschnitt: {avg_time:.2f} Sekunden pro Dokument.")
        
        return results