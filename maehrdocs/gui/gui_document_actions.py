"""
Dokumentenaktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Dokumenten
"""

import os
import sys
from tkinter import filedialog, messagebox

def process_documents(app):
    """
    Verarbeitet alle Dokumente im Eingangsordner
    
    Args:
        app: Instanz der GuiApp
    """
    from .gui_command_executor import run_command_in_thread
    # Direkter Pfad zur main.py im maehrdocs-Verzeichnis
    script_dir = os.path.dirname(os.path.dirname(__file__))  # Übergeordnetes Verzeichnis
    main_script = os.path.join(script_dir, "main.py")
    # Python-Umgebungsvariable PYTHONPATH setzen, um das Paket zu finden
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(script_dir)  # Übergeordnetes Verzeichnis des Projektverzeichnisses
    run_command_in_thread(app, [sys.executable, main_script], env=env)

def simulate_processing(app):
    """
    Führt eine Simulation (Dry-Run) durch
    
    Args:
        app: Instanz der GuiApp
    """
    from .gui_command_executor import run_command_in_thread
    script_dir = os.path.dirname(os.path.dirname(__file__))
    main_script = os.path.join(script_dir, "main.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(script_dir)
    run_command_in_thread(app, [sys.executable, main_script, "--dry-run"], env=env)

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
        script_dir = os.path.dirname(os.path.dirname(__file__))
        main_script = os.path.join(script_dir, "main.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(script_dir)
        run_command_in_thread(app, [sys.executable, main_script, "--single-file", file_path], env=env)

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
        script_dir = os.path.dirname(os.path.dirname(__file__))
        main_script = os.path.join(script_dir, "main.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(script_dir)
        run_command_in_thread(app, [sys.executable, main_script, "--rebuild-config"], env=env)