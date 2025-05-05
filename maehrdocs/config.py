"""
Konfigurationsverwaltung für MaehrDocs
Enthält die ConfigManager-Klasse zum Laden, Speichern und Verwalten der Anwendungskonfiguration.

Dieses Modul bildet das Herzstück für alle konfigurationsbezogenen Funktionen und
gewährleistet eine konsistente, persistente Speicherung von Benutzereinstellungen.
Es unterstützt das Erstellen von Standardkonfigurationen und das sichere Speichern
und Laden von Konfigurationsdaten im YAML-Format.

Die Implementierung als Singleton-Pattern stellt sicher, dass im gesamten System
nur eine Instanz der Konfiguration existiert, um Dateninkonsistenzen zu vermeiden
und den Zugriff auf Konfigurationsdaten zu vereinheitlichen.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Verwaltet die Konfiguration des MaehrDocs-Systems als Singleton
    
    Stellt sicher, dass im gesamten System nur eine Instanz der
    Konfiguration existiert, um Inkonsistenzen zu vermeiden.
    Bietet Methoden zum Laden, Speichern und Zurücksetzen der Konfiguration.
    """
    
    # Singleton-Instanz
    _instance: Optional['ConfigManager'] = None
    
    # Klassenattribut für den Pfad zur Konfigurationsdatei
    DEFAULT_CONFIG_PATH = "autodocs_config.yaml"
    
    def __new__(cls, config_path=None):
        """
        Erstellt eine neue Instanz oder gibt die bestehende Singleton-Instanz zurück
        
        Args:
            config_path: Pfad zur Konfigurationsdatei (optional)
            
        Returns:
            ConfigManager: Die Singleton-Instanz
        """
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path=None):
        """
        Initialisiert den ConfigManager
        
        Args:
            config_path: Pfad zur Konfigurationsdatei (optional)
        """
        # Vermeidet mehrfache Initialisierung des Singletons
        if self._initialized:
            return
            
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.logger = logging.getLogger(__name__)
        self._config = None  # Lazy Loading - wird erst bei Bedarf geladen
        self._initialized = True
        
        self.logger.debug(f"ConfigManager initialisiert mit Pfad: {self.config_path}")
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        Property-Getter für die Konfiguration mit Lazy Loading
        
        Returns:
            dict: Die aktuelle Konfiguration
        """
        if self._config is None:
            self._load_config()
        return self._config
    
    def get_config(self) -> Dict[str, Any]:
        """
        Gibt die aktuelle Konfiguration zurück
        
        Returns:
            dict: Die aktuelle Konfiguration
        """
        return self.config
    
    def _load_config(self) -> None:
        """
        Lädt die Konfiguration aus der YAML-Datei (intern)
        """
        try:
            if not os.path.exists(self.config_path):
                self.logger.info(f"Konfigurationsdatei {self.config_path} nicht gefunden. Erstelle Standardkonfiguration.")
                self._config = self.create_default_config()
                self.save_config(self._config)
            else:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file)
                    self.logger.info(f"Konfiguration aus {self.config_path} geladen.")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            self.logger.info("Verwende Standardkonfiguration.")
            self._config = self.create_default_config()
    
    def reload_config(self) -> Dict[str, Any]:
        """
        Lädt die Konfiguration neu und gibt sie zurück
        
        Nützlich, wenn die Konfigurationsdatei extern geändert wurde
        und die Änderungen übernommen werden sollen.
        
        Returns:
            dict: Die neu geladene Konfiguration
        """
        self._config = None  # Zurücksetzen, damit beim nächsten Zugriff neu geladen wird
        return self.config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Speichert die Konfiguration in die YAML-Datei
        
        Args:
            config: Die zu speichernde Konfiguration
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                self.logger.info(f"Konfiguration in {self.config_path} gespeichert.")
            
            # Aktualisiere die interne Konfiguration
            self._config = config
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")
            return False
    
    def update_config(self, updates: Dict[str, Any], section: str = None) -> bool:
        """
        Aktualisiert die Konfiguration mit den angegebenen Werten
        
        Args:
            updates: Dictionary mit den zu aktualisierenden Werten
            section: Optional, Konfigurationsabschnitt (z.B. 'paths')
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            if section:
                if section not in self.config:
                    self.config[section] = {}
                self.config[section].update(updates)
            else:
                self.config.update(updates)
                
            return self.save_config(self.config)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Konfiguration: {str(e)}")
            return False
    
    def reset_section(self, section: str) -> bool:
        """
        Setzt einen Konfigurationsabschnitt auf die Standardwerte zurück
        
        Args:
            section: Name des Konfigurationsabschnitts
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            default_config = self.create_default_config()
            if section in default_config:
                self.config[section] = default_config[section]
                return self.save_config(self.config)
            return False
            
        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksetzen des Abschnitts {section}: {str(e)}")
            return False
    
    def reset_config(self) -> bool:
        """
        Setzt die gesamte Konfiguration auf die Standardwerte zurück
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            self._config = self.create_default_config()
            return self.save_config(self._config)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksetzen der Konfiguration: {str(e)}")
            return False
    
    def create_default_config(self) -> Dict[str, Any]:
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
                
    def get_value(self, key_path, default=None):
        """
        Holt einen Wert aus der Konfiguration mit Punktnotation (z.B. 'paths.input_dir')
        
        Args:
            key_path: Pfad zum Konfigurationsschlüssel mit Punkten getrennt
            default: Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            Der Wert aus der Konfiguration oder der Standardwert
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if key in value:
                    value = value[key]
                else:
                    return default
                    
            return value
            
        except Exception:
            return default