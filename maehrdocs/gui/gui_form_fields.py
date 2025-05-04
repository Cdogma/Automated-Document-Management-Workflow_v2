# gui_form_fields.py
"""
Spezifische Formularfelder für MaehrDocs GUI
Enthält die verschiedenen Formularfelder und deren Erstellung
"""

import tkinter as tk
from tkinter import ttk
from .gui_buttons import create_button

def create_text_field(app, parent, value=""):
    """
    Erstellt ein Textfeld
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        value: Vorausgefüllter Wert (optional)
        
    Returns:
        tk.Entry: Das erstellte Textfeld
    """
    input_field = tk.Entry(
        parent, 
        font=app.fonts["normal"],
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        insertbackground=app.colors["text_primary"]
    )
    
    if isinstance(value, str):
        input_field.insert(0, value)
        
    return input_field

def create_folder_field(app, parent, key, value=""):
    """
    Erstellt ein Feld für die Ordnerauswahl mit Durchsuchen-Button
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        key: Konfigurationsschlüssel
        value: Vorausgefüllter Wert (optional)
        
    Returns:
        tk.Entry: Das erstellte Textfeld
    """
    input_frame = tk.Frame(parent, bg=app.colors["card_background"])
    input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    input_field = tk.Entry(
        input_frame, 
        font=app.fonts["normal"],
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        insertbackground=app.colors["text_primary"]
    )
    input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    if isinstance(value, str):
        input_field.insert(0, value)
    
    browse_btn = create_button(
        app,
        input_frame, 
        "...", 
        lambda: app.browse_folder(key)
    )
    browse_btn.pack(side=tk.LEFT, padx=5)
    
    return input_field

def create_dropdown_field(app, parent, options, value=None):
    """
    Erstellt ein Dropdown-Feld
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        options: Liste der Optionen
        value: Vorausgewählter Wert (optional)
        
    Returns:
        ttk.Combobox: Das erstellte Dropdown-Feld
    """
    input_field = ttk.Combobox(
        parent, 
        values=options,
        font=app.fonts["normal"]
    )
    
    if isinstance(value, str) and value in options:
        input_field.set(value)
    else:
        input_field.current(0)
        
    return input_field

def create_spinbox_field(app, parent, from_val, to_val, value=None):
    """
    Erstellt ein Spinbox-Feld
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        from_val: Minimalwert
        to_val: Maximalwert
        value: Vorausgefüllter Wert (optional)
        
    Returns:
        tk.Spinbox: Das erstellte Spinbox-Feld
    """
    input_field = tk.Spinbox(
        parent, 
        from_=from_val, 
        to=to_val,
        font=app.fonts["normal"],
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        buttonbackground=app.colors["primary"]
    )
    
    if isinstance(value, (int, float)):
        input_field.delete(0, tk.END)
        input_field.insert(0, str(value))
        
    return input_field

def create_scale_field(app, parent, from_val, to_val, resolution, value=None):
    """
    Erstellt ein Schieberegler-Feld
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        from_val: Minimalwert
        to_val: Maximalwert
        resolution: Auflösung
        value: Vorausgefüllter Wert (optional)
        
    Returns:
        tk.Scale: Das erstellte Schieberegler-Feld
    """
    input_field = tk.Scale(
        parent, 
        orient=tk.HORIZONTAL, 
        from_=from_val, 
        to=to_val, 
        resolution=resolution,
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"],
        highlightthickness=0,
        sliderrelief=tk.FLAT,
        troughcolor=app.colors["background_medium"]
    )
    
    if isinstance(value, (int, float)):
        input_field.set(value)
        
    return input_field

def create_checkbox_field(app, parent, value=False):
    """
    Erstellt ein Checkbox-Feld
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        value: Vorausgewählter Wert (optional)
        
    Returns:
        tk.Checkbutton: Das erstellte Checkbox-Feld
    """
    var = tk.BooleanVar(value=bool(value))
    
    input_field = tk.Checkbutton(
        parent, 
        variable=var,
        bg=app.colors["card_background"],
        activebackground=app.colors["card_background"],
        selectcolor=app.colors["background_dark"],
        fg=app.colors["text_primary"]
    )
    
    input_field.var = var
    
    return input_field