"""
Button-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen verschiedener Arten von Buttons
"""

import tkinter as tk

def create_button(app, parent, text, command, size="normal", bg=None):
    """
    Erstellt einen styled Button
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        text: Button-Text
        command: Callback-Funktion
        size: Größe (normal oder large)
        bg: Hintergrundfarbe (optional)
        
    Returns:
        tk.Button: Der erstellte Button
    """
    if bg is None:
        bg = app.colors["primary"]
        
    if size == "large":
        button = tk.Button(
            parent, 
            text=text,
            font=app.fonts["normal"],
            bg=bg,
            fg=app.colors["text_primary"],
            activebackground=app.colors["accent"],
            activeforeground=app.colors["text_primary"],
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor="hand2",
            command=command
        )
    else:
        button = tk.Button(
            parent, 
            text=text,
            font=app.fonts["small"],
            bg=bg,
            fg=app.colors["text_primary"],
            activebackground=app.colors["accent"],
            activeforeground=app.colors["text_primary"],
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=command
        )
    
    return button

def create_icon_button(app, parent, icon_text, tooltip, command, size="normal", bg=None):
    """
    Erstellt einen Button mit Icon
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        icon_text: Unicode-Icon (z.B. "🔍")
        tooltip: Tooltip-Text
        command: Callback-Funktion
        size: Größe (normal oder large)
        bg: Hintergrundfarbe (optional)
        
    Returns:
        tk.Button: Der erstellte Button
    """
    if bg is None:
        bg = app.colors["primary"]
    
    # Icon-Schriftgröße basierend auf der Größe
    icon_size = 14 if size == "normal" else 18
    
    button = tk.Button(
        parent,
        text=icon_text,
        font=("Segoe UI", icon_size),
        bg=bg,
        fg=app.colors["text_primary"],
        activebackground=app.colors["accent"],
        activeforeground=app.colors["text_primary"],
        relief=tk.FLAT,
        padx=8 if size == "normal" else 12,
        pady=4 if size == "normal" else 8,
        cursor="hand2",
        command=command
    )
    
    # Tooltip
    _create_tooltip(button, tooltip)
    
    return button

def create_toggle_button(app, parent, text, command, is_active=False, size="normal"):
    """
    Erstellt einen Toggle-Button, der zwischen zwei Zuständen wechseln kann
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        text: Button-Text
        command: Callback-Funktion, die den aktuellen Zustand als Parameter erhält
        is_active: Anfangszustand (True = aktiv)
        size: Größe (normal oder large)
        
    Returns:
        tuple: (tk.Button, tk.BooleanVar) Der erstellte Button und die Variable für den Zustand
    """
    state_var = tk.BooleanVar(value=is_active)
    
    # Farben basierend auf dem Zustand
    active_bg = app.colors["success"]
    inactive_bg = app.colors["background_medium"]
    
    # Initial
    initial_bg = active_bg if is_active else inactive_bg
    
    button = create_button(
        app,
        parent,
        text,
        lambda: _toggle_button_state(app, button, state_var, command),
        size=size,
        bg=initial_bg
    )
    
    # Speichere Zustandsvariable und Farben als Attribute
    button.state_var = state_var
    button.active_bg = active_bg
    button.inactive_bg = inactive_bg
    
    return button, state_var

def _toggle_button_state(app, button, state_var, command):
    """
    Hilfsfunktion zum Umschalten des Button-Zustands
    
    Args:
        app: Instanz der GuiApp
        button: Der Toggle-Button
        state_var: Die BooleanVar für den Zustand
        command: Die Callback-Funktion
    """
    # Zustand umschalten
    new_state = not state_var.get()
    state_var.set(new_state)
    
    # Farbe ändern
    button.config(bg=button.active_bg if new_state else button.inactive_bg)
    
    # Callback aufrufen
    if command:
        command(new_state)

def _create_tooltip(widget, text):
    """
    Erstellt einen einfachen Tooltip für ein Widget
    
    Args:
        widget: Das Widget, für das der Tooltip erstellt werden soll
        text: Der Tooltip-Text
    """
    def enter(event):
        # Position des Tooltips
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Tooltip-Fenster erstellen
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Tooltip-Inhalt
        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=2
        )
        label.pack()
        
        # Referenz speichern
        widget.tooltip = tooltip
    
    def leave(event):
        # Tooltip zerstören
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            delattr(widget, "tooltip")
    
    # Event-Binding
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)