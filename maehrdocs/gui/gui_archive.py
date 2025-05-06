"""
Archivierungsfunktionen für MaehrDocs
Enthält Funktionen zur Archivierung von Dokumenten in ZIP-Dateien
"""

import os
import zipfile
import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

def create_monthly_archive(app, year=None, month=None):
    """
    Erstellt ein monatliches Archiv aller Dateien im Ausgabeordner
    
    Args:
        app: Instanz der GuiApp
        year: Jahr für die Archivierung (Standard: aktuelles Jahr)
        month: Monat für die Archivierung (Standard: aktueller Monat)
        
    Returns:
        str: Pfad zur erstellten ZIP-Datei oder None bei Fehler
    """
    try:
        # Aktuelle Zeit bestimmen, wenn nicht angegeben
        current_date = datetime.now()
        year = year or current_date.year
        month = month or current_date.month
        
        # Zielordner für Archiv
        archive_dir = os.path.join(
            app.config.get('paths', {}).get('archive_dir', 'archives'),
            f"{year}"
        )
        
        # Sicherstellen, dass der Archivordner existiert
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        
        # Archivname generieren
        archive_name = f"{year}-{month:02d}_MaehrDocs_Archive.zip"
        archive_path = os.path.join(archive_dir, archive_name)
        
        # Ausgabeordner
        output_dir = app.config.get('paths', {}).get('output_dir', '')
        
        if not os.path.exists(output_dir):
            app.messaging.notify(f"Ausgabeordner nicht gefunden: {output_dir}", level="error")
            return None
        
        # Dateien des angegebenen Monats sammeln
        files_to_archive = []
        month_prefix = f"{year}-{month:02d}"
        
        for filename in os.listdir(output_dir):
            if filename.startswith(month_prefix) and filename.lower().endswith('.pdf'):
                files_to_archive.append(os.path.join(output_dir, filename))
        
        if not files_to_archive:
            app.messaging.notify(f"Keine Dateien für Archiv {month_prefix} gefunden", level="warning")
            return None
        
        # ZIP-Datei erstellen
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_archive:
                # Nur Dateiname ohne Pfad im Archiv speichern
                zipf.write(file, os.path.basename(file))
        
        app.messaging.notify(
            f"Monatsarchiv erstellt: {archive_name} mit {len(files_to_archive)} Dateien", 
            level="success"
        )
        
        return archive_path
        
    except Exception as e:
        app.messaging.notify(f"Fehler bei der Archivierung: {str(e)}", level="error")
        return None

def show_archive_dialog(app):
    """
    Zeigt einen Dialog zur manuellen Archivierung an
    
    Args:
        app: Instanz der GuiApp
    """
    archive_dialog = tk.Toplevel(app.root)
    archive_dialog.title("Archivierung")
    archive_dialog.geometry("400x300")
    archive_dialog.configure(bg=app.colors["background_dark"])
    
    # Frame für den Dialog
    dialog_frame = tk.Frame(
        archive_dialog, 
        bg=app.colors["background_medium"], 
        padx=15, 
        pady=15
    )
    dialog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Überschrift
    header = tk.Label(
        dialog_frame, 
        text="Monatsarchiv erstellen", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    header.pack(anchor=tk.W, pady=(0, 15))
    
    # Auswahlfelder für Jahr und Monat
    current_date = datetime.now()
    
    # Jahre (aktuelles Jahr und 5 Jahre zurück)
    year_frame = tk.Frame(dialog_frame, bg=app.colors["background_medium"])
    year_frame.pack(fill=tk.X, pady=5)
    
    year_label = tk.Label(
        year_frame, 
        text="Jahr:", 
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"],
        width=10,
        anchor=tk.W
    )
    year_label.pack(side=tk.LEFT)
    
    year_var = tk.StringVar(value=str(current_date.year))
    year_options = [str(current_date.year - i) for i in range(6)]
    year_dropdown = tk.OptionMenu(year_frame, year_var, *year_options)
    year_dropdown.configure(
        font=app.fonts["normal"],
        bg=app.colors["background_dark"],
        fg=app.colors["text_primary"],
        activebackground=app.colors["primary"],
        activeforeground=app.colors["text_primary"],
        highlightthickness=0
    )
    year_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Monate
    month_frame = tk.Frame(dialog_frame, bg=app.colors["background_medium"])
    month_frame.pack(fill=tk.X, pady=5)
    
    month_label = tk.Label(
        month_frame, 
        text="Monat:", 
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"],
        width=10,
        anchor=tk.W
    )
    month_label.pack(side=tk.LEFT)
    
    month_names = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    month_var = tk.StringVar(value=month_names[current_date.month - 1])
    month_dropdown = tk.OptionMenu(month_frame, month_var, *month_names)
    month_dropdown.configure(
        font=app.fonts["normal"],
        bg=app.colors["background_dark"],
        fg=app.colors["text_primary"],
        activebackground=app.colors["primary"],
        activeforeground=app.colors["text_primary"],
        highlightthickness=0
    )
    month_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Hinweistext
    info_text = tk.Label(
        dialog_frame,
        text="Diese Funktion erstellt ein ZIP-Archiv aller Dokumente\ndes ausgewählten Monats aus dem Ausgabeordner.",
        font=app.fonts["small"],
        fg=app.colors["text_secondary"],
        bg=app.colors["background_medium"],
        justify=tk.LEFT
    )
    info_text.pack(fill=tk.X, pady=10)
    
    # Buttons
    buttons_frame = tk.Frame(dialog_frame, bg=app.colors["background_medium"])
    buttons_frame.pack(fill=tk.X, pady=10)
    
    from .gui_buttons import create_button
    
    cancel_btn = create_button(
        app,
        buttons_frame, 
        "Abbrechen", 
        archive_dialog.destroy
    )
    cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_archive():
        try:
            year = int(year_var.get())
            month = month_names.index(month_var.get()) + 1
            
            # Archiv erstellen
            archive_path = create_monthly_archive(app, year, month)
            
            if archive_path:
                # Erfolgsmeldung
                messagebox.showinfo(
                    "Archivierung erfolgreich",
                    f"Das Archiv wurde erstellt:\n{archive_path}"
                )
                archive_dialog.destroy()
        except Exception as e:
            app.messaging.notify(f"Fehler bei der Archivierung: {str(e)}", level="error")
    
    create_btn = create_button(
        app,
        buttons_frame, 
        "Archiv erstellen", 
        create_archive,
        bg=app.colors["primary"]
    )
    create_btn.pack(side=tk.RIGHT, padx=5)