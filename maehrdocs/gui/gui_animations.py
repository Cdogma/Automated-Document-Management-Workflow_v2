# animations.py
import tkinter as tk

def animate_window(window):
    """
    Animiert das Erscheinen eines Fensters mit Fade-In-Effekt
    
    Args:
        window: Das zu animierende Fenster (Toplevel)
    """
    # Start mit transparentem Fenster
    window.attributes("-alpha", 0)
    
    # Fade-In starten
    fade_in(window)
    
    return window

def fade_in(window, alpha=0):
    """
    Führt einen Fade-In-Effekt für ein Fenster durch
    
    Args:
        window: Das Fenster
        alpha: Aktueller Alpha-Wert (Transparenz)
    """
    # Alpha-Wert erhöhen
    alpha += 0.1
    
    # Prüfen, ob der maximale Wert erreicht ist
    if alpha <= 1:
        # Alpha-Wert setzen
        window.attributes("-alpha", alpha)
        
        # Nach 20ms erneut aufrufen
        window.after(20, lambda: fade_in(window, alpha))
    
    return window

def fade_out(window, alpha=1.0, destroy_window=True):
    """
    Führt einen Fade-Out-Effekt für ein Fenster durch
    
    Args:
        window: Das Fenster
        alpha: Aktueller Alpha-Wert (Transparenz)
        destroy_window: Ob das Fenster nach dem Fade-Out zerstört werden soll
    """
    # Alpha-Wert verringern
    alpha -= 0.1
    
    # Prüfen, ob der minimale Wert erreicht ist
    if alpha >= 0:
        # Alpha-Wert setzen
        window.attributes("-alpha", alpha)
        
        # Nach 20ms erneut aufrufen
        window.after(20, lambda: fade_out(window, alpha, destroy_window))
    elif destroy_window:
        # Fenster zerstören
        window.destroy()
    
    return window