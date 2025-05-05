"""
Logging-Funktionalität für MaehrDocs GUI
Implementiert ein visuelles Logging-System mit farblicher Hervorhebung verschiedener
Log-Levels (Info, Warnung, Fehler, Erfolg) und Integration in die GUI-Komponenten.

Dieses Modul verbindet das Python-Standard-Logging mit der grafischen Benutzeroberfläche
und sorgt für konsistente und gut sichtbare Statusmeldungen während der Anwendungsausführung.
"""

import tkinter as tk
import logging
from datetime import datetime

def setup_logging(app):
    """
    Richtet die Tags für das Logging im Textfeld ein und konfiguriert die Formatierung.
    
    Erstellt farbliche Tags für verschiedene Log-Levels, um die visuelle Unterscheidung
    von Meldungen zu ermöglichen und die Benutzerfreundlichkeit zu verbessern.
    
    Args:
        app: Die GuiApp-Instanz mit dem konfigurierten log_text-Widget
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
    Fügt eine formatierte Nachricht zum Protokollbereich der GUI hinzu.
    
    Die Nachricht wird mit Zeitstempel, Präfix je nach Level und entsprechender
    Farbformatierung dargestellt. Zusätzlich wird die Nachricht an den Standard-Logger
    weitergeleitet und in der Aktivitätsanzeige des Dashboards aktualisiert.
    
    Args:
        app: Die GuiApp-Instanz mit dem konfigurierten log_text-Widget
        message (str): Die zu protokollierende Nachricht
        level (str): Log-Level ("info", "warning", "error", "success")
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
    Aktualisiert die Aktivitätsanzeige im Dashboard mit der neuesten Nachricht.
    
    Zeigt die letzte Aktivität prominent im Dashboard an, um einen schnellen
    Überblick über den aktuellen Status der Anwendung zu bieten, ohne dass
    der Benutzer das vollständige Protokoll durchsuchen muss.
    
    Args:
        app: Die GuiApp-Instanz mit konfiguriertem Dashboard
        message (str): Die anzuzeigende Nachricht
    """
    if hasattr(app, 'dashboard_elements') and "activity_list" in app.dashboard_elements:
        activity_list = app.dashboard_elements["activity_list"]
        activity_list.config(state=tk.NORMAL)
        activity_list.delete(1.0, tk.END)
        activity_list.insert(tk.END, message)
        activity_list.config(state=tk.DISABLED)

def export_log(app, filepath=None):
    """
    Exportiert das aktuelle Protokoll in eine Textdatei.
    
    Ermöglicht es dem Benutzer, den kompletten Protokollinhalt für
    Dokumentations- oder Fehlerbehebungszwecke zu speichern.
    
    Args:
        app: Die GuiApp-Instanz mit dem konfigurierten log_text-Widget
        filepath (str, optional): Zieldatei-Pfad. Falls None, wird ein Dialog geöffnet.
        
    Returns:
        bool: True bei erfolgreicher Durchführung, False bei Fehler
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