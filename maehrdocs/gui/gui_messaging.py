"""
Zentrales Messaging-System für MaehrDocs
Bietet eine einheitliche Schnittstelle für alle Arten von Benachrichtigungen, 
Dialogen und Feedback-Mechanismen in der Anwendung.
"""

class MessagingSystem:
    """
    Zentrale Klasse für alle Benachrichtigungen und Dialoge.
    
    Vereinheitlicht die verschiedenen Benachrichtigungsmechanismen:
    - Protokolleinträge
    - Popup-Benachrichtigungen
    - Toast-Meldungen
    - Dialogfenster
    - Statusleistenaktualisierungen
    
    Bietet eine konsistente API, unabhängig von der zugrundeliegenden Implementierung.
    """
    
    def __init__(self, app):
        """
        Initialisiert das Messaging-System mit der GuiApp-Instanz.
        
        Args:
            app: Die GuiApp-Instanz
        """
        self.app = app
    
    def notify(self, message, level="info", visual=True, log=True, toast=False, timeout=5000):
        """
        Zeigt eine Benachrichtigung an und/oder protokolliert sie.
        
        Args:
            message (str): Die Nachricht
            level (str): Log-Level (info, warning, error, success)
            visual (bool): Ob eine visuelle Benachrichtigung angezeigt werden soll
            log (bool): Ob die Nachricht protokolliert werden soll
            toast (bool): Ob eine Toast-Benachrichtigung verwendet werden soll
            timeout (int): Timeout für visuelle Benachrichtigungen in ms
            
        Returns:
            Das erzeugte Benachrichtigungsfenster oder None
        """
        # Logging
        if log:
            from .gui_logger import log_message
            log_message(self.app, message, level)
        
        # Visuelle Benachrichtigung
        if visual:
            if toast:
                from .gui_toast import show_toast
                return show_toast(self.app, message, duration=timeout)
            else:
                from .gui_notifications import show_notification
                return show_notification(self.app, message, level=level, timeout=timeout)
        
        return None
    
    def dialog(self, title, message, type="info"):
        """
        Zeigt einen Dialogfenster an.
        
        Args:
            title (str): Titel des Dialogs
            message (str): Nachricht des Dialogs
            type (str): Typ des Dialogs (info, warning, error, confirm)
            
        Returns:
            Bei confirm: bool (Bestätigung)
            Bei anderen Typen: None
        """
        from .gui_dialog import (
            show_info_dialog, 
            show_warning_dialog, 
            show_error_dialog, 
            show_confirm_dialog
        )
        
        if type == "confirm":
            return show_confirm_dialog(self.app, title, message)
        elif type == "warning":
            show_warning_dialog(self.app, title, message)
        elif type == "error":
            show_error_dialog(self.app, title, message)
        else:  # info
            show_info_dialog(self.app, title, message)
        
        return None
    
    def update_status(self, message):
        """
        Aktualisiert die Statusleiste.
        
        Args:
            message (str): Statusnachricht
        """
        if hasattr(self.app, 'status_label') and self.app.status_label:
            self.app.status_label.config(text=message)