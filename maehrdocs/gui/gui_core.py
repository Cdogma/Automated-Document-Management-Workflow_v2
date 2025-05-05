"""
Kernmodul der GUI-Anwendung für MaehrDocs
Enthält die Hauptklasse GuiApp, die alle anderen GUI-Komponenten koordiniert und steuert.

Dieses Modul dient als zentraler Einstiegspunkt für die grafische Benutzeroberfläche
und verwaltet die Interaktion zwischen den verschiedenen GUI-Komponenten, dem Backend
und der Anwendungskonfiguration.
"""

import tkinter as tk
import logging
from tkinter import messagebox

# Prüfe, ob TkinterDnD2 installiert ist für Drag & Drop Funktionalität
DRAG_DROP_ENABLED = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_ENABLED = True
except ImportError:
    pass

# Lokale Importe
from .gui_buttons import create_button
from .gui_dashboard import create_dashboard
from .gui_layout import (
    create_header,
    create_control_panel,
    create_log_panel,
    create_status_bar
)
from .gui_logger import setup_logging, log_message
from .gui_utils import (
    update_dashboard,
    check_for_new_documents,
    setup_drag_drop,
    clear_log
)
from .gui_settings import open_settings
from .gui_help import show_help
from .gui_actions import handle_drop

# Neuer Import für den ErrorHandler
from maehrdocs.error_handler import ErrorHandler

