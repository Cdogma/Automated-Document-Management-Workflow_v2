import os
import yaml
import logging

class ConfigManager:
    def __init__(self, config_path="autodocs_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
            else:
                return self.create_default_config()
        except Exception as e:
            logging.error(f"Fehler beim Laden der Konfiguration: {e}")
            return self.create_default_config()
    
    def create_default_config(self):
        """Erstellt eine Standard-Konfiguration"""
        default_config = {
            "paths": {
                "input_dir": os.path.join(os.path.expanduser("~"), "OneDrive", "09_AutoDocs", "01_InboxDocs"),
                "output_dir": os.path.join(os.path.expanduser("~"), "OneDrive", "09_AutoDocs", "02_FinalDocs"),
                "trash_dir": os.path.join(os.path.expanduser("~"), "OneDrive", "09_AutoDocs", "03_TrashDocs")
            },
            "openai": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_retries": 3
            },
            "document_processing": {
                "max_file_size_mb": 20,
                "similarity_threshold": 0.85
            },
            "valid_doc_types": [
                "rechnung", "vertrag", "brief", "meldung", 
                "bescheid", "dokument", "antrag"
            ]
        }
        
        # Speichern der Standard-Konfiguration
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """Speichert die Konfiguration in die YAML-Datei"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def get_config(self):
        """Gibt die aktuelle Konfiguration zurück"""
        return self.config
    
    def update_config(self, new_config):
        """Aktualisiert die Konfiguration"""
        self.config = new_config
        return self.save_config()