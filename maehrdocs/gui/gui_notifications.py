"""
Benachrichtigungssystem für MaehrDocs
Implementiert visuelle Benachrichtigungen und Popup-Fenster für Systemmeldungen.

Dieses Modul enthält die Kernfunktionalität für das Anzeigen von
Benachrichtigungen verschiedener Dringlichkeitsstufen (Info, Erfolg, Warnung, Fehler).
"""
import logging
import tkinter as tk
from .gui_animations import animate_window, fade_in, fade_out

def show_notification(app, message, level="info", timeout=5000):
    """
    Zeigt eine Benachrichtigung an.
    
    Erstellt ein temporäres, animiertes Popup-Fenster mit einer Meldung,
    das nach einer bestimmten Zeit automatisch verschwindet.
    
    Args:
        app: Die GuiApp-Instanz
        message (str): Die anzuzeigende Nachricht
        level (str): Dringlichkeitsstufe (info, success, warning, error)
        timeout (int): Anzeigedauer in Millisekunden
        
    Returns:
        tk.Toplevel: Das erzeugte Benachrichtigungsfenster
    """
    # Farben je nach Level
    colors = {
        "info": app.colors["primary"],
        "success": app.colors["success"],
        "warning": app.colors["warning"],
        "error": app.colors["error"]
    }
    
    # Icons je nach Level
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    # Fenster erstellen
    notif_window = tk.Toplevel(app.root)
    notif_window.overrideredirect(True)  # Kein Fensterrahmen
    notif_window.attributes("-topmost", True)  # Immer im Vordergrund
    
    # Styling
    bg_color = colors.get(level, app.colors["primary"])
    notif_window.configure(bg=bg_color)
    
    # Abstandhalter für Padding
    padx, pady = 15, 10
    
    # Frame für Inhalt
    content_frame = tk.Frame(notif_window, bg=bg_color, padx=padx, pady=pady)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Icon
    icon_label = tk.Label(
        content_frame,
        text=icons.get(level, "ℹ️"),
        font=("Segoe UI", 16),
        bg=bg_color,
        fg=app.colors["text_primary"]
    )
    icon_label.pack(side=tk.LEFT, padx=(0, 10))
    
    # Nachricht
    message_label = tk.Label(
        content_frame,
        text=message,
        font=app.fonts["normal"],
        bg=bg_color,
        fg=app.colors["text_primary"],
        wraplength=400,
        justify=tk.LEFT
    )
    message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Schließen-Button
    close_btn = tk.Label(
        content_frame,
        text="✖",
        font=("Segoe UI", 12),
        bg=bg_color,
        fg=app.colors["text_primary"],
        cursor="hand2"
    )
    close_btn.pack(side=tk.RIGHT, padx=(10, 0))
    close_btn.bind("<Button-1>", lambda e: fade_out(notif_window))
    
    # Position berechnen (rechts unten)
    notif_window.update_idletasks()
    width = notif_window.winfo_width()
    height = notif_window.winfo_height()
    
    screen_width = app.root.winfo_screenwidth()
    screen_height = app.root.winfo_screenheight()
    
    x = screen_width - width - 20
    y = screen_height - height - 40
    
    notif_window.geometry(f"+{x}+{y}")
    
    # Animation starten
    animate_window(notif_window)
    
    # Automatisch schließen nach timeout
    if timeout > 0:
        notif_window.after(timeout, lambda: fade_out(notif_window))
    
    # Auch in die Log-Datei schreiben
    if hasattr(app, 'logger'):
        log_level = {
            "info": logging.INFO,
            "success": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR
        }.get(level, logging.INFO)
        
        app.logger.log(log_level, message)
    
    return notif_window