class GuiApp:
    """
    Hauptklasse für die MaehrDocs GUI-Anwendung.
    
    Diese Klasse dient als zentraler Koordinator für die gesamte GUI und:
    - Initialisiert das Hauptfenster und alle UI-Komponenten
    - Verwaltet das Farbschema und die Schriftarten
    - Stellt Hilfsfunktionen für andere GUI-Komponenten bereit
    - Koordiniert die Interaktion zwischen UI und Backend-Logik
    - Verwaltet regelmäßige Hintergrundaufgaben und Updates
    
    Die GuiApp-Instanz wird von allen UI-Komponenten als Referenz verwendet,
    um auf gemeinsame Ressourcen und Konfigurationen zuzugreifen.
    """
    def __init__(self, config_manager, document_processor):
        """
        Initialisiert die GUI mit Konfiguration und Dokumentenprozessor.
        
        Setzt das Farbschema, die Schriftarten und die grundlegenden
        Anwendungsreferenzen, ohne jedoch die eigentliche GUI zu erstellen.
        Die GUI-Erstellung erfolgt separat über setup_gui().
        
        Args:
            config_manager: Instanz des ConfigManager für Konfigurationszugriff
            document_processor: Instanz des DocumentProcessor für Dokumentenverarbeitung
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.document_processor = document_processor
        self.logger = logging.getLogger(__name__)
        
        # Zentrale Fehlerbehandlung initialisieren
        self.error_handler = ErrorHandler(self)
        
        # Farbschema definieren - modernes, dunkles Design
        self.colors = {
            "background_dark": "#0D1117",    # Tiefdunkles Blau-Schwarz
            "background_medium": "#161B22",  # Etwas hellerer Hintergrund
            "card_background": "#1F2937",    # Dunkles Grau-Blau für Panels
            "primary": "#3B82F6",            # Auffälliges, modernes Blau
            "accent": "#60A5FA",             # Helleres Blau für Hover
            "text_primary": "#F9FAFB",       # Fast weiß
            "text_secondary": "#9CA3AF",     # Mittelhelles Grau-Blau
            "success": "#10B981",            # Frisches Grün
            "warning": "#FBBF24",            # Sattes Gelb-Orange
            "error": "#EF4444"               # Kräftiges Rot
        }
        
        # Schriftarten definieren
        self.fonts = {
            "header": ("Segoe UI", 16, "bold"),
            "subheader": ("Segoe UI", 14, "bold"),
            "normal": ("Segoe UI", 12),
            "small": ("Segoe UI", 10),
            "code": ("Consolas", 11)
        }
        
        # GUI-Elemente
        self.root = None
        self.main_frame = None
        self.log_text = None
        self.status_label = None
        
        # Status und Tracking
        self.dashboard_elements = {}
        self.processing = False
        self.last_inbox_count = 0
        
        # Zentrale Messaging-Instanz (wird in setup_gui initialisiert)
        self.messaging = None
    
    def setup_gui(self):
        """
        Richtet die GUI ein und erstellt alle UI-Komponenten.
        
        Erstellt das Hauptfenster, initialisiert alle UI-Komponenten wie
        Header, Dashboard, Steuerungspanel und Protokollbereich, und
        startet die regelmäßigen Hintergrundaufgaben wie die Prüfung
        auf neue Dokumente.
        
        Returns:
            tk.Tk: Das Root-Fenster der Anwendung
        """
        # Mit ErrorHandler für sichere GUI-Initialisierung
        with self.error_handler.safe_operation(context="GUI-Initialisierung", level="critical"):
            # Initialisiere das Hauptfenster mit TkinterDnD wenn verfügbar, sonst normales Tk
            if DRAG_DROP_ENABLED:
                self.root = TkinterDnD.Tk()
            else:
                self.root = tk.Tk()
                self.logger.warning("TkinterDnD2 nicht installiert. Drag & Drop wird deaktiviert.")
            
            self.root.title("MaehrDocs - Automatisches Dokumentenmanagement")
            self.root.geometry("1700x1300")
            self.root.configure(bg=self.colors["background_dark"])
            
            # Hauptframe erstellen
            self.main_frame = tk.Frame(self.root, bg=self.colors["background_dark"])
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Header erstellen
            self.header_elements = create_header(
                self,
                self.main_frame,
                lambda: open_settings(self),
                lambda: show_help(self)
            )
            
            # Dashboard erstellen
            self.dashboard_elements = create_dashboard(
                self,
                self.main_frame,
                self.config
            )
            
            # Steuerungspanel erstellen
            self.control_elements = create_control_panel(self, self.main_frame)
            
            # Protokollbereich erstellen
            self.log_panel_elements = create_log_panel(
                self,
                self.main_frame,
                lambda: clear_log(self)
            )
            self.log_text = self.log_panel_elements["log_text"]
            
            # Statusleiste erstellen
            self.status_elements = create_status_bar(self, self.main_frame)
            self.status_label = self.status_elements["status_label"]
            
            # Logging einrichten
            setup_logging(self)
            
            # Messaging-System initialisieren (NACH der GUI-Erstellung)
            from .messaging import MessagingSystem
            self.messaging = MessagingSystem(self)
            
            # ErrorHandler aktualisieren, um das jetzt verfügbare Messaging-System zu nutzen
            self.error_handler.app = self
            
            # Dashboard aktualisieren
            update_dashboard(self)
            
            # Drag & Drop-Unterstützung hinzufügen (wenn verfügbar)
            if DRAG_DROP_ENABLED:
                setup_drag_drop(self, lambda e: handle_drop(self, e))
            else:
                log_message(self, "Drag & Drop-Funktionalität nicht verfügbar. Für die volle Funktionalität wird TkinterDnD2 empfohlen. "
                "Installieren Sie es mit 'pip install tkinterdnd2'.", 
                level="warning")
            
            # Prüfe periodisch auf neue Dokumente
            self.root.after(5000, lambda: check_for_new_documents(self))
            
            return self.root
    
    def open_folder(self, folder_suffix):
        """
        Öffnet den angegebenen Ordner im Datei-Explorer.
        
        Verwendet plattformspezifische Methoden, um den entsprechenden
        Ordner im Standarddateimanager des Betriebssystems zu öffnen.
        
        Args:
            folder_suffix: Ordnersuffix (z.B. "01_InboxDocs") für die Identifikation
        """
        # Mit ErrorHandler ausführen
        def _open_folder():
            from .gui_utils import open_folder_in_explorer
            open_folder_in_explorer(self, folder_suffix)
        
        self.error_handler.try_except(_open_folder, context="Ordner öffnen", level="warning")
    
    def browse_folder(self, key):
        """
        Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld.
        
        Zeigt einen Dateiauswahldialog und aktualisiert das entsprechende
        Einstellungsfeld mit dem ausgewählten Ordnerpfad.
        
        Args:
            key: Schlüssel des betroffenen Konfigurationsfeldes
        """
        # Mit ErrorHandler ausführen
        def _browse_folder():
            from .gui_settings import browse_folder
            browse_folder(self, key)
        
        self.error_handler.try_except(_browse_folder, context="Ordnerdialog", level="warning")
    
    def log(self, message, level="info"):
        """
        Fügt eine Nachricht zum Protokollbereich hinzu.
        
        Zentrale Methode zur Protokollierung von Nachrichten in der GUI
        mit entsprechender visueller Hervorhebung je nach Log-Level.
        
        Args:
            message: Die zu protokollierende Nachricht
            level: Log-Level (info, warning, error, success)
        """
        # Bei verfügbarem Messaging-System dieses verwenden
        if hasattr(self, 'messaging') and self.messaging:
            self.messaging.notify(message, level=level)
        else:
            # Fallback zur älteren Methode
            log_message(self, message, level)