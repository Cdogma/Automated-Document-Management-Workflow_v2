# gui_alerts.py
"""
Dieses Modul dient als zentrale Schnittstelle für alle Benachrichtigungen und Dialoge
in der MaehrDocs Anwendung. Es stellt verschiedene Funktionen zur Verfügung,
um Benachrichtigungen und Dialoge anzuzeigen.

Die eigentliche Implementierung dieser Funktionen wurde in separate Module ausgelagert:
- notifications.py: Benachrichtigungsfenster
- animations.py: Animationseffekte
- toast.py: Toast-Nachrichten
- dialog.py: Standard-Dialoge
"""

# Importe aus den spezialisierten Modulen
from .gui_notifications import show_notification
from .gui_animations import animate_window, fade_in, fade_out
from .gui_toast import show_toast
from .gui_dialog import (
    show_confirm_dialog,
    show_info_dialog, 
    show_error_dialog, 
    show_warning_dialog
)

# Benachrichtigungsfunktionen
def show_success(app, message, timeout=5000):
    """
    Zeigt eine Erfolgs-Benachrichtigung an
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        timeout: Zeit in ms, nach der die Benachrichtigung automatisch verschwindet
        
    Returns:
        Das erstellte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="success", timeout=timeout)

def show_info(app, message, timeout=5000):
    """
    Zeigt eine Info-Benachrichtigung an
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        timeout: Zeit in ms, nach der die Benachrichtigung automatisch verschwindet
        
    Returns:
        Das erstellte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="info", timeout=timeout)

def show_warning(app, message, timeout=5000):
    """
    Zeigt eine Warnungs-Benachrichtigung an
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        timeout: Zeit in ms, nach der die Benachrichtigung automatisch verschwindet
        
    Returns:
        Das erstellte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="warning", timeout=timeout)

def show_error(app, message, timeout=5000):
    """
    Zeigt eine Fehler-Benachrichtigung an
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        timeout: Zeit in ms, nach der die Benachrichtigung automatisch verschwindet
        
    Returns:
        Das erstellte Benachrichtigungsfenster
    """
    return show_notification(app, message, level="error", timeout=timeout)

# Toast-Funktionen
def show_success_toast(app, message, duration=3000):
    """
    Zeigt einen Erfolgs-Toast an
    
    Args:
        app: Die Hauptanwendung
        message: Die anzuzeigende Nachricht
        duration: Dauer in ms, wie lange der Toast angezeigt wird
        
    Returns:
        Das erstellte Toast-Fenster
    """
    return show_toast(app, message, duration)

# Dialog-Wrapper-Funktionen
def confirm(app, title, message):
    """
    Zeigt einen Bestätigungsdialog an und gibt das Ergebnis zurück
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
        
    Returns:
        bool: True wenn der Benutzer bestätigt hat, sonst False
    """
    return show_confirm_dialog(app, title, message)

def info(app, title, message):
    """
    Zeigt einen Informationsdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    show_info_dialog(app, title, message)
    
def error(app, title, message):
    """
    Zeigt einen Fehlerdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    show_error_dialog(app, title, message)
    
def warning(app, title, message):
    """
    Zeigt einen Warnungsdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    show_warning_dialog(app, title, message)