"""
Karten- und Container-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen von Statuskarten und anderen Container-Elementen
"""

import tkinter as tk
from .gui_buttons import create_button

def create_status_card(app, parent, title, folder_suffix, icon):
    """
    Erstellt eine Statuskarte für einen Ordner
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel der Karte
        folder_suffix: Ordnersuffix (für die Identifikation)
        icon: Icon-Text
        
    Returns:
        tk.Frame: Das erstellte Karten-Widget mit zusätzlichen Attributen
    """
    card = tk.Frame(parent, bg=app.colors["card_background"], padx=20, pady=15)
    
    header_frame = tk.Frame(card, bg=app.colors["card_background"])
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    icon_label = tk.Label(
        header_frame, 
        text=icon, 
        font=("Segoe UI", 18),
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    )
    icon_label.pack(side=tk.LEFT)
    
    title_label = tk.Label(
        header_frame, 
        text=title, 
        font=app.fonts["subheader"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    )
    title_label.pack(side=tk.LEFT, padx=5)
    
    # Dokumente Anzahl
    count_frame = tk.Frame(card, bg=app.colors["card_background"])
    count_frame.pack(fill=tk.X)
    
    count_label = tk.Label(
        count_frame, 
        text="Dokumente:", 
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_secondary"]
    )
    count_label.pack(side=tk.LEFT)
    
    count_value = tk.Label(
        count_frame, 
        text="Wird geladen...", 
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["primary"]
    )
    count_value.pack(side=tk.LEFT, padx=5)
    
    # Ordnerpfad
    path_frame = tk.Frame(card, bg=app.colors["card_background"], pady=5)
    path_frame.pack(fill=tk.X)
    
    path_label = tk.Label(
        path_frame, 
        text="Pfad:", 
        font=app.fonts["small"],
        bg=app.colors["card_background"],
        fg=app.colors["text_secondary"]
    )
    path_label.pack(side=tk.LEFT)
    
    path_value = tk.Label(
        path_frame, 
        text="...", 
        font=app.fonts["small"],
        bg=app.colors["card_background"],
        fg=app.colors["text_secondary"]
    )
    path_value.pack(side=tk.LEFT, padx=5)
    
    # Button zum Öffnen des Ordners
    open_btn = create_button(
        app,
        card, 
        "Ordner öffnen", 
        lambda f=folder_suffix: app.open_folder(f)
    )
    open_btn.pack(anchor=tk.W, pady=10)
    
    # Speichere Labels für späteren Zugriff
    card.count_value = count_value
    card.path_value = path_value
    card.folder_suffix = folder_suffix
    
    return card

def create_info_card(app, parent, title, content, icon=None, bg=None):
    """
    Erstellt eine Informationskarte
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel der Karte
        content: Inhalt der Karte (Text)
        icon: Icon-Text (optional)
        bg: Hintergrundfarbe (optional)
        
    Returns:
        tk.Frame: Das erstellte Karten-Widget
    """
    if bg is None:
        bg = app.colors["card_background"]
    
    card = tk.Frame(parent, bg=bg, padx=15, pady=15)
    
    # Header mit Icon
    header_frame = tk.Frame(card, bg=bg)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    if icon:
        icon_label = tk.Label(
            header_frame, 
            text=icon, 
            font=("Segoe UI", 18),
            bg=bg,
            fg=app.colors["text_primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 5))
    
    title_label = tk.Label(
        header_frame, 
        text=title, 
        font=app.fonts["subheader"],
        bg=bg,
        fg=app.colors["text_primary"]
    )
    title_label.pack(side=tk.LEFT)
    
    # Inhalt
    content_label = tk.Label(
        card, 
        text=content, 
        font=app.fonts["normal"],
        bg=bg,
        fg=app.colors["text_primary"],
        justify=tk.LEFT,
        wraplength=400  # Textumbruch für längere Texte
    )
    content_label.pack(fill=tk.X, pady=5)
    
    return card

def create_activity_card(app, parent, title):
    """
    Erstellt eine Aktivitätskarte mit einem Textfeld für Updates
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel der Karte
        
    Returns:
        tuple: (tk.Frame, tk.Text) Das Karten-Widget und das Textfeld für Updates
    """
    card = tk.Frame(
        parent, 
        bg=app.colors["card_background"], 
        padx=15, 
        pady=15
    )
    
    # Header
    header = tk.Label(
        card, 
        text=title, 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    header.pack(anchor=tk.W, pady=(0, 10))
    
    # Textfeld für Aktivitäten
    activity_text = tk.Text(
        card, 
        height=3, 
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        font=app.fonts["normal"],
        wrap=tk.WORD,
        state=tk.DISABLED
    )
    activity_text.pack(fill=tk.X)
    
    return card, activity_text

def create_section_frame(app, parent, title=None, padx=15, pady=15):
    """
    Erstellt einen Abschnittsrahmen mit optionalem Titel
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel des Abschnitts (optional)
        padx: Horizontales Padding
        pady: Vertikales Padding
        
    Returns:
        tk.Frame: Der erstellte Rahmen
    """
    frame = tk.Frame(
        parent, 
        bg=app.colors["card_background"], 
        padx=padx, 
        pady=pady
    )
    
    if title:
        header = tk.Label(
            frame, 
            text=title, 
            font=app.fonts["subheader"],
            fg=app.colors["text_primary"],
            bg=app.colors["card_background"]
        )
        header.pack(anchor=tk.W, pady=(0, 10))
    
    return frame