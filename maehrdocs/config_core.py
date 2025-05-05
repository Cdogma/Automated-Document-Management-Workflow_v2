"""
Kern-Konfigurationsmanagement für MaehrDocs
Enthält die ConfigManager-Klasse zum Laden und Speichern der Anwendungskonfiguration.

Implementiert das Singleton-Pattern für konsistenten Zugriff auf die Konfiguration
im gesamten System und verhindert Dateninkonsistenzen durch mehrfache Instanzen.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Vorwärtsimport, um zirkuläre Abhängigkeiten zu vermeiden
from .config_defaults import create_default_config, ensure_directories_exist

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
                self._config = create_default_config()
                self.save_config(self._config)
            else:
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file)
                    self.logger.info(f"Konfiguration aus {self.config_path} geladen.")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            self.logger.info("Verwende Standardkonfiguration.")
            self._config = create_default_config()
    
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