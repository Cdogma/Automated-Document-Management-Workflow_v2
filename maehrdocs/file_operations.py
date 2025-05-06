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

class FileOperations:
    """
    Klasse zur Verwaltung von Dateioperationen im Dokumentenmanagementsystem.
    
    Diese Klasse ist verantwortlich für:
    - Verwalten der Ordnerstruktur (Eingang, Ausgang, Papierkorb)
    - Sichere Verschiebung von Dateien zwischen Ordnern
    - Behandlung von Dateinamenskonflikten
    - Erstellung von Sicherungskopien
    - Bereitstellung von Dateilisteninformationen
    
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
        
        Erstellt die Eingangs-, Ausgangs- und Papierkorbverzeichnisse,
        falls sie noch nicht vorhanden sind, um Dateisystemfehler bei
        der Dokumentenverarbeitung zu vermeiden.
        """
        try:
            for dir_path in [
                self.config['paths']['input_dir'],
                self.config['paths']['output_dir'],
                self.config['paths']['trash_dir']
            ]:
                if not os.path.exists(dir_path):
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
            
            # Original löschen, wenn aktiviert
            keep_original = self.config.get('advanced', {}).get('keep_original_files', False)
            if not keep_original:
                os.remove(file_path)
                self.logger.debug(f"Quelldatei gelöscht: {file_path}")
            
            self.logger.info(f"Datei erfolgreich verschoben: {file_path} -> {new_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei {file_path} zu {new_filename}: {str(e)}")
            return False