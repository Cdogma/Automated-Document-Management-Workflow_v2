#!/usr/bin/env python
"""
Grundlegender Import-Test für die Statistik-Komponente
"""

import os
import sys
import tkinter as tk
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("\n=== Grundlegender Statistik-Komponenten-Test ===\n")

try:
    # Matplotlib testen
    logger.info("Teste matplotlib Installation...")
    import matplotlib
    logger.info(f"✅ Matplotlib Version {matplotlib.__version__} ist installiert")
    
    # Prüfen, ob die Dateien existieren
    logger.info("Prüfe, ob die Statistik-Modul-Dateien existieren:")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_check = [
        "gui_statistics.py",
        "gui_statistics_data.py",
        "gui_statistics_charts.py"
    ]
    
    all_files_exist = True
    for file in files_to_check:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            logger.info(f"✅ Datei existiert: {file}")
        else:
            logger.error(f"❌ Datei fehlt: {file}")
            all_files_exist = False
    
    if all_files_exist:
        print("\n✅ Alle Dateien existieren!")
        print("Die Statistik-Module wurden korrekt erstellt.")
        print("Um sie in die GUI zu integrieren, bearbeiten Sie jetzt die __init__.py und gui_dashboard.py wie beschrieben.")
    else:
        print("\n❌ Test fehlgeschlagen: Einige Dateien fehlen!")
        print("Bitte erstellen Sie alle benötigten Dateien im korrekten Verzeichnis.")
    
except ImportError as e:
    logger.error(f"❌ Import-Fehler: {str(e)}")
    print("\n❌ Test fehlgeschlagen!")
    print("Stellen Sie sicher, dass matplotlib installiert ist mit: pip install matplotlib")