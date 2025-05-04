"""
Dokumentenaktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Dokumenten
"""

import os
from tkinter import filedialog, messagebox

def process_documents(app):
    """
    Verarbeitet alle Dokumente im Eingangsordner
    
    Args:
        app: Instanz der GuiApp
    """
    from .gui_command_executor import run_command_in_thread
    run_command_in_thread(app, ["python", "autodocs_v2.py"])

def simulate_processing(app):
    """
    Führt eine Simulation (Dry-Run) durch
    
    Args:
        app: Instanz der GuiApp
    """
    from .gui_command_executor import run_command_in_thread
    run_command_in_thread(app, ["python", "autodocs_v2.py", "--dry-run"])

def process_single_file(app):
    """
    Verarbeitet eine einzelne vom Benutzer ausgewählte Datei
    
    Args:
        app: Instanz der GuiApp
    """
    file_path = filedialog.askopenfilename(
        title="PDF-Datei auswählen",
        filetypes=[("PDF-Dateien", "*.pdf")]
    )
    
    if file_path:
        from .gui_command_executor import run_command_in_thread
        run_command_in_thread(app, ["python", "autodocs_v2.py", "--single-file", file_path])

def rebuild_config(app):
    """
    Setzt die Konfiguration zurück
    
    Args:
        app: Instanz der GuiApp
    """
    if messagebox.askyesno(
        "Konfiguration zurücksetzen", 
        "Möchten Sie die Konfiguration wirklich zurücksetzen? "
        "Alle benutzerdefinierten Einstellungen gehen verloren."
    ):
        from .gui_command_executor import run_command_in_thread
        run_command_in_thread(app, ["python", "autodocs_v2.py", "--rebuild-config"])