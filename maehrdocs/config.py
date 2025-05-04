"""
Konfigurationsverwaltung für MaehrDocs
Enthält die ConfigManager-Klasse zum Laden und Speichern der Konfiguration
"""

import os
import yaml
import logging
from pathlib import Path

class ConfigManager:
    """
    Verwaltet die Konfiguration des MaehrDocs-Systems
    """
    
    def __init__(self, config_path="autodocs_config.yaml"):
        """
        Initialisiert den ConfigManager
        
        Args:
            config_path: Pfad zur Konfigurationsdatei
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Konfiguration laden oder Standardkonfiguration erstellen
        if not os.path.exists(config_path):
            self.logger.info(f"Konfigurationsdatei {config_path} nicht gefunden. Erstelle Standardkonfiguration.")
            self.config = self.create_default_config()
            self.save_config(self.config)
        else:
            self.config = self.load_config()
    
    def get_config(self):
        """
        Gibt die aktuelle Konfiguration zurück
        
        Returns:
            dict: Die aktuelle Konfiguration
        """
        return self.config
    
    def load_config(self):
        """
        Lädt die Konfiguration aus der YAML-Datei
        
        Returns:
            dict: Die geladene Konfiguration
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self.logger.info(f"Konfiguration aus {self.config_path} geladen.")
                return config
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            self.logger.info("Verwende Standardkonfiguration.")
            return self.create_default_config()
    
    def save_config(self, config):
        """
        Speichert die Konfiguration in die YAML-Datei
        
        Args:
            config: Die zu speichernde Konfiguration
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                self.logger.info(f"Konfiguration in {self.config_path} gespeichert.")
            
            # Aktualisiere die interne Konfiguration
            self.config = config
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")
    
    def create_default_config(self):
        """
        Erstellt eine Standardkonfiguration
        
        Returns:
            dict: Die Standardkonfiguration
        """
        home_dir = str(Path.home())
        base_dir = os.path.join(home_dir, "OneDrive", "09_AutoDocs")
        
        # Stellen Sie sicher, dass die Standardordner existieren
        self._ensure_directories_exist([
            os.path.join(base_dir, "01_InboxDocs"),
            os.path.join(base_dir, "02_FinalDocs"),
            os.path.join(base_dir, "03_TrashDocs")
        ])
        
        # Standardkonfiguration
        return {
            "paths": {
                "input_dir": os.path.join(base_dir, "01_InboxDocs"),
                "output_dir": os.path.join(base_dir, "02_FinalDocs"),
                "trash_dir": os.path.join(base_dir, "03_TrashDocs")
            },
            "openai": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_retries": 3
            },
            "document_processing": {
                "max_file_size_mb": 20,
                "similarity_threshold": 0.85,
                "valid_doc_types": [
                    "rechnung",
                    "vertrag",
                    "brief",
                    "meldung",
                    "bescheid",
                    "dokument",
                    "antrag"
                ]
            },
            "gui": {
                "show_duplicate_popup": True,
                "notify_on_completion": True,
                "enable_sounds": False,
                "notify_on_new_documents": True
            }
        }
    
    def _ensure_directories_exist(self, directory_list):
        """
        Stellt sicher, dass die angegebenen Verzeichnisse existieren
        
        Args:
            directory_list: Liste der zu prüfenden Verzeichnisse
        """
        for directory in directory_list:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    self.logger.info(f"Verzeichnis erstellt: {directory}")
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen von Verzeichnis {directory}: {str(e)}")