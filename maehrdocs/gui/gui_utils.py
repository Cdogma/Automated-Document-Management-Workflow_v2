"""
Hilfsfunktionen für MaehrDocs GUI
Enthält verschiedene Hilfsfunktionen für die GUI
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
    try:
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
        app.status_label.config(text=f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}")
        
        # Aktivitätsliste aktualisieren, wenn vorhanden
        if "activity_list" in app.dashboard_elements:
            app.dashboard_elements["activity_list"].config(state=tk.NORMAL)
            app.dashboard_elements["activity_list"].delete(1.0, tk.END)
            app.dashboard_elements["activity_list"].insert(tk.END, "Dashboard aktualisiert.")
            app.dashboard_elements["activity_list"].config(state=tk.DISABLED)
            
    except Exception as e:
        log_message(app, f"Fehler beim Aktualisieren des Dashboards: {str(e)}", level="error")

def open_folder_in_explorer(app, folder_suffix):
    """
    Öffnet den angegebenen Ordner im Datei-Explorer
    
    Args:
        app: Instanz der GuiApp
        folder_suffix: Ordnersuffix (für die Identifikation)
    """
    try:
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
            
    except Exception as e:
        log_message(app, f"Fehler beim Öffnen des Ordners: {str(e)}", level="error")

def setup_drag_drop(app, drop_callback):
    """
    Richtet Drag & Drop-Funktionalität ein (erfordert tkinterdnd2)
    
    Args:
        app: Instanz der GuiApp
        drop_callback: Callback-Funktion für Drop-Events
    """
    # Prüfen, ob TkinterDnD2 importiert wurde
    if not hasattr(app.root, 'drop_target_register'):
        log_message(app, "Drag & Drop nicht verfügbar. TkinterDnD2 ist nicht installiert.", level="warning")
        return
    
    # Register ist nur in tkinterdnd2 verfügbar
    try:
        app.root.drop_target_register('DND_Files')
        app.root.dnd_bind('<<Drop>>', drop_callback)
    except AttributeError:
        log_message(app, "Fehler beim Einrichten von Drag & Drop", level="error")

def clear_log(app):
    """
    Löscht den Inhalt des Protokolls
    
    Args:
        app: Instanz der GuiApp
    """
    if not hasattr(app, 'log_text') or app.log_text is None:
        return
        
    if messagebox.askyesno("Protokoll löschen", "Möchten Sie das Protokoll wirklich löschen?"):
        app.log_text.config(state=tk.NORMAL)
        app.log_text.delete(1.0, tk.END)
        app.log_text.config(state=tk.DISABLED)
        log_message(app, "Protokoll gelöscht.")

def check_for_new_documents(app):
    """
    Prüft periodisch, ob neue Dokumente im Eingangsordner liegen
    
    Args:
        app: Instanz der GuiApp
    """
    try:
        # Eingangsordner prüfen
        inbox_dir = app.config["paths"]["input_dir"]
        
        if not os.path.exists(inbox_dir):
            # Ordner erstellen, falls er nicht existiert
            os.makedirs(inbox_dir)
            log_message(app, f"Eingangsordner erstellt: {inbox_dir}", level="info")
            
        # Zähle PDF-Dateien
        pdf_count = len([f for f in os.listdir(inbox_dir) if f.lower().endswith('.pdf')])
        
        # Initialisieren, falls noch nicht geschehen
        if not hasattr(app, 'last_inbox_count'):
            app.last_inbox_count = pdf_count
        
        # Wenn neue Dokumente vorhanden sind, Nachricht anzeigen
        if pdf_count > app.last_inbox_count and pdf_count > 0:
            new_count = pdf_count - app.last_inbox_count
            log_message(app, f"{new_count} neue Dokumente im Eingangsordner entdeckt.", level="info")
            
            # Benachrichtigung anzeigen wenn aktiviert
            if app.config.get("gui", {}).get("notify_on_new_documents", True):
                if messagebox.askyesno("Neue Dokumente", 
                                     f"{new_count} neue Dokumente im Eingangsordner entdeckt. Möchten Sie diese jetzt verarbeiten?"):
                    process_documents(app)
        
        # Zustand aktualisieren
        app.last_inbox_count = pdf_count
        
        # Dashboard aktualisieren, wenn sich etwas geändert hat
        if "inbox_card" in app.dashboard_elements:
            current_display = app.dashboard_elements["inbox_card"].count_value.cget("text")
            if pdf_count != int(current_display):
                update_dashboard(app)
        
    except Exception as e:
        log_message(app, f"Fehler beim Prüfen auf neue Dokumente: {str(e)}", level="error")
    
    # In 5 Sekunden erneut prüfen
    app.root.after(5000, lambda: check_for_new_documents(app))

def create_directory_structure(app):
    """
    Erstellt die Verzeichnisstruktur für die Anwendung
    
    Args:
        app: Instanz der GuiApp
    """
    try:
        # Erstelle alle benötigten Verzeichnisse
        for key, path in app.config["paths"].items():
            if not os.path.exists(path):
                os.makedirs(path)
                log_message(app, f"Verzeichnis erstellt: {path}", level="info")
    except Exception as e:
        log_message(app, f"Fehler beim Erstellen der Verzeichnisstruktur: {str(e)}", level="error")

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