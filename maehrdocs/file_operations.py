"""
Dateioperationen für MaehrDocs
Verwaltet alle Dateioperationen wie Verschieben, Kopieren, Umbenennen und Löschen
von Dokumenten im Rahmen des Dokumentenmanagementsystems.

Dieses Modul bietet eine zentrale Schnittstelle für alle dateibezogenen Operationen
und stellt sicher, dass Dokumente konsistent und fehlerfrei zwischen den verschiedenen
Systemordnern verschoben werden können, unter Berücksichtigung von Dateinamenskonflikten
und anderen potenziellen Problemen.
"""

import os
import shutil
import logging
from datetime import datetime

class FileOperations:
    """
    Klasse zur Verwaltung von Dateioperationen im Dokumentenmanagementsystem.
    
    Diese Klasse ist verantwortlich für:
    - Verwalten der Ordnerstruktur (Eingang, Ausgang, Papierkorb, Verarbeitet)
    - Sichere Verschiebung von Dateien zwischen Ordnern
    - Behandlung von Dateinamenskonflikten
    - Erstellung von Sicherungskopien
    - Bereitstellung von Dateilisteninformationen
    - Markierung verarbeiteter Dateien und Verschiebung in processed_dir
    
    Sie bildet die Grundlage für die sicheren Dateioperationen im
    gesamten Dokumentenmanagementsystem.
    """
    
    def __init__(self, config):
        """
        Initialisiert die Dateioperationen mit der Anwendungskonfiguration.
        
        Richtet Logging ein und stellt sicher, dass alle erforderlichen
        Verzeichnisse für die Dokumentenverarbeitung existieren.
        
        Args:
            config (dict): Konfigurationsdaten mit Pfadeinstellungen für die Ordner
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Stelle sicher, dass alle erforderlichen Verzeichnisse existieren
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """
        Stellt sicher, dass alle erforderlichen Verzeichnisse existieren.
        
        Erstellt die Eingangs-, Ausgangs-, Papierkorb- und Verarbeitungsverzeichnisse,
        falls sie noch nicht vorhanden sind, um Dateisystemfehler bei
        der Dokumentenverarbeitung zu vermeiden.
        """
        try:
            for dir_path in [
                self.config['paths']['input_dir'],
                self.config['paths']['output_dir'],
                self.config['paths']['trash_dir'],
                self.config['paths'].get('log_dir', ''),
                self.config['paths'].get('processed_dir', '')
            ]:
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    self.logger.info(f"Verzeichnis erstellt: {dir_path}")
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Verzeichnisse: {str(e)}")
    
    def move_to_output(self, file_path, new_filename, force=False):
        """
        Verschiebt eine Datei in den Ausgabeordner mit neuem Namen.
        
        Implementiert intelligente Konfliktbehandlung, indem bei bereits
        existierenden Dateien automatisch ein Suffix hinzugefügt wird.
        Bei aktivierter force-Option werden vorhandene Dateien überschrieben.
        
        Args:
            file_path (str): Pfad zur Originaldatei
            new_filename (str): Neuer vollständiger Zieldateiname (mit Pfad)
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Prüfen, ob die Quelldatei existiert
            if not os.path.exists(file_path):
                self.logger.error(f"Quelldatei existiert nicht: {file_path}")
                return False
            
            # Wenn die Zieldatei bereits existiert
            if os.path.exists(new_filename):
                if force:
                    # Bei force=True vorhandene Datei überschreiben
                    self.logger.info(f"Überschreibe vorhandene Datei: {new_filename}")
                    os.remove(new_filename)
                else:
                    # Sonst ein Suffix hinzufügen
                    base, ext = os.path.splitext(new_filename)
                    counter = 1
                    while os.path.exists(f"{base}_{counter}{ext}"):
                        counter += 1
                    new_filename = f"{base}_{counter}{ext}"
                    self.logger.info(f"Datei existiert bereits, verwende alternativen Namen: {new_filename}")
            
            # Datei kopieren
            shutil.copy2(file_path, new_filename)
            
            # Original in processed_dir verschieben oder löschen, je nach Konfiguration
            self.mark_as_processed(file_path)
            
            self.logger.info(f"Datei erfolgreich verschoben: {file_path} -> {new_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei {file_path} zu {new_filename}: {str(e)}")
            return False
    
    def mark_as_processed(self, file_path):
        """
        Markiert eine Datei als verarbeitet und verschiebt sie in den processed_dir,
        sofern in der Konfiguration aktiviert.
        
        Wenn mark_processed_files in der Konfiguration aktiviert ist, wird die Originaldatei
        mit einem Präfix versehen und in den processed_dir verschoben. Andernfalls wird
        die Originaldatei gelöscht, wenn keep_original_files auf False gesetzt ist.
        
        Args:
            file_path (str): Pfad zur Originaldatei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            # Neues Verhalten: Markieren und Verschieben der verarbeiteten Dateien
            mark_processed = self.config.get('advanced', {}).get('mark_processed_files', False)
            keep_original = self.config.get('advanced', {}).get('keep_original_files', False)
            
            # Wenn Markierung aktiviert ist und processed_dir konfiguriert ist
            if mark_processed and 'processed_dir' in self.config.get('paths', {}):
                processed_dir = self.config['paths']['processed_dir']
                
                # Sicherstellen, dass das Verzeichnis existiert
                if not os.path.exists(processed_dir):
                    os.makedirs(processed_dir)
                
                # Präfix für verarbeitete Dateien erstellen
                date_str = datetime.now().strftime("%Y-%m-%d")
                prefix = self.config.get('filename_rules', {}).get('processed_file_prefix', "PROCESSED_{date}_")
                prefix = prefix.replace("{date}", date_str)
                
                # Neuen Dateinamen erstellen
                filename = os.path.basename(file_path)
                processed_filename = prefix + filename
                processed_path = os.path.join(processed_dir, processed_filename)
                
                # Bei Namenskonflikt ein Suffix hinzufügen
                if os.path.exists(processed_path):
                    base, ext = os.path.splitext(processed_path)
                    counter = 1
                    while os.path.exists(f"{base}_{counter}{ext}"):
                        counter += 1
                    processed_path = f"{base}_{counter}{ext}"
                
                # Datei in processed_dir verschieben
                shutil.move(file_path, processed_path)
                self.logger.info(f"Datei als verarbeitet markiert und verschoben: {file_path} -> {processed_path}")
                return True
                
            # Altes Verhalten: Datei löschen, wenn keep_original_files auf False gesetzt ist
            elif not keep_original:
                os.remove(file_path)
                self.logger.debug(f"Quelldatei gelöscht: {file_path}")
                return True
                
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Markieren der Datei als verarbeitet: {file_path}, Fehler: {str(e)}")
            return False
    
    def check_for_duplicates(self, file_path, check_in_output=True, check_in_processed=True):
        """
        Prüft, ob eine Datei ein Duplikat (identischer Dateiname) in den Zielordnern hat.
        
        Diese Methode prüft, ob eine Datei mit demselben Namen bereits in den
        konfigurierten Ausgabe- und Verarbeitungsordnern existiert, um Konflikte
        frühzeitig zu erkennen. Die vollständige Duplikaterkennung erfolgt separat
        über den DuplicateDetector.
        
        Args:
            file_path (str): Pfad zur zu prüfenden Datei
            check_in_output (bool): Prüfung im Ausgabeordner durchführen
            check_in_processed (bool): Prüfung im Verarbeitungsordner durchführen
            
        Returns:
            tuple: (bool, str) - (Ist ein Duplikat, Pfad des Duplikats)
        """
        filename = os.path.basename(file_path)
        
        # Prüfung im Ausgabeordner
        if check_in_output and 'output_dir' in self.config.get('paths', {}):
            output_dir = self.config['paths']['output_dir']
            output_path = os.path.join(output_dir, filename)
            
            if os.path.exists(output_path):
                return True, output_path
        
        # Prüfung im Verarbeitungsordner
        if check_in_processed and 'processed_dir' in self.config.get('paths', {}):
            processed_dir = self.config['paths']['processed_dir']
            
            # Für den Verarbeitungsordner müssen wir nach Dateien suchen, die mit dem Basisnamen enden
            # da sie mit einem Präfix versehen wurden
            for processed_file in os.listdir(processed_dir):
                # Wir prüfen, ob der Dateiname mit dem Originalnamen endet (berücksichtigt Präfix)
                if processed_file.endswith(filename):
                    processed_path = os.path.join(processed_dir, processed_file)
                    return True, processed_path
        
        return False, None