"""
Haupteinstiegspunkt für MaehrDocs
Enthält die Kommandozeilenargumente und die CLI-Logik
"""

import os
import sys
import argparse
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

from maehrdocs.config import ConfigManagerExtended
from maehrdocs.document_processor import DocumentProcessor
from maehrdocs.error_handler import ErrorHandler

def parse_arguments():
    """
    Parst die Kommandozeilenargumente

    Returns:
        argparse.Namespace: Die geparsten Argumente
    """
    parser = argparse.ArgumentParser(description='MaehrDocs - Dokumentenmanagementsystem')
    
    # Allgemeine Optionen
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Erhöht die Ausführlichkeit der Ausgabe (kann mehrfach verwendet werden)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simuliert die Verarbeitung ohne Dateioperationen')
    
    # Verschiedene Modi
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--process', action='store_true',
                      help='Verarbeitet alle PDF-Dokumente im Eingangsordner')
    group.add_argument('--file', metavar='FILE',
                      help='Verarbeitet eine einzelne PDF-Datei')
    group.add_argument('--config', action='store_true',
                      help='Zeigt die aktuelle Konfiguration an')
    group.add_argument('--reset-config', action='store_true',
                      help='Setzt die Konfiguration zurück')
    
    return parser.parse_args()

def setup_logging(config, verbose_level=0):
    """
    Richtet das Logging basierend auf der Konfiguration und Ausführlichkeitsstufe ein

    Args:
        config (dict): Konfiguration mit Logging-Einstellungen
        verbose_level (int): Die Ausführlichkeitsstufe (0-2), überschreibt die Konfiguration
        
    Returns:
        logging.Logger: Root-Logger
    """
    # Log-Levels aus Verbose-Stufe oder Konfiguration
    cmd_log_levels = {
        0: logging.WARNING,  # Standardlevel
        1: logging.INFO,     # -v
        2: logging.DEBUG     # -vv
    }
    
    # Sicherstellen, dass verbose_level im gültigen Bereich liegt
    if verbose_level > max(cmd_log_levels.keys()):
        verbose_level = max(cmd_log_levels.keys())
    
    # Einstellungen aus der Konfiguration laden
    log_config = config.get('logging', {})
    log_level_str = log_config.get('level', 'info').upper()
    file_logging = log_config.get('file_logging', True)
    console_logging = log_config.get('console_logging', True)
    max_log_files = log_config.get('max_log_files', 10)
    max_file_size_mb = log_config.get('max_file_size_mb', 5)
    
    # Log-Level bestimmen (Kommandozeile hat Vorrang)
    if verbose_level > 0:
        log_level = cmd_log_levels.get(verbose_level)
    else:
        log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Root-Logger konfigurieren
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Alte Handler entfernen (falls vorhanden)
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
        today = datetime.now().strftime('%Y%m%d')
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

def main():
    """
    Hauptfunktion des Programms
    Verarbeitet die Argumente und führt die entsprechende Aktion aus
    """
    # Argumente parsen
    args = parse_arguments()
    
    # Zeit messen
    start_time = time.time()
    
    try:
        # Konfiguration laden
        config_manager = ConfigManagerExtended()
        config = config_manager.get_config()
        
        # Logging einrichten (mit Konfiguration und Kommandozeilenargumenten)
        logger = setup_logging(config, args.verbose)
        
        # Begrüßungsmeldung
        logger.info("MaehrDocs - Dokumentenmanagementsystem")
        logger.info(f"Ausführung gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Konfigurationsbezogene Aktionen
        if args.config:
            # Zeige die Konfiguration an
            import yaml
            print(yaml.dump(config, default_flow_style=False))
            return
        elif args.reset_config:
            # Konfiguration zurücksetzen
            config_manager.reset_config()
            logger.info("Konfiguration wurde zurückgesetzt.")
            return
        
        # DocumentProcessor initialisieren
        document_processor = DocumentProcessor(config)
        
        # Verarbeitungsaktionen
        results = []
        if args.file:
            # Einzelnes Dokument verarbeiten
            if not os.path.exists(args.file):
                logger.error(f"Die angegebene Datei existiert nicht: {args.file}")
                return
            
            result = document_processor.process_document(args.file, dry_run=args.dry_run)
            if result:
                results.append(result)
        elif args.process or not any([args.config, args.reset_config, args.file]):
            # Standard: Alle Dokumente im Eingangsordner verarbeiten
            input_dir = config.get('paths', {}).get('input_dir', '')
            
            if not os.path.exists(input_dir):
                logger.error(f"Der Eingangsordner existiert nicht: {input_dir}")
                return
            
            # Über alle Dateien im Eingangsordner iterieren
            for filename in os.listdir(input_dir):
                file_path = os.path.join(input_dir, filename)
                # Nur Dateien verarbeiten, keine Verzeichnisse
                if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
                    # Einzelnes Dokument verarbeiten
                    result = document_processor.process_document(file_path, dry_run=args.dry_run)
                    if result:
                        results.append(result)
        
        # Zusammenfassung ausgeben
        if args.process or args.file or not any([args.config, args.reset_config]):
            logger.info(f"Verarbeitung abgeschlossen. {len(results)} Dokumente verarbeitet.")
            if args.dry_run:
                logger.info("Simulationsmodus: Es wurden keine Dateioperationen durchgeführt.")
        
    except Exception as e:
        # Minimale Logging-Einrichtung, falls das Logging noch nicht eingerichtet wurde
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        logger = logging.getLogger(__name__)
        
        error_handler = ErrorHandler()
        error_handler.handle_exception(e)
        logger.error(f"Fehler: {str(e)}")
        return 1
    
    # Zeitauswertung
    total_time = time.time() - start_time
    logger.info(f"Gesamtlaufzeit: {total_time:.2f} Sekunden")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())