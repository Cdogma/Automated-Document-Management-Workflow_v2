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

def setup_logging(verbose_level):
    """
    Richtet das Logging basierend auf der Ausführlichkeitsstufe ein

    Args:
        verbose_level (int): Die Ausführlichkeitsstufe (0-2)
    """
    log_levels = {
        0: logging.WARNING,  # Standardlevel
        1: logging.INFO,     # -v
        2: logging.DEBUG     # -vv
    }
    
    # Sicherstellen, dass verbose_level im gültigen Bereich liegt
    if verbose_level > max(log_levels.keys()):
        verbose_level = max(log_levels.keys())
    
    # Logging konfigurieren
    log_level = log_levels.get(verbose_level, logging.WARNING)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Konsolenausgabe
            logging.FileHandler(f'maehrdocs_{datetime.now().strftime("%Y%m%d")}.log')  # Dateiausgabe
        ]
    )

def main():
    """
    Hauptfunktion des Programms
    Verarbeitet die Argumente und führt die entsprechende Aktion aus
    """
    # Argumente parsen
    args = parse_arguments()
    
    # Logging einrichten
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Begrüßungsmeldung
    logger.info("MaehrDocs - Dokumentenmanagementsystem")
    logger.info(f"Ausführung gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Zeit messen
    start_time = time.time()
    
    try:
        # Konfiguration laden
        config_manager = ConfigManagerExtended()
        config = config_manager.get_config()
        
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
                if os.path.isfile(file_path):
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