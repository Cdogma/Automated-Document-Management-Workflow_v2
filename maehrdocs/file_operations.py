"""
Dateioperationen für MaehrDocs
Verwaltet alle Dateioperationen wie Verschieben, Kopieren und Löschen von Dateien
"""

import os
import shutil
import logging

class FileOperations:
    """
    Klasse zur Verwaltung von Dateioperationen
    """
    
    def __init__(self, config):
        """
        Initialisiert die Dateioperationen
        
        Args:
            config (dict): Konfigurationsdaten mit Pfadeinstellungen
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Stelle sicher, dass alle erforderlichen Verzeichnisse existieren
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """
        Stellt sicher, dass alle erforderlichen Verzeichnisse existieren
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
        Verschiebt eine Datei in den Ausgabeordner mit neuem Namen
        
        Args:
            file_path (str): Pfad zur Quelldatei
            new_filename (str): Neuer Dateiname
            force (bool): Wenn True, werden vorhandene Dateien überschrieben
            
        Returns:
            str: Pfad zur neuen Datei oder None bei Fehler
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Quelldatei existiert nicht: {file_path}")
                return None
            
            # Zielverzeichnis
            output_dir = self.config['paths']['output_dir']
            
            # Zielverzeichnis erstellen, falls es nicht existiert
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Zielverzeichnis
            dest_path = os.path.join(output_dir, new_filename)
            
            # Prüfe, ob die Zieldatei bereits existiert
            if os.path.exists(dest_path) and not force:
                # Füge eine Nummer hinzu, um Konflikte zu vermeiden
                base, ext = os.path.splitext(new_filename)
                counter = 1
                while os.path.exists(os.path.join(output_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                dest_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
            
            # Datei verschieben
            self.logger.info(f"Verschiebe Datei nach: {dest_path}")
            shutil.move(file_path, dest_path)
            
            return dest_path
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei nach {dest_path}: {str(e)}")
            return None
    
    def move_to_trash(self, file_path):
        """
        Verschiebt eine Datei in den Papierkorb
        
        Args:
            file_path (str): Pfad zur Quelldatei
            
        Returns:
            str: Pfad zur neuen Datei oder None bei Fehler
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Quelldatei existiert nicht: {file_path}")
                return None
            
            # Zielverzeichnis
            trash_dir = self.config['paths']['trash_dir']
            
            # Zielverzeichnis erstellen, falls es nicht existiert
            if not os.path.exists(trash_dir):
                os.makedirs(trash_dir)
            
            # Zielverzeichnis
            dest_path = os.path.join(trash_dir, os.path.basename(file_path))
            
            # Prüfe, ob die Zieldatei bereits existiert
            if os.path.exists(dest_path):
                # Füge eine Nummer hinzu, um Konflikte zu vermeiden
                base, ext = os.path.splitext(os.path.basename(file_path))
                counter = 1
                while os.path.exists(os.path.join(trash_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                dest_path = os.path.join(trash_dir, f"{base}_{counter}{ext}")
            
            # Datei verschieben
            self.logger.info(f"Verschiebe Datei in den Papierkorb: {dest_path}")
            shutil.move(file_path, dest_path)
            
            return dest_path
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei in den Papierkorb: {str(e)}")
            return None
    
    def get_input_files(self, extension='.pdf'):
        """
        Gibt eine Liste aller Dateien mit der angegebenen Endung im Eingangsordner zurück
        
        Args:
            extension (str): Dateiendung (Standardwert: '.pdf')
            
        Returns:
            list: Liste der Dateipfade
        """
        try:
            input_dir = self.config['paths']['input_dir']
            
            if not os.path.exists(input_dir):
                self.logger.warning(f"Eingangsordner existiert nicht: {input_dir}")
                return []
            
            return [
                os.path.join(input_dir, filename)
                for filename in os.listdir(input_dir)
                if filename.lower().endswith(extension.lower())
            ]
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Dateien aus dem Eingangsordner: {str(e)}")
            return []
    
    def get_output_files(self, extension='.pdf'):
        """
        Gibt eine Liste aller Dateien mit der angegebenen Endung im Ausgabeordner zurück
        
        Args:
            extension (str): Dateiendung (Standardwert: '.pdf')
            
        Returns:
            list: Liste der Dateipfade
        """
        try:
            output_dir = self.config['paths']['output_dir']
            
            if not os.path.exists(output_dir):
                self.logger.warning(f"Ausgabeordner existiert nicht: {output_dir}")
                return []
            
            return [
                os.path.join(output_dir, filename)
                for filename in os.listdir(output_dir)
                if filename.lower().endswith(extension.lower())
            ]
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Dateien aus dem Ausgabeordner: {str(e)}")
            return []
    
    def create_backup(self, file_path, backup_dir=None):
        """
        Erstellt eine Sicherungskopie einer Datei
        
        Args:
            file_path (str): Pfad zur Quelldatei
            backup_dir (str): Verzeichnis für die Sicherungskopie (optional)
            
        Returns:
            str: Pfad zur Sicherungskopie oder None bei Fehler
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Quelldatei existiert nicht: {file_path}")
                return None
            
            # Standardverzeichnis für Sicherungskopien
            if backup_dir is None:
                backup_dir = os.path.join(os.path.dirname(file_path), "backup")
            
            # Backup-Verzeichnis erstellen, falls es nicht existiert
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Zieldatei
            base_name = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, base_name)
            
            # Prüfe, ob die Zieldatei bereits existiert
            if os.path.exists(backup_path):
                # Füge eine Nummer hinzu, um Konflikte zu vermeiden
                base, ext = os.path.splitext(base_name)
                counter = 1
                while os.path.exists(os.path.join(backup_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                backup_path = os.path.join(backup_dir, f"{base}_{counter}{ext}")
            
            # Datei kopieren
            self.logger.info(f"Erstelle Sicherungskopie: {backup_path}")
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Sicherungskopie: {str(e)}")
            return None