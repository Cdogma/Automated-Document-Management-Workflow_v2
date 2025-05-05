"""
Layout-Komponenten für MaehrDocs GUI
Enthält Funktionen zur strukturierten Erstellung der Hauptlayout-Bereiche der Anwendung:
Header, Steuerungspanel, Protokollbereich und Statusleiste.

Diese Module bilden das visuelle Grundgerüst der Anwendung und stellen eine konsistente
Benutzeroberfläche sicher, die den Design-Standards der MaehrDocs-Anwendung entspricht.
"""

import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

from .gui_buttons import create_button
from .gui_actions import (
    process_documents, 
    simulate_processing, 
    process_single_file, 
    rebuild_config
)

def create_header(app, parent, settings_callback, help_callback):
    """
    Erstellt den Kopfbereich der GUI mit Logo, Titel und Funktionsschaltflächen.
    
    Der Header dient als primärer Navigationspunkt und enthält den Anwendungstitel
    sowie Schnellzugriff auf Einstellungen und Hilfefunktionen.
    
    Args:
        app: Die GuiApp-Instanz mit den Farbdefinitionen und Schriftarten
        parent: Das übergeordnete Widget, in dem der Header platziert wird
        settings_callback: Callback-Funktion für den Einstellungen-Button
        help_callback: Callback-Funktion für den Hilfe-Button
        
    Returns:
        dict: Dictionary mit allen erstellten Header-Elementen für späteren Zugriff
    """
    header_elements = {}
    
    # Header-Frame erstellen
    header_frame = tk.Frame(parent, bg=app.colors["background_dark"], padx=15, pady=15)
    header_frame.pack(fill=tk.X)
    
    # Logo/Titel-Bereich
    title_frame = tk.Frame(header_frame, bg=app.colors["background_dark"])
    title_frame.pack(side=tk.LEFT)
    
    # Haupttitel
    title_label = tk.Label(
        title_frame, 
        text="MaehrDocs", 
        font=app.fonts["header"],
        bg=app.colors["background_dark"],
        fg=app.colors["primary"]
    )
    title_label.pack(anchor=tk.W)
    
    # Untertitel
    subtitle_label = tk.Label(
        title_frame, 
        text="Automatisches Dokumentenmanagementsystem", 
        font=app.fonts["normal"],
        bg=app.colors["background_dark"],
        fg=app.colors["text_secondary"]
    )
    subtitle_label.pack(anchor=tk.W)
    
    # Buttons-Bereich
    buttons_frame = tk.Frame(header_frame, bg=app.colors["background_dark"])
    buttons_frame.pack(side=tk.RIGHT)
    
    # Einstellungen-Button
    settings_button = create_button(
        app,
        buttons_frame, 
        "⚙️ Einstellungen", 
        settings_callback
    )
    settings_button.pack(side=tk.RIGHT, padx=5)
    
    # Hilfe-Button
    help_button = create_button(
        app,
        buttons_frame, 
        "❓ Hilfe", 
        help_callback
    )
    help_button.pack(side=tk.RIGHT, padx=5)
    
    # Elemente speichern
    header_elements["header_frame"] = header_frame
    header_elements["title_label"] = title_label
    header_elements["subtitle_label"] = subtitle_label
    header_elements["settings_button"] = settings_button
    header_elements["help_button"] = help_button
    
    return header_elements

