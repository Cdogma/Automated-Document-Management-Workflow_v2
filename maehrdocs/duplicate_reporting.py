"""
Duplikat-Berichterstattung für MaehrDocs
Hauptmodul zur Erstellung detaillierter Berichte über erkannte Dokumentenduplikate.

Dieses Modul importiert und koordiniert die spezialisierten Berichtsgeneratoren
und stellt eine einheitliche Schnittstelle zur Berichterstellung bereit.
"""

import os
import logging
import datetime
from pathlib import Path

# Importiere die Berichtsgeneratoren
from maehrdocs.report_generators import (
    generate_text_report,
    generate_html_report,
    generate_json_report
)
from maehrdocs.visual_comparison import generate_visual_comparison

def generate_duplicate_report(config, duplicate_file, original_file, new_filename, logger=None):
    """
    Generiert einen Bericht über ein erkanntes Duplikat.
    
    Je nach Konfiguration wird ein Bericht im HTML-, Text- oder JSON-Format erstellt,
    der detaillierte Informationen über beide Dateien enthält, und optional
    einen visuellen Vergleich der Dokumente.
    
    Args:
        config (dict): Die Anwendungskonfiguration
        duplicate_file (str): Pfad zur Duplikatdatei
        original_file (str): Pfad zur Originaldatei
        new_filename (str): Der generierte neue Dateiname (ohne Pfad)
        logger: Optional, Logger-Instanz für die Protokollierung
    
    Returns:
        str: Pfad zum generierten Bericht oder None bei Fehler
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # Einstellungen für Duplikatberichte aus der Konfiguration laden
        report_format = config.get('duplicate_detection', {}).get('report_format', 'text')
        report_dir = config.get('paths', {}).get('log_dir', '')
        
        # Wenn kein Log-Verzeichnis konfiguriert ist, nehmen wir den Trash-Ordner
        if not report_dir:
            report_dir = config.get('paths', {}).get('trash_dir', '')
        
        # Sicherstellen, dass das Verzeichnis existiert
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        # Eindeutigen Dateinamen für den Bericht generieren
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        report_basename = f"duplicate_report_{timestamp}_{os.path.splitext(new_filename)[0]}"
        
        # Je nach gewünschtem Format den entsprechenden Bericht erstellen
        if report_format.lower() == 'html':
            report_file = os.path.join(report_dir, f"{report_basename}.html")
            generate_html_report(report_file, duplicate_file, original_file, config, logger)
        elif report_format.lower() == 'json':
            report_file = os.path.join(report_dir, f"{report_basename}.json")
            generate_json_report(report_file, duplicate_file, original_file, config, logger)
        else:  # Standardmäßig Textbericht erstellen
            report_file = os.path.join(report_dir, f"{report_basename}.txt")
            generate_text_report(report_file, duplicate_file, original_file, config, logger)
        
        # Visuellen Vergleich erstellen, falls gewünscht
        if config.get('duplicate_detection', {}).get('visual_comparison', False):
            visual_file = os.path.join(report_dir, f"{report_basename}_visual.html")
            generate_visual_comparison(visual_file, duplicate_file, original_file, config, logger)
        
        logger.info(f"Duplikatbericht erstellt: {report_file}")
        return report_file
        
    except Exception as e:
        if logger:
            logger.error(f"Fehler bei der Erstellung des Duplikatberichts: {str(e)}")
        return None