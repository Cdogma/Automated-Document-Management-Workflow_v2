"""
Benachrichtigungskomponenten für MaehrDocs
Zentrale Schnittstelle für Systembenachrichtigungen und Dialogfenster.

Dieses Modul dient als Kompatibilitätsschicht und leitet Aufrufe an die 
spezialisierten Module wie gui_notifications.py und gui_animations.py weiter,
um die Abwärtskompatibilität nach der Modularisierung zu gewährleisten.
"""

from maehrdocs.gui.gui_notifications import show_notification
from maehrdocs.gui.gui_animations import animate_window, fade_in, fade_out

def show_success(app, message, timeout=5000):
    """
    Zeigt eine Erfolgs-Benachrichtigung an.
    
    Erzeugt ein temporäres Popup-Fenster im erfolgreichen Stil (normalerweise grün),
    das nach einer bestimmten Zeit automatisch verschwindet.
    
    Args:
        app: Die GuiApp-Instanz
        message (str): Die anzuzeigende Nachricht
        timeout (int): Anzeigedauer in Millisekunden, bevor die Benachrichtigung verschwindet
        
    Returns:
        Das erzeugte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="success", timeout=timeout)

def show_info(app, message, timeout=5000):
    """
    Zeigt eine Informations-Benachrichtigung an.
    
    Erzeugt ein temporäres Popup-Fenster im Infostil (normalerweise blau),
    das nach einer bestimmten Zeit automatisch verschwindet.
    
    Args:
        app: Die GuiApp-Instanz
        message (str): Die anzuzeigende Nachricht
        timeout (int): Anzeigedauer in Millisekunden, bevor die Benachrichtigung verschwindet
        
    Returns:
        Das erzeugte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="info", timeout=timeout)

def show_warning(app, message, timeout=5000):
    """
    Zeigt eine Warnungs-Benachrichtigung an.
    
    Erzeugt ein temporäres Popup-Fenster im Warnungsstil (normalerweise gelb/orange),
    das nach einer bestimmten Zeit automatisch verschwindet.
    
    Args:
        app: Die GuiApp-Instanz
        message (str): Die anzuzeigende Nachricht
        timeout (int): Anzeigedauer in Millisekunden, bevor die Benachrichtigung verschwindet
        
    Returns:
        Das erzeugte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="warning", timeout=timeout)

def show_error(app, message, timeout=5000):
    """
    Zeigt eine Fehler-Benachrichtigung an.
    
    Erzeugt ein temporäres Popup-Fenster im Fehlerstil (normalerweise rot),
    das nach einer bestimmten Zeit automatisch verschwindet.
    
    Args:
        app: Die GuiApp-Instanz
        message (str): Die anzuzeigende Nachricht
        timeout (int): Anzeigedauer in Millisekunden, bevor die Benachrichtigung verschwindet
        
    Returns:
        Das erzeugte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="error", timeout=timeout)