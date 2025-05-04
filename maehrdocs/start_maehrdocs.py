#!/usr/bin/env python
"""
Starter-Skript für MaehrDocs
Startet die GUI der Anwendung
"""

import tkinter as tk
import logging
import os
import sys

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
    from maehrdocs.gui import GuiApp
except ImportError as e:
    logging.error(f"Fehler beim Importieren der Module: {str(e)}")
    print(f"Fehler: {str(e)}")
    print("Stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden und alle Abhängigkeiten installiert sind.")
    sys.exit(1)

def main():
    """
    Hauptfunktion zum Starten der GUI
    """
    try:
        # Erstelle eine Instanz des ConfigManager
        config_manager = ConfigManager()
        
        # Lade oder erstelle die Konfiguration
        config = config_manager.get_config()
        
        # Erstelle eine Instanz des DocumentProcessor
        document_processor = DocumentProcessor(config)
        
        # Erstelle die GUI-Anwendung
        app = GuiApp(config_manager, document_processor)
        
        # Starte die GUI
        root = app.setup_gui()
        
        # Starte den Event-Loop
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        print(f"Fehler: {str(e)}")
        input("Drücken Sie Enter, um zu beenden.")
        sys.exit(1)

if __name__ == "__main__":
    main()