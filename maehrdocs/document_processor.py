"""
DocumentProcessor für MaehrDocs
Hauptklasse zur Verarbeitung von Dokumenten

Diese Klasse koordiniert den gesamten Dokumentenverarbeitungsprozess:
- Text aus PDF-Dokumenten extrahieren
- KI-basierte Analyse und Informationsextraktion
- Duplikaterkennung
- Generierung neuer Dateinamen
- Verschieben und Archivieren von Dokumenten
- Excel-Integration
"""

import os
import logging
import time

from maehrdocs.text_extractor import TextExtractor
from maehrdocs.openai_integration import OpenAIIntegration
from maehrdocs.file_operations import FileOperations
from maehrdocs.filename_generator import FilenameGenerator
from maehrdocs.duplicate_detector import DuplicateDetector
from maehrdocs.duplicate_reporting import generate_duplicate_report
from maehrdocs.document_archiver import archive_business_document
from maehrdocs.excel_core import ExcelWriter

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
                moved_file_path = self._move_file(file_path, new_filename, is_duplicate, force, duplicate_path)
                
                # Dokument zur Excel-Tabelle hinzufügen, wenn nicht als Duplikat erkannt
                if not is_duplicate and moved_file_path:
                    self._add_to_excel(doc_info, moved_file_path)
            else:
                self.logger.info(f"[SIMULATION] Würde Datei verschieben: {file_path} -> {new_filename}")
                if is_duplicate:
                    self.logger.info(f"[SIMULATION] Dokument ist ein Duplikat von: {duplicate_path}")
                else:
                    self.logger.info(f"[SIMULATION] Quelldatei würde als verarbeitet markiert werden")
                    self.logger.info(f"[SIMULATION] Dokument würde zur Excel-Tabelle hinzugefügt werden")
            
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
                        if os.path.exists(file_path) and os.path.samefile(file_path, compare_path):
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
                            
                            # Spezielle Nachricht für Duplikaterkennung mit speziellem Präfix
                            message = f"DUPLIKAT_ERKANNT|{filename}|{os.path.basename(file_path)}|{similarity:.2f}"
                            print(message)  # Diese Zeile ist wichtig für die Erkennung im Stdout
                            self.logger.info(message)
                            
                            break
            
            return is_duplicate, duplicate_path
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Duplikatserkennung: {str(e)}")
            return False, None
    
    def _move_file(self, file_path, new_filename, is_duplicate, force=False, duplicate_path=None):
        """
        Verschiebt die Datei in den entsprechenden Ordner (Ausgabe oder Papierkorb).
        
        Args:
            file_path (str): Pfad zur Originaldatei
            new_filename (str): Neuer Dateiname für die Datei
            is_duplicate (bool): Ob die Datei ein Duplikat ist
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            duplicate_path (str): Pfad zum Original-Duplikat, falls vorhanden
            
        Returns:
            str: Pfad zur verschobenen Datei oder None bei Fehler
        """
        try:
            target_path = None
            
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
                
                # Wenn ein Duplikatbericht generiert werden soll
                if self.config.get('duplicate_detection', {}).get('generate_report', False) and duplicate_path:
                    generate_duplicate_report(self.config, file_path, duplicate_path, new_filename, self.logger)
            else:
                # Datei in den Ausgabeordner verschieben
                target_dir = self.config.get('paths', {}).get('output_dir', '')
                
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                target_path = os.path.join(target_dir, new_filename)
                
                # Datei verschieben
                self.file_operations.move_to_output(file_path, target_path, force)
                self.logger.info(f"Datei erfolgreich verarbeitet: {new_filename}")
            
            return target_path
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei: {str(e)}")
            return None
    
    def _add_to_excel(self, doc_info, file_path):
        """
        Fügt ein verarbeitetes Dokument zur Excel-Tabelle hinzu.
        
        Args:
            doc_info (dict): Extrahierte Dokumenteninformationen
            file_path (str): Pfad zur verarbeiteten PDF-Datei (für den Hyperlink)
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # ExcelWriter initialisieren
            excel_writer = ExcelWriter(self.config)
            
            # Dokument zur Excel-Tabelle hinzufügen
            success = excel_writer.add_document(doc_info, file_path)
            
            if success:
                self.logger.info(f"Dokument zur Excel-Tabelle hinzugefügt: {os.path.basename(file_path)}")
            else:
                self.logger.warning(f"Fehler beim Hinzufügen des Dokuments zur Excel-Tabelle: {os.path.basename(file_path)}")
                
            # Wenn das Dokument als Business oder Bar klassifiziert ist, speichere es auch im Business-Ordner
            art = doc_info.get('art', '').lower()
            if art in ['business', 'bar'] and 'datum' in doc_info:
                archive_business_document(self.config, file_path, doc_info, self.logger)
            
            return success
        
        except ImportError:
            self.logger.warning("ExcelWriter nicht verfügbar. Excel-Integration ist deaktiviert.")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Dokuments zur Excel-Tabelle: {str(e)}")
            return False