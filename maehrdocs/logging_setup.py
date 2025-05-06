"""
Logging-Konfiguration für MaehrDocs
Konfiguriert das Python-Logging-Modul basierend auf den Anwendungseinstellungen.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(config):
    """
    Richtet das Logging basierend auf der Konfiguration ein.
    
    Args:
        config (dict): Konfiguration mit Logging-Einstellungen
    
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    # Einstellungen aus der Konfiguration laden
    log_config = config.get('logging', {})
    log_level_str = log_config.get('level', 'info').upper()
    file_logging = log_config.get('file_logging', True)
    console_logging = log_config.get('console_logging', True)
    max_log_files = log_config.get('max_log_files', 10)
    max_file_size_mb = log_config.get('max_file_size_mb', 5)
    
    # Log-Level bestimmen
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Root-Logger konfigurieren
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Altes Handlers entfernen (falls vorhanden)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Log-Format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Konsolen-Handler hinzufügen, wenn aktiviert
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Datei-Handler hinzufügen, wenn aktiviert
    if file_logging:
        log_dir = config.get('paths', {}).get('log_dir', '')
        
        # Standardpfad, wenn nicht konfiguriert
        if not log_dir:
            log_dir = os.path.join(os.getcwd(), 'logs')
        
        # Sicherstellen, dass das Verzeichnis existiert
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Aktuelles Datum für Dateinamen
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'maehrdocs_{today}.log')
        
        # Rotating File Handler für Log-Rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,  # MB in Bytes umrechnen
            backupCount=max_log_files
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.info("Logging eingerichtet. Protokollebene: %s", log_level_str)
    if file_logging:
        logger.info("Protokolldatei: %s", log_file)
    
    return logger