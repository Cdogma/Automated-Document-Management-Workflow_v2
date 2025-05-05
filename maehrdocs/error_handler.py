"""
Zentrale Fehlerbehandlung für MaehrDocs
Bietet eine einheitliche Schnittstelle zur Fehlerbehandlung und -protokollierung
"""

import logging
import traceback
import sys
from typing import Optional, Any, Callable, Type

class ErrorHandler:
    """
    Zentrale Klasse zur Fehlerbehandlung in MaehrDocs.
    
    Ermöglicht einheitliche Fehlerbehandlung für verschiedene Arten von Fehlern:
    - Erfasst Ausnahmen und leitet sie an das Messaging-System weiter
    - Bietet Kontext-Manager für fehleranfällige Operationen
    - Unterstützt hierarchische Fehlerbehandlung
    - Definiert klare Fehlercodes und -kategorien
    """
    
    def __init__(self, app=None):
        """
        Initialisiert den ErrorHandler
        
        Args:
            app: Die GuiApp-Instanz (optional)
        """
        self.app = app
        self.logger = logging.getLogger(__name__)
        # Fehlerklassen nach Schweregrad
        self.error_levels = {
            "critical": 50,  # Schwerwiegende Fehler, die sofortiges Beenden erfordern
            "error": 40,     # Standardfehler, die behandelt werden können
            "warning": 30,   # Warnungen, die den Betrieb nicht beeinträchtigen
            "info": 20       # Informationsmeldungen
        }
    
    def handle_exception(self, exception: Exception, context: str = None, level: str = "error") -> None:
        """
        Behandelt eine Exception und leitet sie entsprechend weiter
        
        Args:
            exception: Die aufgetretene Exception
            context: Kontextinformation zum Ort des Fehlers
            level: Schweregrad des Fehlers (critical, error, warning, info)
        """
        error_msg = str(exception)
        if context:
            error_msg = f"{context}: {error_msg}"
        
        # Stack-Trace für ausführlichere Protokollierung
        stack_trace = traceback.format_exc()
        
        # Logging
        log_level = self.error_levels.get(level, logging.ERROR)
        self.logger.log(log_level, error_msg)
        if log_level >= logging.ERROR:
            self.logger.debug(f"Stack-Trace:\n{stack_trace}")
        
        # Weiterleitung an das Messaging-System, wenn verfügbar
        if self.app and hasattr(self.app, 'messaging'):
            visual = level in ["critical", "error"]
            self.app.messaging.notify(
                message=error_msg, 
                level=level, 
                visual=visual,
                log=True
            )
            
            # Bei kritischen Fehlern Dialog anzeigen
            if level == "critical":
                self.app.messaging.dialog(
                    title="Kritischer Fehler",
                    message=f"{error_msg}\n\nDie Anwendung wird beendet.",
                    type="error"
                )
                # Anwendung beenden
                if hasattr(self.app, 'root'):
                    self.app.root.after(1000, self.app.root.destroy)
    
    def try_except(self, func: Callable, *args, context: str = None, 
                  level: str = "error", default_return: Any = None, **kwargs) -> Any:
        """
        Führt eine Funktion in einem try-except-Block aus
        
        Args:
            func: Die auszuführende Funktion
            *args: Positionsargumente für die Funktion
            context: Kontextinformation zum Ort des Fehlers
            level: Schweregrad des Fehlers
            default_return: Rückgabewert bei einem Fehler
            **kwargs: Schlüsselwortargumente für die Funktion
            
        Returns:
            Das Ergebnis der Funktion oder default_return bei einem Fehler
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(e, context=context or f"Fehler in {func.__name__}", level=level)
            return default_return
    
    def safe_operation(self, context: str = None, level: str = "error", default_return: Any = None):
        """
        Context-Manager für fehleranfällige Operationen
        
        Args:
            context: Kontextinformation zum Ort des Fehlers
            level: Schweregrad des Fehlers
            default_return: Rückgabewert bei einem Fehler
            
        Returns:
            Ein Context-Manager für try-except-Blöcke
        """
        class SafeOperationContext:
            def __init__(self, handler, ctx, lvl, default):
                self.handler = handler
                self.context = ctx
                self.level = lvl
                self.default = default
                self.result = default
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_val:
                    self.handler.handle_exception(exc_val, context=self.context, level=self.level)
                    return True  # Exception wurde behandelt
                return False
            
            def return_value(self, value):
                self.result = value
                return value
        
        return SafeOperationContext(self, context, level, default_return)