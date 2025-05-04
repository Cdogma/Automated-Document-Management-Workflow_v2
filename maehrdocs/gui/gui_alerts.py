# gui_alerts.py
# Diese Datei importiert nun die aufgeteilten Module

from maehrdocs.gui.gui_notifications import show_notification
from maehrdocs.gui.gui_animations import animate_window, fade_in, fade_out

# Diese Datei dient jetzt nur noch als Vermittlungslayer für einfache Imports
# und um Abwärtskompatibilität zu gewährleisten

def show_success(app, message, timeout=5000):
    """Zeigt eine Erfolgs-Benachrichtigung an"""
    return show_notification(app, message, level="success", timeout=timeout)

def show_info(app, message, timeout=5000):
    """Zeigt eine Info-Benachrichtigung an"""
    return show_notification(app, message, level="info", timeout=timeout)

def show_warning(app, message, timeout=5000):
    """Zeigt eine Warnungs-Benachrichtigung an"""
    return show_notification(app, message, level="warning", timeout=timeout)

def show_error(app, message, timeout=5000):
    """Zeigt eine Fehler-Benachrichtigung an"""
    return show_notification(app, message, level="error", timeout=timeout)