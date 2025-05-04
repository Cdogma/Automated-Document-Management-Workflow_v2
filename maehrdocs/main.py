#!/usr/bin/env python
"""
Haupteinstiegspunkt für MaehrDocs
Enthält die Kommandozeilenargumente und die CLI-Logik
"""

import argparse
import logging
import os
import sys
import time

# Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('maehrdocs.log', encoding='utf-8')
    ]
)

# Importiere notwendige Module
try:
    from maehrdocs import ConfigManager, DocumentProcessor
except ImportError as e:
    logging.error(f"Fehler beim Importieren der Module: {str(e)}")
    print(f"Fehler: {str(e)}")
    print("Stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden und alle Abhängigkeiten installiert sind.")
    sys.exit(1)

def parse_arguments():
    """
    Parst die Kommandozeilenargumente
    
    Returns:
        argparse.Namespace: Die geparsten Argumente
    """
    parser = argparse.ArgumentParser(description='MaehrDocs - Automatisches Dokumentenmanagementsystem')
    
    # Optionale Argumente
    parser.add_argument('--dry-run', action='store_true', 
                      help='Simulation ohne tatsächliche Änderungen')
    parser.add_argument('--single-file', type=str, metavar='FILE',
                      help='Verarbeitet eine einzelne PDF-Datei statt des Eingangsordners')
    parser.add_argument('--rebuild-config', action='store_true',
                      help='Erstellt die Konfigurationsdatei neu mit Standardwerten')
    parser.add_argument('--force', action='store_true',
                      help='Überschreibt vorhandene Dateien ohne Rückfrage')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                      help='Erhöht die Ausführlichkeit der Ausgabe (verwende -vv für noch mehr Details)')
    
    return parser.parse_args()

def setup_logging(verbose_level):
    """
    Richtet das Logging basierend auf der Ausführlichkeitsstufe ein
    
    Args:
        verbose_level: Ausführlichkeitsstufe (0=normal, 1=verbose, 2=debug)
    """
    # Logging-Level basierend auf der Ausführlichkeitsstufe festlegen
    if verbose_level >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose_level >= 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    logging.info(f"Logging-Level gesetzt auf: {logging.getLogger().getEffectiveLevel()}")

def main():
    """
    Hauptfunktion des Programms
    """
    try:
        # Argumente parsen
        args = parse_arguments()
        
        # Logging einrichten
        setup_logging(args.verbose)
        
        # Konfiguration laden oder neu erstellen
        config_manager = ConfigManager()
        
        # Wenn die Konfiguration neu erstellt werden soll
        if args.rebuild_config:
            logging.info("Erstelle Konfigurationsdatei neu...")
            config = config_manager.create_default_config()
            config_manager.save_config(config)
            logging.info("Konfigurationsdatei wurde neu erstellt.")
            return
        
        # Konfiguration laden
        config = config_manager.get_config()
        
        # Dokumentenprozessor erstellen
        document_processor = DocumentProcessor(config)
        
        # Verbosity-Level setzen
        document_processor.verbose = args.verbose
        
        # Force-Option setzen
        document_processor.force = args.force
        
        # Einzelne Datei verarbeiten
        if args.single_file:
            file_path = args.single_file
            if not os.path.exists(file_path):
                logging.error(f"Datei nicht gefunden: {file_path}")
                return
                
            logging.info(f"Verarbeite einzelne Datei: {file_path}")
            result = document_processor.process_document(file_path, dry_run=args.dry_run)
            
            if result:
                logging.info(f"Dokument verarbeitet: {result['new_filename']}")
                if result.get('is_duplicate', False):
                    logging.warning(f"Duplikat erkannt: Ähnlich zu {result['duplicate_path']}")
            else:
                logging.error(f"Fehler bei der Verarbeitung von {file_path}")
        
        # Alle Dokumente im Eingangsordner verarbeiten
        else:
            mode = "Simulation" if args.dry_run else "Verarbeitung"
            logging.info(f"{mode} aller Dokumente im Eingangsordner gestartet...")
            
            start_time = time.time()
            results = document_processor.process_all_documents(dry_run=args.dry_run)
            end_time = time.time()
            
            if results:
                logging.info(f"{len(results)} Dokumente verarbeitet in {end_time - start_time:.2f} Sekunden.")
            else:
                logging.warning("Keine Dokumente verarbeitet oder Fehler aufgetreten.")
        
    except KeyboardInterrupt:
        logging.info("Programm durch Benutzer abgebrochen.")
    except Exception as e:
        logging.error(f"Fehler: {str(e)}", exc_info=True)
        print(f"Fehler: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())