"""
Formular- und Einstellungskomponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen von Formularelementen und Einstellungssektionen
"""

import tkinter as tk
from tkinter import ttk
from .gui_buttons import create_button

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

def create_form_field(app, parent, field_config):
    """
    Erstellt ein einzelnes Formularfeld basierend auf der Konfiguration
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        field_config: Feldkonfiguration (dict)
        
    Returns:
        tk.Frame: Das Rahmen-Widget mit dem Feld
    """
    field_frame = tk.Frame(parent, bg=app.colors["card_background"])
    
    # Label erstellen
    label = tk.Label(
        field_frame, 
        text=field_config["label"] + ":", 
        font=app.fonts["normal"],
        width=25,
        anchor=tk.W,
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    label.pack(side=tk.LEFT)
    
    # Wert aus Konfiguration holen
    value = _get_config_value(app, field_config["key"])
    
    # Feld erstellen basierend auf dem Typ
    field_type = field_config["type"]
    
    if field_type == "text":
        input_field = create_text_field(app, field_frame, value)
        input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    elif field_type == "folder":
        input_field = create_folder_field(app, field_frame, field_config["key"], value)
        
    elif field_type == "dropdown":
        input_field = create_dropdown_field(app, field_frame, field_config["options"], value)
        input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    elif field_type == "spinbox":
        input_field = create_spinbox_field(
            app, field_frame, field_config["from"], field_config["to"], value
        )
        input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    elif field_type == "scale":
        input_field = create_scale_field(
            app, field_frame, 
            field_config["from"], field_config["to"], field_config["resolution"], 
            value
        )
        input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    elif field_type == "checkbox":
        input_field = create_checkbox_field(app, field_frame, bool(value))
        input_field.pack(side=tk.LEFT)
    
    # Speichere Feldtyp und -schlüssel für späteren Zugriff
    if input_field:
        input_field.field_type = field_type
        input_field.field_key = field_config["key"]
        
        # Speichere Feld im übergeordneten Frame
        field_id = field_config["key"].replace(".", "_")
        setattr(parent, field_id, input_field)
    
    return field_frame

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

def _get_config_value(app, key_path):
    """
    Holt einen Wert aus der Konfiguration
    
    Args:
        app: Instanz der GuiApp
        key_path: Pfad zum Konfigurationsschlüssel (mit Punkten getrennt)
        
    Returns:
        Der Wert aus der Konfiguration oder None
    """
    keys = key_path.split(".")
    value = app.config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
            
    return value