"""
Logging-Funktionalität für MaehrDocs GUI
Enthält Funktionen zum Protokollieren von Nachrichten
"""

import tkinter as tk
import logging
from datetime import datetime

def setup_logging(app):
    """
    Richtet die Tags für das Logging ein
    
    Args:
        app: Instanz der GuiApp
    """
    if not hasattr(app, 'log_text') or app.log_text is None:
        return
        
    # Tags für verschiedene Log-Level erstellen
    app.log_text.config(state=tk.NORMAL)
    
    # Nur erstellen, wenn noch nicht vorhanden
    if not hasattr(app.log_text, 'tags_created'):
        app.log_text.tag_configure("error", foreground=app.colors["error"])
        app.log_text.tag_configure("warning", foreground=app.colors["warning"])
        app.log_text.tag_configure("success", foreground=app.colors["success"])
        app.log_text.tag_configure("info", foreground=app.colors["text_primary"])
        app.log_text.tags_created = True
    
    app.log_text.config(state=tk.DISABLED)

def log_message(app, message, level="info"):
    """
    Fügt eine Nachricht zum Protokollbereich hinzu
    
    Args:
        app: Instanz der GuiApp
        message: Die zu protokollierende Nachricht
        level: Log-Level (info, warning, error, success)
    """
    if not hasattr(app, 'log_text') or app.log_text is None:
        return
        
    # Aktuelle Zeit
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Farbe und Präfix je nach Level
    tag = None
    if level == "error":
        tag = "error"
        prefix = "❌ FEHLER"
        log_level = logging.ERROR
    elif level == "warning":
        tag = "warning"
        prefix = "⚠️ WARNUNG"
        log_level = logging.WARNING
    elif level == "success":
        tag = "success"
        prefix = "✅ ERFOLG"
        log_level = logging.INFO
    else:
        tag = "info"
        prefix = "ℹ️ INFO"
        log_level = logging.INFO
    
    # Log an Logger-Objekt senden
    if hasattr(app, 'logger'):
        app.logger.log(log_level, message)
    
    # Log-Eintrag formatieren
    log_entry = f"[{timestamp}] {prefix}: {message}\n"
    
    # Text-Widget aktualisieren
    app.log_text.config(state=tk.NORMAL)
    
    # Tags erstellen, falls noch nicht vorhanden
    if not hasattr(app.log_text, 'tags_created'):
        setup_logging(app)
    
    # Text einfügen
    app.log_text.insert(tk.END, log_entry, tag)
    
    # Zum Ende scrollen
    app.log_text.see(tk.END)
    
    # Auf read-only setzen
    app.log_text.config(state=tk.DISABLED)
    
    # Letzte Aktivität aktualisieren
    update_activity_display(app, message)

def update_activity_display(app, message):
    """
    Aktualisiert die Aktivitätsanzeige mit der neuesten Nachricht
    
    Args:
        app: Instanz der GuiApp
        message: Die Nachricht, die angezeigt werden soll
    """
    if hasattr(app, 'dashboard_elements') and "activity_list" in app.dashboard_elements:
        activity_list = app.dashboard_elements["activity_list"]
        activity_list.config(state=tk.NORMAL)
        activity_list.delete(1.0, tk.END)
        activity_list.insert(tk.END, message)
        activity_list.config(state=tk.DISABLED)

def export_log(app, filepath=None):
    """
    Exportiert das aktuelle Protokoll in eine Datei
    
    Args:
        app: Instanz der GuiApp
        filepath: Pfad zur Zieldatei (optional)
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    if not hasattr(app, 'log_text') or app.log_text is None:
        return False
    
    try:
        # Wenn kein Pfad angegeben wurde, einen Dialog öffnen
        if filepath is None:
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log-Dateien", "*.log"), ("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
            )
            
            if not filepath:  # Benutzer hat abgebrochen
                return False
        
        # Protokollinhalt holen
        app.log_text.config(state=tk.NORMAL)
        log_content = app.log_text.get(1.0, tk.END)
        app.log_text.config(state=tk.DISABLED)
        
        # In Datei schreiben
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        log_message(app, f"Protokoll exportiert nach: {filepath}", level="success")
        return True
        
    except Exception as e:
        log_message(app, f"Fehler beim Exportieren des Protokolls: {str(e)}", level="error")
        return False