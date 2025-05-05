"""
Toast-Benachrichtigungen für MaehrDocs
Implementiert temporäre, nicht-modale Benachrichtigungen, die am unteren
Bildschirmrand erscheinen und nach einer festgelegten Zeit automatisch verschwinden.

Diese Art von Benachrichtigungen werden häufig für subtile Hinweise und 
Rückmeldungen verwendet, ohne den Arbeitsfluss des Benutzers zu unterbrechen.
"""

import tkinter as tk
from maehrdocs.gui.gui_animations import fade_in, fade_out

class Toast:
    """
    Eine Toast-Benachrichtigung, die kurzzeitig am Bildschirmrand erscheint.
    
    Toast-Benachrichtigungen sind nicht-modale, temporäre Mitteilungen,
    die nicht mit Benutzereingaben interagieren und nach einer bestimmten
    Zeit automatisch verschwinden.
    """
    def __init__(self, app, message, duration=3000, position="bottom"):
        """
        Erstellt eine neue Toast-Benachrichtigung.
        
        Args:
            app: Die Hauptanwendung (GuiApp-Instanz)
            message (str): Die anzuzeigende Nachricht
            duration (int): Dauer in Millisekunden, wie lange der Toast angezeigt wird
            position (str): Position des Toasts: "bottom", "top" oder "center"
        """
        self.app = app
        self.message = message
        self.duration = duration
        self.position = position
        self.window = None
        
    def show(self):
        """
        Zeigt den Toast an.
        
        Erzeugt ein neues Fenster, positioniert es entsprechend der 
        Konfiguration, führt die Fade-In-Animation aus und startet einen
        Timer für das automatische Ausblenden.
        
        Returns:
            Das erzeugte Toast-Fenster-Objekt
        """
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
    Hilfsfunktion zum einfachen Anzeigen eines Toasts.
    
    Erstellt und zeigt eine Toast-Benachrichtigung an, ohne dass 
    der Aufrufer ein Toast-Objekt erstellen muss.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        message (str): Die anzuzeigende Nachricht
        duration (int): Dauer in Millisekunden, wie lange der Toast angezeigt wird
        position (str): Position des Toasts: "bottom", "top" oder "center"
        
    Returns:
        Das erzeugte Toast-Fenster-Objekt
    """
    toast = Toast(app, message, duration, position)
    return toast.show()