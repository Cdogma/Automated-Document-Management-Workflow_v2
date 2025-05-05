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

from .config_core import ConfigManager
from .config_defaults import create_default_config, ensure_directories_exist
from .config_utils import (
    update_config,
    reset_section,
    reset_config,
    get_value
)

# Erweitere die ConfigManager-Klasse um die Hilfsfunktionen
class ConfigManagerExtended(ConfigManager):
    """
    Erweiterte Version der ConfigManager-Klasse mit zusätzlichen Hilfsfunktionen
    """
    
    def update_config(self, updates, section=None):
        """
        Aktualisiert die Konfiguration mit den angegebenen Werten
        
        Args:
            updates: Dictionary mit den zu aktualisierenden Werten
            section: Optional, Konfigurationsabschnitt (z.B. 'paths')
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        return update_config(self, updates, section)
    
    def reset_section(self, section):
        """
        Setzt einen Konfigurationsabschnitt auf die Standardwerte zurück
        
        Args:
            section: Name des Konfigurationsabschnitts
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        return reset_section(self, section)
    
    def reset_config(self):
        """
        Setzt die gesamte Konfiguration auf die Standardwerte zurück
        
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        return reset_config(self)
    
    def get_value(self, key_path, default=None):
        """
        Holt einen Wert aus der Konfiguration mit Punktnotation (z.B. 'paths.input_dir')
        
        Args:
            key_path: Pfad zum Konfigurationsschlüssel mit Punkten getrennt
            default: Standardwert, falls der Schlüssel nicht existiert
            
        Returns:
            Der Wert aus der Konfiguration oder der Standardwert
        """
        return get_value(self, key_path, default)

# Override des ursprünglichen ConfigManager mit der erweiterten Version
ConfigManager = ConfigManagerExtended

__all__ = [
    'ConfigManager',
    'create_default_config',
    'ensure_directories_exist',
    'update_config',
    'reset_section',
    'reset_config',
    'get_value'
]