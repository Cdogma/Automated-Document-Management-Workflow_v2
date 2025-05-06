"""
Funktionen zur Erstellung von Duplikatberichten für MaehrDocs
Enthält Funktionalität zum Erstellen von Berichten über erkannte Duplikate
in verschiedenen Formaten (Text, JSON, HTML).
"""

import os
import logging
from datetime import datetime

def generate_duplicate_report(config, original_file, duplicate_file, new_filename, logger=None):
    """
    Generiert einen Bericht über erkannte Duplikate.
    
    Erstellt je nach Konfiguration einen Text-, JSON- oder HTML-Bericht
    mit Details zu den erkannten Duplikaten.
    
    Args:
        config (dict): Konfigurationsdaten
        original_file (str): Pfad zur Originaldatei
        duplicate_file (str): Pfad zur Duplikatdatei
        new_filename (str): Neuer Dateiname für die Duplikatdatei
        logger (Logger): Logger-Instanz für Protokollierung (optional)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    if logger is None:
        logger = logging.getLogger(__name__)
        
    try:
        # Konfiguration für Duplikatberichte laden
        report_format = config.get('duplicate_detection', {}).get('report_format', 'text')
        
        # Berichte legen wir im Log-Verzeichnis ab, falls konfiguriert
        log_dir = config.get('paths', {}).get('log_dir', '')
        if not log_dir:
            log_dir = os.path.dirname(os.path.abspath(config.get('paths', {}).get('trash_dir', '')))
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Berichtsname basierend auf Datum und Duplikatdatei
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"duplicate_report_{timestamp}_{os.path.basename(duplicate_file)}"
        
        # Je nach gewünschtem Format den entsprechenden Bericht erstellen
        if report_format == 'html':
            return _create_html_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger)
        elif report_format == 'json':
            return _create_json_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger)
        else:  # Standardmäßig Text
            return _create_text_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger)
            
    except Exception as e:
        if logger:
            logger.error(f"Fehler bei der Erstellung des Duplikatberichts: {str(e)}")
        return False

def _create_html_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger):
    """
    Erstellt einen HTML-Bericht über ein erkanntes Duplikat.
    
    Args:
        log_dir (str): Verzeichnis für den Bericht
        report_name (str): Basisname des Berichts
        original_file (str): Pfad zur Originaldatei
        duplicate_file (str): Pfad zur Duplikatdatei
        new_filename (str): Neuer Dateiname für die Duplikatdatei
        logger (Logger): Logger-Instanz für Protokollierung
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    report_path = os.path.join(log_dir, f"{report_name}.html")
    try:
        # HTML-Bericht erstellen (vereinfachte Version)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><head><title>Duplikatbericht</title></head><body>")
            f.write(f"<h1>Duplikat erkannt</h1>")
            f.write(f"<p><strong>Original:</strong> {original_file}</p>")
            f.write(f"<p><strong>Duplikat:</strong> {duplicate_file}</p>")
            f.write(f"<p><strong>Neuer Name:</strong> {new_filename}</p>")
            f.write(f"<p><strong>Erkennungsdatum:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
            f.write("</body></html>")
        
        logger.info(f"HTML-Duplikatbericht erstellt: {report_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des HTML-Duplikatberichts: {str(e)}")
        return False

def _create_json_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger):
    """
    Erstellt einen JSON-Bericht über ein erkanntes Duplikat.
    
    Args:
        log_dir (str): Verzeichnis für den Bericht
        report_name (str): Basisname des Berichts
        original_file (str): Pfad zur Originaldatei
        duplicate_file (str): Pfad zur Duplikatdatei
        new_filename (str): Neuer Dateiname für die Duplikatdatei
        logger (Logger): Logger-Instanz für Protokollierung
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    report_path = os.path.join(log_dir, f"{report_name}.json")
    try:
        # JSON-Bericht erstellen
        import json
        report_data = {
            "original": original_file,
            "duplicate": duplicate_file,
            "new_filename": new_filename,
            "detection_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4)
        
        logger.info(f"JSON-Duplikatbericht erstellt: {report_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des JSON-Duplikatberichts: {str(e)}")
        return False

def _create_text_report(log_dir, report_name, original_file, duplicate_file, new_filename, logger):
    """
    Erstellt einen Textbericht über ein erkanntes Duplikat.
    
    Args:
        log_dir (str): Verzeichnis für den Bericht
        report_name (str): Basisname des Berichts
        original_file (str): Pfad zur Originaldatei
        duplicate_file (str): Pfad zur Duplikatdatei
        new_filename (str): Neuer Dateiname für die Duplikatdatei
        logger (Logger): Logger-Instanz für Protokollierung
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    report_path = os.path.join(log_dir, f"{report_name}.txt")
    try:
        # Text-Bericht erstellen
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Duplikatbericht\n")
            f.write(f"===============\n\n")
            f.write(f"Original: {original_file}\n")
            f.write(f"Duplikat: {duplicate_file}\n")
            f.write(f"Neuer Name: {new_filename}\n")
            f.write(f"Erkennungsdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info(f"Text-Duplikatbericht erstellt: {report_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Text-Duplikatberichts: {str(e)}")
        return False