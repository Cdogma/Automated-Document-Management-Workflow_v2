# toast.py (im GUI-Unterordner)

import tkinter as tk
from maehrdocs.gui.gui_animations import fade_in, fade_out

class Toast:
    """
    Eine Toast-Benachrichtigung, die kurzzeitig am unteren Bildschirmrand erscheint
    """
    def __init__(self, app, message, duration=3000, position="bottom"):
        """
        Erstellt eine neue Toast-Benachrichtigung
        
        Args:
            app: Die Hauptanwendung
            message: Die anzuzeigende Nachricht
            duration: Dauer in ms, wie lange der Toast angezeigt wird
            position: Position des Toasts (bottom, top, center)
        """
        self.app = app
        self.message = message
        self.duration = duration
        self.position = position
        self.window = None
        
    def show(self):
        """Zeigt den Toast an"""
        # Fenster erstellen
        self.window = tk.Toplevel(self.app)
        self.window.overrideredirect(True)
        
        # Styling
        self.window.configure(bg=self.app.colors["card_background"])
        
        # Label für die Nachricht
        label = tk.Label(
            self.window,
            text=self.message,
            font=self.app.fonts["normal"],
            bg=self.app.colors["card_background"],
            fg=self.app.colors["text_primary"],
            padx=20,
            pady=10
        )
        label.pack()
        
        # Größe des Fensters an den Inhalt anpassen
        self.window.update_idletasks()
        width = label.winfo_width() + 40
        height = label.winfo_height() + 20
        
        # Position berechnen
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        
        if self.position == "bottom":
            x = (screen_width - width) // 2
            y = screen_height - height - 40
        elif self.position == "top":
            x = (screen_width - width) // 2
            y = 40
        else:  # center
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Animation starten
        fade_in(self.window)
        
        # Timer zum Ausblenden
        self.window.after(self.duration, lambda: fade_out(self.window))
        
        return self.window

def show_toast(app, message, duration=3000, position="bottom"):
    """
    Zeigt einen Toast an und gibt das Fenster zurück
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        duration: Dauer in ms, wie lange der Toast angezeigt wird
        position: Position des Toasts (bottom, top, center)
    """
    toast = Toast(app, message, duration, position)
    return toast.show()