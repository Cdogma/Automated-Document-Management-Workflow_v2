# gui_forms.py
"""
Zentrale Formularkomponenten für MaehrDocs GUI
Koordiniert die verschiedenen Formularelemente und -funktionen
"""

import tkinter as tk
from .gui_form_fields import (
    create_text_field,
    create_folder_field,
    create_dropdown_field,
    create_spinbox_field,
    create_scale_field,
    create_checkbox_field
)

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
    input_field = None
    
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