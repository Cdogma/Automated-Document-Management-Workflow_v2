"""
Hilfsfunktionen für die Konfigurationsverwaltung
Enthält Funktionen zum Aktualisieren und Abfragen von Konfigurationswerten.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def update_config(config_manager, updates: Dict[str, Any], section: str = None) -> bool:
    """
    Aktualisiert die Konfiguration mit den angegebenen Werten
    
    Args:
        config_manager: Die ConfigManager-Instanz
        updates: Dictionary mit den zu aktualisierenden Werten
        section: Optional, Konfigurationsabschnitt (z.B. 'paths')
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        config = config_manager.config
        if section:
            if section not in config:
                config[section] = {}
            config[section].update(updates)
        else:
            config.update(updates)
            
        return config_manager.save_config(config)
        
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Konfiguration: {str(e)}")
        return False

def reset_section(config_manager, section: str) -> bool:
    """
    Setzt einen Konfigurationsabschnitt auf die Standardwerte zurück
    
    Args:
        config_manager: Die ConfigManager-Instanz
        section: Name des Konfigurationsabschnitts
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        from .config_defaults import create_default_config
        
        default_config = create_default_config()
        if section in default_config:
            config_manager.config[section] = default_config[section]
            return config_manager.save_config(config_manager.config)
        return False
        
    except Exception as e:
        logger.error(f"Fehler beim Zurücksetzen des Abschnitts {section}: {str(e)}")
        return False

def reset_config(config_manager) -> bool:
    """
    Setzt die gesamte Konfiguration auf die Standardwerte zurück
    
    Args:
        config_manager: Die ConfigManager-Instanz
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        from .config_defaults import create_default_config
        
        config = create_default_config()
        return config_manager.save_config(config)
        
    except Exception as e:
        logger.error(f"Fehler beim Zurücksetzen der Konfiguration: {str(e)}")
        return False

def get_value(config_manager, key_path, default=None):
    """
    Holt einen Wert aus der Konfiguration mit Punktnotation (z.B. 'paths.input_dir')
    
    Args:
        config_manager: Die ConfigManager-Instanz
        key_path: Pfad zum Konfigurationsschlüssel mit Punkten getrennt
        default: Standardwert, falls der Schlüssel nicht existiert
        
    Returns:
        Der Wert aus der Konfiguration oder der Standardwert
    """
    try:
        keys = key_path.split('.')
        value = config_manager.config
        
        for key in keys:
            if key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    except Exception:
        return default