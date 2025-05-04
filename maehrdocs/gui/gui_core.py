"""
Kernmodul der GUI-Anwendung für MaehrDocs
Enthält die Hauptklasse GuiApp, die alle anderen GUI-Komponenten koordiniert
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

class GuiApp:
    """
    Hauptklasse für die MaehrDocs GUI-Anwendung
    """
    def __init__(self, config_manager, document_processor):
        """
        Initialisiert die GUI mit Konfiguration und Dokumentenprozessor
        
        Args:
            config_manager: Instanz des ConfigManager
            document_processor: Instanz des DocumentProcessor
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.document_processor = document_processor
        self.logger = logging.getLogger(__name__)
        
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
    
    def setup_gui(self):
        """
        Richtet die GUI ein und gibt das Root-Fenster zurück
        
        Returns:
            tk.Tk: Das Root-Fenster der Anwendung
        """
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
        
        # Dashboard aktualisieren
        update_dashboard(self)
        
        # Drag & Drop-Unterstützung hinzufügen (wenn verfügbar)
        if DRAG_DROP_ENABLED:
            setup_drag_drop(self, lambda e: handle_drop(self, e))
        else:
            log_message(self, "Drag & Drop nicht verfügbar. Installieren Sie TkinterDnD2 für diese Funktion.", level="warning")
        
        # Prüfe periodisch auf neue Dokumente
        self.root.after(5000, lambda: check_for_new_documents(self))
        
        return self.root
    
    def open_folder(self, folder_suffix):
        """
        Öffnet den angegebenen Ordner im Datei-Explorer
        
        Args:
            folder_suffix: Ordnersuffix (für die Identifikation)
        """
        from .gui_utils import open_folder_in_explorer
        open_folder_in_explorer(self, folder_suffix)
    
    def browse_folder(self, key):
        """
        Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld
        
        Args:
            key: Schlüssel des betroffenen Feldes
        """
        from .gui_settings import browse_folder
        browse_folder(self, key)
    
    def log(self, message, level="info"):
        """
        Fügt eine Nachricht zum Protokollbereich hinzu
        
        Args:
            message: Die zu protokollierende Nachricht
            level: Log-Level (info, warning, error, success)
        """
        log_message(self, message, level)