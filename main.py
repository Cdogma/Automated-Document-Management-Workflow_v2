import logging
import argparse
import sys
import os

# Importiere die Module aus dem maehrdocs-Paket
from maehrdocs.config import ConfigManager
from maehrdocs.document_processor import DocumentProcessor
from maehrdocs.gui_manager import GuiManager

def setup_logging(verbose=0):
    """Richtet das Logging ein"""
    log_levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    
    # Wähle das Log-Level basierend auf dem verbose-Parameter
    log_level = log_levels.get(verbose, logging.DEBUG)
    
    # Konfiguriere das Logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def parse_arguments():
    """Verarbeitet Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(description='MaehrDocs - Automatisches Dokumentenmanagementsystem')
    
    parser.add_argument('--dry-run', action='store_true', help='Simulationsmodus (keine Änderungen)')
    parser.add_argument('--single-file', type=str, help='Einzelne Datei verarbeiten')
    parser.add_argument('--rebuild-config', action='store_true', help='Konfiguration zurücksetzen')
    parser.add_argument('--force', action='store_true', help='Vorhandene Dateien überschreiben')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Erhöht den Detaillierungsgrad')
    parser.add_argument('--gui', action='store_true', help='Startet die GUI')
    
    return parser.parse_args()

def main():
    """Hauptfunktion des Programms"""
    args = parse_arguments()
    
    # Richte das Logging ein
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Erstelle die Konfiguration
    config_manager = ConfigManager()
    
    # Wenn --rebuild-config angegeben wurde, setze die Konfiguration zurück
    if args.rebuild_config:
        logger.info("Konfiguration wird zurückgesetzt...")
        config_manager.create_default_config()
        logger.info("Konfiguration wurde zurückgesetzt.")
        return
    
    # Erstelle den DocumentProcessor
    document_processor = DocumentProcessor(config_manager)
    
    # GUI oder Kommandozeilenmodus
    if args.gui:
        logger.info("Starte GUI...")
        gui_manager = GuiManager(config_manager, document_processor)
        root = gui_manager.setup_gui()
        root.mainloop()
    else:
        # Kommandozeilenmodus
        if args.single_file:
            # Einzelne Datei verarbeiten
            if not os.path.exists(args.single_file):
                logger.error(f"Datei nicht gefunden: {args.single_file}")
                return
                
            logger.info(f"Verarbeite Datei: {args.single_file}")
            result = document_processor.process_document(args.single_file, dry_run=args.dry_run, force=args.force)
            
            if result:
                logger.info(f"Dokument verarbeitet: {args.single_file} → {result['new_filename']}")
                if result['is_duplicate']:
                    logger.warning(f"Duplikat erkannt: Ähnlich zu {result['duplicate_path']}")
        else:
            # Alle Dokumente im Eingangsordner verarbeiten
            logger.info("Verarbeite alle Dokumente im Eingangsordner...")
            results = document_processor.process_all_documents(dry_run=args.dry_run, force=args.force)
            
            if results:
                logger.info(f"{len(results)} Dokumente verarbeitet.")

if __name__ == "__main__":
    main()