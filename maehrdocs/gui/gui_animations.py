"""
Animations- und Effektkomponenten für MaehrDocs GUI
Enthält Funktionen für sanfte Übergänge und Animationen in der Benutzeroberfläche,
wie Fade-In/Fade-Out-Effekte für Fenster und andere visuelle Elemente.
"""

import tkinter as tk

def animate_window(window):
    """
    Animiert das Erscheinen eines Fensters mit Fade-In-Effekt.
    
    Das Fenster erscheint sanft, indem es von völliger Transparenz
    zu voller Sichtbarkeit übergeht. Dies erzeugt einen angenehmeren
    Benutzererfahrung als abruptes Erscheinen.
    
    Args:
        window: Das zu animierende Fenster (Toplevel)
        
    Returns:
        Das animierte Fenster-Objekt
    """
    # Start mit transparentem Fenster
    window.attributes("-alpha", 0)
    
    # Fade-In starten
    fade_in(window)
    
    return window

def fade_in(window, alpha=0):
    """
    Führt einen Fade-In-Effekt für ein Fenster durch.
    
    Erhöht schrittweise die Transparenz des Fensters von transparent
    zu vollständig sichtbar. Die Animation wird rekursiv mit zeitlicher
    Verzögerung durchgeführt.
    
    Args:
        window: Das Fenster
        alpha (float): Aktueller Alpha-Wert (Transparenz), Startwert
        
    Returns:
        Das Fenster-Objekt
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
    Führt einen Fade-Out-Effekt für ein Fenster durch.
    
    Verringert schrittweise die Transparenz des Fensters von vollständig
    sichtbar zu transparent. Nach Abschluss kann das Fenster optional
    zerstört werden.
    
    Args:
        window: Das Fenster
        alpha (float): Aktueller Alpha-Wert (Transparenz), Startwert
        destroy_window (bool): Ob das Fenster nach dem Fade-Out zerstört werden soll
        
    Returns:
        Das Fenster-Objekt oder None, wenn es zerstört wurde
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
        return None
    
    return window