"""
Layout-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen der Hauptlayout-Komponenten
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
    Erstellt den Kopfbereich der GUI
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        settings_callback: Callback für den Einstellungen-Button
        help_callback: Callback für den Hilfe-Button
        
    Returns:
        dict: Die erstellten Header-Elemente
    """
    header_elements = {}
    
    header_frame = tk.Frame(parent, bg=app.colors["background_dark"], pady=10)
    header_frame.pack(fill=tk.X)
    header_elements["frame"] = header_frame
    
    # Logo/Titel
    title_label = tk.Label(
        header_frame, 
        text="MaehrDocs", 
        font=("Segoe UI", 24, "bold"),
        fg=app.colors["primary"],
        bg=app.colors["background_dark"]
    )
    title_label.pack(side=tk.LEFT, padx=10)
    header_elements["title"] = title_label
    
    subtitle_label = tk.Label(
        header_frame, 
        text="Intelligentes Dokumentenmanagement",
        font=app.fonts["subheader"],
        fg=app.colors["text_secondary"],
        bg=app.colors["background_dark"]
    )
    subtitle_label.pack(side=tk.LEFT, padx=10)
    header_elements["subtitle"] = subtitle_label
    
    # Rechte Seite mit Optionsbuttons
    options_frame = tk.Frame(header_frame, bg=app.colors["background_dark"])
    options_frame.pack(side=tk.RIGHT)
    header_elements["options_frame"] = options_frame
    
    # Einstellungen-Button
    settings_btn = create_button(
        app,
        options_frame, 
        "⚙️ Einstellungen", 
        settings_callback
    )
    settings_btn.pack(side=tk.RIGHT, padx=5)
    header_elements["settings_button"] = settings_btn
    
    # Hilfe-Button
    help_btn = create_button(
        app,
        options_frame, 
        "❓ Hilfe", 
        help_callback
    )
    help_btn.pack(side=tk.RIGHT, padx=5)
    header_elements["help_button"] = help_btn
    
    return header_elements

def create_control_panel(app, parent):
    """
    Erstellt das Steuerungspanel
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        
    Returns:
        dict: Die erstellten Steuerungselemente
    """
    control_elements = {}
    
    control_frame = tk.Frame(
        parent, 
        bg=app.colors["background_medium"], 
        padx=15, 
        pady=15
    )
    control_frame.pack(fill=tk.X, pady=10)
    control_elements["frame"] = control_frame
    
    # Überschrift
    control_header = tk.Label(
        control_frame, 
        text="Steuerung", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    control_header.pack(anchor=tk.W, pady=(0, 10))
    control_elements["header"] = control_header
    
    # Buttons-Container
    buttons_frame = tk.Frame(control_frame, bg=app.colors["background_medium"])
    buttons_frame.pack(fill=tk.X)
    control_elements["buttons_frame"] = buttons_frame
    
    # Verarbeiten-Button
    process_btn = create_button(
        app,
        buttons_frame, 
        "🔄 Alle Dokumente verarbeiten", 
        lambda: process_documents(app),
        size="large"
    )
    process_btn.pack(side=tk.LEFT, padx=5)
    control_elements["process_button"] = process_btn
    
    # Simulation-Button
    simulate_btn = create_button(
        app,
        buttons_frame, 
        "🔍 Simulation (Dry-Run)", 
        lambda: simulate_processing(app),
        size="large"
    )
    simulate_btn.pack(side=tk.LEFT, padx=5)
    control_elements["simulate_button"] = simulate_btn
    
    # Datei-Button
    file_btn = create_button(
        app,
        buttons_frame, 
        "📄 Einzelne Datei verarbeiten", 
        lambda: process_single_file(app),
        size="large"
    )
    file_btn.pack(side=tk.LEFT, padx=5)
    control_elements["file_button"] = file_btn
    
    # Rechte Seite
    right_buttons = tk.Frame(buttons_frame, bg=app.colors["background_medium"])
    right_buttons.pack(side=tk.RIGHT)
    control_elements["right_buttons"] = right_buttons
    
    # Konfiguration-Button
    config_btn = create_button(
        app,
        right_buttons, 
        "🔧 Konfiguration zurücksetzen", 
        lambda: rebuild_config(app)
    )
    config_btn.pack(side=tk.RIGHT, padx=5)
    control_elements["config_button"] = config_btn
    
    return control_elements

def create_log_panel(app, parent, clear_callback):
    """
    Erstellt den Protokollbereich
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        clear_callback: Callback für den Protokoll-Löschen-Button
        
    Returns:
        dict: Die erstellten Protokollelemente
    """
    log_elements = {}
    
    log_frame = tk.Frame(
        parent, 
        bg=app.colors["background_medium"], 
        padx=15, 
        pady=15
    )
    log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    log_elements["frame"] = log_frame
    
    # Überschrift
    log_header = tk.Label(
        log_frame, 
        text="Protokoll", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    log_header.pack(anchor=tk.W, pady=(0, 10))
    log_elements["header"] = log_header
    
    # Protokollausgabe
    log_text = scrolledtext.ScrolledText(
        log_frame, 
        height=20,
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"],
        font=app.fonts["code"]
    )
    log_text.pack(fill=tk.BOTH, expand=True)
    log_text.config(state=tk.DISABLED)
    log_elements["log_text"] = log_text
    
    # Button zum Löschen des Protokolls
    clear_btn = create_button(
        app,
        log_frame, 
        "🧹 Protokoll löschen", 
        clear_callback
    )
    clear_btn.pack(anchor=tk.E, pady=10)
    log_elements["clear_button"] = clear_btn
    
    return log_elements

def create_status_bar(app, parent):
    """
    Erstellt die Statusleiste am unteren Rand
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        
    Returns:
        dict: Die erstellten Statuselemente
    """
    status_elements = {}
    
    status_frame = tk.Frame(
        parent, 
        bg=app.colors["background_dark"], 
        padx=10, 
        pady=5
    )
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    status_elements["frame"] = status_frame
    
    # Status-Label
    status_label = tk.Label(
        status_frame, 
        text="Bereit", 
        font=app.fonts["small"],
        fg=app.colors["text_secondary"],
        bg=app.colors["background_dark"]
    )
    status_label.pack(side=tk.LEFT)
    status_elements["status_label"] = status_label
    
    # Version und Copyright
    version_label = tk.Label(
        status_frame, 
        text="MaehrDocs v2.0 | © 2025", 
        font=app.fonts["small"],
        fg=app.colors["text_secondary"],
        bg=app.colors["background_dark"]
    )
    version_label.pack(side=tk.RIGHT)
    status_elements["version_label"] = version_label
    
    return status_elements