def create_control_panel(app, parent):
    """
    Erstellt das Steuerungspanel mit den Hauptfunktionsschaltflächen.
    
    Das Steuerungspanel enthält alle primären Aktionsschaltflächen für die 
    Dokumentverarbeitung sowie weitere Funktionen wie Konfigurationsreset.
    Es bildet das zentrale Bedienelement der Anwendung.
    
    Args:
        app: Die GuiApp-Instanz mit den Farbdefinitionen und Schriftarten
        parent: Das übergeordnete Widget, in dem das Panel platziert wird
        
    Returns:
        dict: Dictionary mit allen erstellten Steuerungselementen für späteren Zugriff
    """
    control_elements = {}
    
    # Frame für das Steuerungspanel
    control_frame = tk.Frame(parent, bg=app.colors["card_background"], padx=15, pady=15)
    control_frame.pack(fill=tk.X, pady=10)
    
    # Überschrift
    control_header = tk.Label(
        control_frame, 
        text="Dokumentenverarbeitung", 
        font=app.fonts["subheader"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    )
    control_header.pack(anchor=tk.W, pady=(0, 10))
    
    # Buttons-Rahmen
    buttons_frame = tk.Frame(control_frame, bg=app.colors["card_background"])
    buttons_frame.pack(fill=tk.X)
    
    # Alle verarbeiten Button
    process_button = create_button(
        app,
        buttons_frame, 
        "📄 Alle Dokumente verarbeiten", 
        lambda: process_documents(app)
    )
    process_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Simulation Button
    simulation_button = create_button(
        app,
        buttons_frame, 
        "🔍 Simulation (Dry-Run)", 
        lambda: simulate_processing(app)
    )
    simulation_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Einzelne Datei Button
    single_file_button = create_button(
        app,
        buttons_frame, 
        "📎 Einzelne Datei verarbeiten", 
        lambda: process_single_file(app)
    )
    single_file_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Konfiguration zurücksetzen Button
    reset_config_button = create_button(
        app,
        buttons_frame, 
        "🔄 Konfiguration zurücksetzen", 
        lambda: rebuild_config(app)
    )
    reset_config_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    # Elemente speichern
    control_elements["control_frame"] = control_frame
    control_elements["control_header"] = control_header
    control_elements["process_button"] = process_button
    control_elements["simulation_button"] = simulation_button
    control_elements["single_file_button"] = single_file_button
    control_elements["reset_config_button"] = reset_config_button
    
    return control_elements

def create_log_panel(app, parent, clear_callback):
    """
    Erstellt den Protokollbereich für Statusmeldungen und Aktivitätslogs.
    
    Der Protokollbereich zeigt alle Systemaktivitäten, Fehler, Warnungen und
    Erfolgsmeldungen an und ermöglicht dem Benutzer, den Verarbeitungsstatus
    zu überwachen und Probleme zu diagnostizieren.
    
    Args:
        app: Die GuiApp-Instanz mit den Farbdefinitionen und Schriftarten
        parent: Das übergeordnete Widget, in dem das Panel platziert wird
        clear_callback: Callback-Funktion zum Löschen des Protokolls
        
    Returns:
        dict: Dictionary mit allen erstellten Protokollelementen für späteren Zugriff
    """
    log_elements = {}
    
    # Frame für den Protokollbereich
    log_frame = tk.Frame(parent, bg=app.colors["background_medium"], padx=10, pady=10)
    log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Überschrift
    log_header = tk.Frame(log_frame, bg=app.colors["background_medium"])
    log_header.pack(fill=tk.X, padx=5, pady=5)
    
    log_title = tk.Label(
        log_header, 
        text="Aktivitätsprotokoll", 
        font=app.fonts["subheader"], 
        bg=app.colors["background_medium"], 
        fg=app.colors["text_primary"]
    )
    log_title.pack(side=tk.LEFT)
    
    # Löschen-Button
    clear_button = create_button(
        app, 
        log_header, 
        "Protokoll löschen", 
        clear_callback
    )
    clear_button.pack(side=tk.RIGHT, padx=5)
    
    # Textbereich mit Scrollbalken
    log_text = scrolledtext.ScrolledText(
        log_frame,
        wrap=tk.WORD,
        font=app.fonts["code"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"],
        height=15
    )
    log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    log_text.config(state=tk.DISABLED)  # Schreibgeschützt
    
    # Elemente speichern
    log_elements["log_frame"] = log_frame
    log_elements["log_title"] = log_title
    log_elements["log_text"] = log_text
    log_elements["clear_button"] = clear_button
    
    return log_elements

def create_status_bar(app, parent):
    """
    Erstellt die Statusleiste am unteren Rand der Anwendung.
    
    Die Statusleiste zeigt den aktuellen Betriebsstatus der Anwendung,
    Versionsinformationen und Copyright-Hinweise an. Sie dient als
    konstante Informationsquelle über den Zustand des Systems.
    
    Args:
        app: Die GuiApp-Instanz mit den Farbdefinitionen und Schriftarten
        parent: Das übergeordnete Widget, in dem die Statusleiste platziert wird
        
    Returns:
        dict: Dictionary mit allen erstellten Statuselementen für späteren Zugriff
    """
    status_elements = {}
    
    # Frame für die Statusleiste
    status_frame = tk.Frame(parent, bg=app.colors["background_dark"])
    status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
    
    # Status-Label
    status_label = tk.Label(
        status_frame,
        text="Bereit",
        font=app.fonts["small"],
        bg=app.colors["background_dark"],
        fg=app.colors["text_secondary"],
        anchor=tk.W
    )
    status_label.pack(side=tk.LEFT, padx=5)
    
    # Version und Copyright
    version_label = tk.Label(
        status_frame,
        text="MaehrDocs v2.0.0 | © 2025 René Mähr",
        font=app.fonts["small"],
        bg=app.colors["background_dark"],
        fg=app.colors["text_secondary"],
        anchor=tk.E
    )
    version_label.pack(side=tk.RIGHT, padx=5)
    
    # Elemente speichern
    status_elements["status_frame"] = status_frame
    status_elements["status_label"] = status_label
    status_elements["version_label"] = version_label
    
    return status_elements