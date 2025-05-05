# Datei: maehrdocs/gui/gui_utils.py

"""
Hilfsfunktionen für MaehrDocs GUI
Enthält verschiedene Hilfsfunktionen für die GUI mit verbesserter Fehlerbehandlung
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from .gui_actions import process_documents
from .gui_logger import log_message

def update_dashboard(app):
    """
    Aktualisiert die Anzeigen im Dashboard
    
    Args:
        app: Instanz der GuiApp
    """
    # Verwenden des ErrorHandlers für diese Operation
    with app.error_handler.safe_operation(context="Dashboard-Aktualisierung", level="warning"):
        # Inbox
        inbox_path = app.config["paths"]["input_dir"]
        inbox_count = len([f for f in os.listdir(inbox_path) if f.lower().endswith('.pdf')])
        app.dashboard_elements["inbox_card"].count_value.config(text=str(inbox_count))
        app.dashboard_elements["inbox_card"].path_value.config(text=inbox_path)
        
        # Processed
        processed_path = app.config["paths"]["output_dir"]
        processed_count = len([f for f in os.listdir(processed_path) if f.lower().endswith('.pdf')])
        app.dashboard_elements["processed_card"].count_value.config(text=str(processed_count))
        app.dashboard_elements["processed_card"].path_value.config(text=processed_path)
        
        # Trash
        trash_path = app.config["paths"]["trash_dir"]
        trash_count = len([f for f in os.listdir(trash_path) if f.lower().endswith('.pdf')])
        app.dashboard_elements["trash_card"].count_value.config(text=str(trash_count))
        app.dashboard_elements["trash_card"].path_value.config(text=trash_path)
        
        # Letzte Verarbeitungszeit aktualisieren
        app.messaging.update_status(f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}")
        
        # Aktivitätsliste aktualisieren, wenn vorhanden
        if "activity_list" in app.dashboard_elements:
            app.dashboard_elements["activity_list"].config(state=tk.NORMAL)
            app.dashboard_elements["activity_list"].delete(1.0, tk.END)
            app.dashboard_elements["activity_list"].insert(tk.END, "Dashboard aktualisiert.")
            app.dashboard_elements["activity_list"].config(state=tk.DISABLED)

def open_folder_in_explorer(app, folder_suffix):
    """
    Öffnet den angegebenen Ordner im Datei-Explorer
    
    Args:
        app: Instanz der GuiApp
        folder_suffix: Ordnersuffix (für die Identifikation)
    """
    # Verwenden der try_except-Methode des ErrorHandlers
    def _open_folder():
        if folder_suffix == "01_InboxDocs":
            folder_path = app.config["paths"]["input_dir"]
        elif folder_suffix == "02_FinalDocs":
            folder_path = app.config["paths"]["output_dir"]
        elif folder_suffix == "03_TrashDocs":
            folder_path = app.config["paths"]["trash_dir"]
        else:
            return
            
        # Plattformabhängiges Öffnen des Ordners
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # macOS oder Linux
            subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', folder_path])
    
    app.error_handler.try_except(
        _open_folder, 
        context="Öffnen des Ordners", 
        level="warning"
    )

def setup_drag_drop(app, drop_callback):
    """
    Richtet Drag & Drop-Funktionalität ein (erfordert tkinterdnd2)
    
    Args:
        app: Instanz der GuiApp
        drop_callback: Callback-Funktion für Drop-Events
    """
    # Prüfen, ob TkinterDnD2 importiert wurde
    if not hasattr(app.root, 'drop_target_register'):
        app.messaging.notify(
            "Drag & Drop nicht verfügbar. TkinterDnD2 ist nicht installiert.", 
            level="warning"
        )
        return
    
    # Register ist nur in tkinterdnd2 verfügbar
    def _setup_dnd():
        app.root.drop_target_register('DND_Files')
        app.root.dnd_bind('<<Drop>>', drop_callback)
    
    app.error_handler.try_except(
        _setup_dnd,
        context="Drag & Drop-Einrichtung",
        level="warning"
    )

def clear_log(app):
    """
    Löscht den Inhalt des Protokolls
    
    Args:
        app: Instanz der GuiApp
    """
    if not hasattr(app, 'log_text') or app.log_text is None:
        return
    
    def _clear_log():
        confirm = app.messaging.dialog(
            "Protokoll löschen", 
            "Möchten Sie das Protokoll wirklich löschen?", 
            type="confirm"
        )
        
        if confirm:
            app.log_text.config(state=tk.NORMAL)
            app.log_text.delete(1.0, tk.END)
            app.log_text.config(state=tk.DISABLED)
            app.messaging.notify("Protokoll gelöscht.")
    
    app.error_handler.try_except(
        _clear_log,
        context="Protokoll löschen",
        level="warning"
    )

def check_for_new_documents(app):
    """
    Prüft periodisch, ob neue Dokumente im Eingangsordner liegen
    
    Args:
        app: Instanz der GuiApp
    """
    # Mit ErrorHandler ausführen, aber keine visuelle Benachrichtigung bei Fehlern
    with app.error_handler.safe_operation(context="Prüfung auf neue Dokumente", level="warning"):
        # Eingangsordner prüfen
        inbox_dir = app.config["paths"]["input_dir"]
        
        if not os.path.exists(inbox_dir):
            # Ordner erstellen, falls er nicht existiert
            os.makedirs(inbox_dir)
            app.messaging.notify(f"Eingangsordner erstellt: {inbox_dir}", level="info")
            
        # Zähle PDF-Dateien
        pdf_count = len([f for f in os.listdir(inbox_dir) if f.lower().endswith('.pdf')])
        
        # Initialisieren, falls noch nicht geschehen
        if not hasattr(app, 'last_inbox_count'):
            app.last_inbox_count = pdf_count
        
        # Wenn neue Dokumente vorhanden sind, Nachricht anzeigen
        if pdf_count > app.last_inbox_count and pdf_count > 0:
            new_count = pdf_count - app.last_inbox_count
            app.messaging.notify(f"{new_count} neue Dokumente im Eingangsordner entdeckt.", level="info")
            
            # Benachrichtigung anzeigen wenn aktiviert
            if app.config.get("gui", {}).get("notify_on_new_documents", True):
                confirm = app.messaging.dialog(
                    "Neue Dokumente", 
                    f"{new_count} neue Dokumente im Eingangsordner entdeckt. Möchten Sie diese jetzt verarbeiten?",
                    type="confirm"
                )
                if confirm:
                    process_documents(app)
        
        # Zustand aktualisieren
        app.last_inbox_count = pdf_count
        
        # Dashboard aktualisieren, wenn sich etwas geändert hat
        if "inbox_card" in app.dashboard_elements:
            current_display = app.dashboard_elements["inbox_card"].count_value.cget("text")
            if pdf_count != int(current_display):
                update_dashboard(app)
    
    # In 5 Sekunden erneut prüfen
    app.root.after(5000, lambda: check_for_new_documents(app))

def create_directory_structure(app):
    """
    Erstellt die Verzeichnisstruktur für die Anwendung
    
    Args:
        app: Instanz der GuiApp
    """
    def _create_dirs():
        # Erstelle alle benötigten Verzeichnisse
        for key, path in app.config["paths"].items():
            if not os.path.exists(path):
                os.makedirs(path)
                app.messaging.notify(f"Verzeichnis erstellt: {path}", level="info")
    
    app.error_handler.try_except(
        _create_dirs,
        context="Verzeichnisstruktur erstellen",
        level="error"
    )

def get_file_count(directory, extension='.pdf'):
    """
    Zählt die Anzahl der Dateien mit der angegebenen Endung im Verzeichnis
    
    Args:
        directory: Verzeichnispfad
        extension: Dateiendung (Standardwert: '.pdf')
        
    Returns:
        int: Anzahl der Dateien
    """
    if not os.path.exists(directory):
        return 0
        
    return len([f for f in os.listdir(directory) if f.lower().endswith(extension.lower())])

def format_timestamp():
    """
    Erstellt einen formatierten Zeitstempel
    
    Returns:
        str: Formatierter Zeitstempel
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def is_valid_path(path):
    """
    Prüft, ob der angegebene Pfad gültig ist
    
    Args:
        path: Zu prüfender Pfad
        
    Returns:
        bool: True, wenn der Pfad gültig ist
    """
    try:
        # Prüfe, ob der Pfad absolut ist
        if not os.path.isabs(path):
            return False
            
        # Prüfe, ob das Verzeichnis existiert
        if not os.path.exists(os.path.dirname(path)):
            return False
            
        # Prüfe, ob der Pfad ein Verzeichnis ist
        if os.path.isdir(path):
            # Prüfe, ob wir Schreibrechte haben
            return os.access(path, os.W_OK)
        
        # Wenn es eine Datei ist, prüfe, ob wir in das übergeordnete Verzeichnis schreiben können
        return os.access(os.path.dirname(path), os.W_OK)
    
    except Exception:
        return False