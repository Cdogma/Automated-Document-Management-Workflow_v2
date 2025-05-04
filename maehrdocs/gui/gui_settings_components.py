# gui_settings_components.py
"""
Einstellungskomponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen von Einstellungssektionen und -tabs
"""

import tkinter as tk
from tkinter import ttk
from .gui_forms import create_form_field

def create_settings_section(app, parent, title, fields):
    """
    Erstellt einen Abschnitt in den Einstellungen
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel des Abschnitts
        fields: Liste der Felder
        
    Returns:
        tk.Frame: Der erstellte Abschnitt
    """
    section_frame = tk.Frame(
        parent, 
        bg=app.colors["card_background"], 
        padx=15, 
        pady=15
    )
    section_frame.pack(fill=tk.X, pady=10)
    
    section_header = tk.Label(
        section_frame, 
        text=title, 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    section_header.pack(anchor=tk.W, pady=(0, 10))
    
    # Felder erstellen
    for field in fields:
        field_frame = create_form_field(app, section_frame, field)
        field_frame.pack(fill=tk.X, pady=5)
    
    return section_frame

def create_settings_tab(app, notebook, title, sections):
    """
    Erstellt einen Tab in den Einstellungen
    
    Args:
        app: Instanz der GuiApp
        notebook: ttk.Notebook-Widget
        title: Titel des Tabs
        sections: Liste der Abschnitte (dict mit title und fields)
        
    Returns:
        tk.Frame: Der erstellte Tab-Frame
    """
    tab_frame = tk.Frame(notebook, bg=app.colors["background_medium"])
    notebook.add(tab_frame, text=title)
    
    # Scrollable Bereich erstellen
    canvas = tk.Canvas(
        tab_frame, 
        bg=app.colors["background_medium"],
        highlightthickness=0
    )
    scrollbar = tk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
    content_frame = tk.Frame(canvas, bg=app.colors["background_medium"])
    
    content_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Abschnitte erstellen
    for section in sections:
        create_settings_section(
            app, 
            content_frame, 
            section["title"], 
            section["fields"]
        )
    
    return tab_frame

def collect_settings_from_widget(app, widget):
    """
    Sammelt rekursiv alle Einstellungen aus Widgets
    
    Args:
        app: Instanz der GuiApp
        widget: Das zu durchsuchende Widget
    """
    # Prüfen, ob das Widget ein Feld mit einem Wert ist
    if hasattr(widget, 'field_key') and hasattr(widget, 'field_type'):
        # Wert entsprechend dem Feldtyp extrahieren
        value = None
        if widget.field_type == 'text' or widget.field_type == 'folder':
            value = widget.get()
        elif widget.field_type == 'dropdown':
            value = widget.get()
        elif widget.field_type == 'spinbox':
            try:
                value = int(widget.get())
            except ValueError:
                try:
                    value = float(widget.get())
                except ValueError:
                    value = widget.get()
        elif widget.field_type == 'scale':
            value = widget.get()
        elif widget.field_type == 'checkbox':
            value = widget.var.get()
            
        # Wert in der Konfiguration speichern
        keys = widget.field_key.split('.')
        current = app.config
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                current[key] = value
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
    
    # Rekursiv für alle Kind-Widgets aufrufen
    if hasattr(widget, 'winfo_children'):
        for child in widget.winfo_children():
            collect_settings_from_widget(app, child)

def search_and_update_field(widget, field_key, value):
    """
    Durchsucht ein Widget nach einem Feld und aktualisiert dessen Wert
    
    Args:
        widget: Das zu durchsuchende Widget
        field_key: Schlüssel des gesuchten Feldes
        value: Neuer Wert für das Feld
    """
    # Prüfen, ob das Widget das gesuchte Feld ist
    if hasattr(widget, 'field_key') and widget.field_key == field_key:
        widget.delete(0, tk.END)
        widget.insert(0, value)
        return True
    
    # Rekursiv für alle Kind-Widgets aufrufen
    if hasattr(widget, 'winfo_children'):
        for child in widget.winfo_children():
            if search_and_update_field(child, field_key, value):
                return True
    
    return False