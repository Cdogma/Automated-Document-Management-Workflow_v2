"""
Kernmodul der GUI-Anwendung für MaehrDocs
Enthält die Hauptklasse GuiApp, die alle anderen GUI-Komponenten koordiniert
"""

import tkinter as tk
import logging
import os
import threading
from tkinter import scrolledtext, messagebox
from datetime import datetime

# Lokale Importe
from .gui_components import create_button, create_status_card
from .gui_dashboard import create_dashboard
from .gui_settings import open_settings
from .gui_document_viewer import compare_documents, open_document
from .gui_handlers import (
    process_documents, 
    simulate_processing, 
    process_single_file, 
    rebuild_config,
    handle_drop
)

# Prüfe, ob TkinterDnD2 installiert ist für Drag & Drop Funktionalität
DRAG_DROP_ENABLED = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_ENABLED = True
except ImportError:
    pass

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
        self.processing = False
        
        # Status und Tracking
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
        self._create_header()
        
        # Dashboard erstellen
        self.dashboard_elements = create_dashboard(
            self,
            self.main_frame,
            self.config,
            self.open_folder
        )
        
        # Steuerungspanel erstellen
        self._create_control_panel()
        
        # Protokollbereich erstellen
        self._create_log_panel()
        
        # Statusleiste erstellen
        self._create_status_bar()
        
        # Dashboard aktualisieren
        self.update_dashboard()
        
        # Drag & Drop-Unterstützung hinzufügen (wenn verfügbar)
        if DRAG_DROP_ENABLED:
            self._setup_drag_drop()
        else:
            self.log("Drag & Drop nicht verfügbar. Installieren Sie TkinterDnD2 für diese Funktion.", level="warning")
        
        # Prüfe periodisch auf neue Dokumente
        self.root.after(5000, self._check_for_new_documents)
        
        return self.root
    
    def _create_header(self):
        """Erstellt den Kopfbereich der GUI"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors["background_dark"], pady=10)
        header_frame.pack(fill=tk.X)
        
        # Logo/Titel
        title_label = tk.Label(
            header_frame, 
            text="MaehrDocs", 
            font=("Segoe UI", 24, "bold"),
            fg=self.colors["primary"],
            bg=self.colors["background_dark"]
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Intelligentes Dokumentenmanagement",
            font=self.fonts["subheader"],
            fg=self.colors["text_secondary"],
            bg=self.colors["background_dark"]
        )
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Rechte Seite mit Optionsbuttons
        options_frame = tk.Frame(header_frame, bg=self.colors["background_dark"])
        options_frame.pack(side=tk.RIGHT)
        
        # Einstellungen-Button
        settings_btn = create_button(
            self,
            options_frame, 
            "⚙️ Einstellungen", 
            lambda: open_settings(self)
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # Hilfe-Button
        help_btn = create_button(
            self,
            options_frame, 
            "❓ Hilfe", 
            self._show_help
        )
        help_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_control_panel(self):
        """Erstellt das Steuerungspanel"""
        control_frame = tk.Frame(
            self.main_frame, 
            bg=self.colors["background_medium"], 
            padx=15, 
            pady=15
        )
        control_frame.pack(fill=tk.X, pady=10)
        
        # Überschrift
        control_header = tk.Label(
            control_frame, 
            text="Steuerung", 
            font=self.fonts["header"],
            fg=self.colors["text_primary"],
            bg=self.colors["background_medium"]
        )
        control_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons-Container
        buttons_frame = tk.Frame(control_frame, bg=self.colors["background_medium"])
        buttons_frame.pack(fill=tk.X)
        
        # Verarbeiten-Button
        process_btn = create_button(
            self,
            buttons_frame, 
            "🔄 Alle Dokumente verarbeiten", 
            lambda: process_documents(self),
            size="large"
        )
        process_btn.pack(side=tk.LEFT, padx=5)
        
        # Simulation-Button
        simulate_btn = create_button(
            self,
            buttons_frame, 
            "🔍 Simulation (Dry-Run)", 
            lambda: simulate_processing(self),
            size="large"
        )
        simulate_btn.pack(side=tk.LEFT, padx=5)
        
        # Datei-Button
        file_btn = create_button(
            self,
            buttons_frame, 
            "📄 Einzelne Datei verarbeiten", 
            lambda: process_single_file(self),
            size="large"
        )
        file_btn.pack(side=tk.LEFT, padx=5)
        
        # Rechte Seite
        right_buttons = tk.Frame(buttons_frame, bg=self.colors["background_medium"])
        right_buttons.pack(side=tk.RIGHT)
        
        # Konfiguration-Button
        config_btn = create_button(
            self,
            right_buttons, 
            "🔧 Konfiguration zurücksetzen", 
            lambda: rebuild_config(self)
        )
        config_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_log_panel(self):
        """Erstellt den Protokollbereich"""
        log_frame = tk.Frame(
            self.main_frame, 
            bg=self.colors["background_medium"], 
            padx=15, 
            pady=15
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Überschrift
        log_header = tk.Label(
            log_frame, 
            text="Protokoll", 
            font=self.fonts["header"],
            fg=self.colors["text_primary"],
            bg=self.colors["background_medium"]
        )
        log_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Protokollausgabe
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=20,
            bg=self.colors["card_background"],
            fg=self.colors["text_primary"],
            font=self.fonts["code"]
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Button zum Löschen des Protokolls
        clear_btn = create_button(
            self,
            log_frame, 
            "🧹 Protokoll löschen", 
            self._clear_log
        )
        clear_btn.pack(anchor=tk.E, pady=10)
    
    def _create_status_bar(self):
        """Erstellt die Statusleiste am unteren Rand"""
        status_frame = tk.Frame(
            self.main_frame, 
            bg=self.colors["background_dark"], 
            padx=10, 
            pady=5
        )
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame, 
            text="Bereit", 
            font=self.fonts["small"],
            fg=self.colors["text_secondary"],
            bg=self.colors["background_dark"]
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Version und Copyright
        version_label = tk.Label(
            status_frame, 
            text="MaehrDocs v2.0 | © 2025", 
            font=self.fonts["small"],
            fg=self.colors["text_secondary"],
            bg=self.colors["background_dark"]
        )
        version_label.pack(side=tk.RIGHT)
    
    def _setup_drag_drop(self):
        """Richtet Drag & Drop-Funktionalität ein (erfordert tkinterdnd2)"""
        if DRAG_DROP_ENABLED:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', lambda e: handle_drop(self, e))
        else:
            self.log("Drag & Drop nicht verfügbar. TkinterDnD2 ist nicht installiert.", level="warning")
    
    def _show_help(self):
        """Zeigt ein Hilfefenster an"""
        help_window = tk.Toplevel(self.root)
        help_window.title("MaehrDocs - Hilfe")
        help_window.geometry("800x600")
        help_window.configure(bg=self.colors["background_dark"])
        
        help_frame = tk.Frame(
            help_window, 
            bg=self.colors["background_medium"], 
            padx=20, 
            pady=20
        )
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Überschrift
        header = tk.Label(
            help_frame, 
            text="Hilfe und Dokumentation", 
            font=self.fonts["header"],
            fg=self.colors["text_primary"],
            bg=self.colors["background_medium"]
        )
        header.pack(anchor=tk.W, pady=(0, 20))
        
        # Hilfetext
        help_text = scrolledtext.ScrolledText(
            help_frame, 
            font=self.fonts["normal"],
            bg=self.colors["card_background"],
            fg=self.colors["text_primary"],
            padx=15,
            pady=15
        )
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Hilfetext einfügen
        help_content = """
# MaehrDocs - Benutzerhandbuch

## Überblick

MaehrDocs ist ein intelligentes Dokumentenmanagementsystem, das mit Hilfe von KI PDF-Dokumente automatisch analysiert, 
kategorisiert und umbenennt.

## Hauptfunktionen

1. **Automatische Verarbeitung** - PDFs werden aus dem Eingangsordner gelesen, analysiert und umbenannt
2. **KI-Analyse** - Verwendet OpenAI, um Dokumenttyp, Absender, Datum und andere Informationen zu extrahieren
3. **Duplikaterkennung** - Vermeidet doppelte Dokumente durch intelligente Ähnlichkeitserkennung
4. **Übersichtliches Dashboard** - Zeigt den Status aller Ordner und die letzten Aktivitäten an

## Schnellstart

1. Legen Sie PDF-Dokumente im Eingangsordner ab
2. Klicken Sie auf "Alle Dokumente verarbeiten"
3. Die verarbeiteten Dokumente finden Sie im Ausgabeordner

## Detaillierte Anleitung

### Neue Dokumente verarbeiten

Klicken Sie auf "Alle Dokumente verarbeiten", um alle PDFs im Eingangsordner zu verarbeiten. 
Alternativ können Sie "Simulation (Dry-Run)" wählen, um die Verarbeitung zu testen, ohne Änderungen vorzunehmen.

### Einzelne Datei verarbeiten

Klicken Sie auf "Einzelne Datei verarbeiten" und wählen Sie eine PDF-Datei aus, um nur diese zu verarbeiten.

### Duplikaterkennung

Das System erkennt Duplikate durch:
- Berechnung des Datei-Hashs
- Textähnlichkeitsanalyse
- Vergleich von Metadaten

Bei erkannten Duplikaten erscheint ein Hinweis im Protokoll und ein Popup-Dialog mit Details.

### Konfiguration anpassen

Klicken Sie auf "Einstellungen", um die Konfiguration anzupassen, z.B.:
- Verzeichnispfade
- OpenAI-Modell und Parameter
- Schwellenwert für Duplikaterkennung
- Gültige Dokumenttypen

## Fehlerbehebung

- **Fehler bei der Textextraktion**: Prüfen Sie, ob die PDF beschädigt oder passwortgeschützt ist
- **OpenAI-API-Fehler**: Überprüfen Sie Ihre Internetverbindung und den API-Schlüssel
- **Dokument wird nicht erkannt**: Passen Sie die gültigen Dokumenttypen in den Einstellungen an

## Tipps & Tricks

- Verwenden Sie Drag & Drop, um Dateien direkt in die Anwendung zu ziehen (erfordert TkinterDnD2)
- Halten Sie Ihren Eingangsordner aufgeräumt für bessere Übersicht
- Überprüfen Sie regelmäßig den Problemordner auf nicht verarbeitete Dokumente

Bei weiteren Fragen wenden Sie sich an support@maehrdocs.de
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        # Button zum Schließen
        close_btn = create_button(
            self,
            help_frame, 
            "Schließen", 
            help_window.destroy
        )
        close_btn.pack(anchor=tk.E, pady=10)
    
    def update_dashboard(self):
        """Aktualisiert die Anzeigen im Dashboard"""
        try:
            # Inbox
            inbox_path = self.config["paths"]["input_dir"]
            inbox_count = len([f for f in os.listdir(inbox_path) if f.lower().endswith('.pdf')])
            self.dashboard_elements["inbox_card"].count_value.config(text=str(inbox_count))
            self.dashboard_elements["inbox_card"].path_value.config(text=inbox_path)
            
            # Processed
            processed_path = self.config["paths"]["output_dir"]
            processed_count = len([f for f in os.listdir(processed_path) if f.lower().endswith('.pdf')])
            self.dashboard_elements["processed_card"].count_value.config(text=str(processed_count))
            self.dashboard_elements["processed_card"].path_value.config(text=processed_path)
            
            # Trash
            trash_path = self.config["paths"]["trash_dir"]
            trash_count = len([f for f in os.listdir(trash_path) if f.lower().endswith('.pdf')])
            self.dashboard_elements["trash_card"].count_value.config(text=str(trash_count))
            self.dashboard_elements["trash_card"].path_value.config(text=trash_path)
            
            # Letzte Verarbeitungszeit aktualisieren
            self.status_label.config(text=f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}")
            
            # Aktivitätsliste aktualisieren, wenn vorhanden
            if "activity_list" in self.dashboard_elements:
                self.dashboard_elements["activity_list"].config(state=tk.NORMAL)
                self.dashboard_elements["activity_list"].delete(1.0, tk.END)
                self.dashboard_elements["activity_list"].insert(tk.END, "Dashboard aktualisiert.")
                self.dashboard_elements["activity_list"].config(state=tk.DISABLED)
                
        except Exception as e:
            self.log(f"Fehler beim Aktualisieren des Dashboards: {str(e)}", level="error")
    
    def open_folder(self, folder_suffix):
        """Öffnet den angegebenen Ordner im Datei-Explorer"""
        import sys
        import subprocess
        
        try:
            if folder_suffix == "01_InboxDocs":
                folder_path = self.config["paths"]["input_dir"]
            elif folder_suffix == "02_FinalDocs":
                folder_path = self.config["paths"]["output_dir"]
            elif folder_suffix == "03_TrashDocs":
                folder_path = self.config["paths"]["trash_dir"]
            else:
                return
                
            # Plattformabhängiges Öffnen des Ordners
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS oder Linux
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', folder_path])
                
        except Exception as e:
            self.log(f"Fehler beim Öffnen des Ordners: {str(e)}", level="error")
    
    def log(self, message, level="info"):
        """Fügt eine Nachricht zum Protokollbereich hinzu"""
        if not hasattr(self, 'log_text') or self.log_text is None:
            return
            
        # Aktuelle Zeit
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Farbe je nach Level
        tag = None
        if level == "error":
            tag = "error"
            prefix = "❌ FEHLER"
            log_level = logging.ERROR
        elif level == "warning":
            tag = "warning"
            prefix = "⚠️ WARNUNG"
            log_level = logging.WARNING
        elif level == "success":
            tag = "success"
            prefix = "✅ ERFOLG"
            log_level = logging.INFO
        else:
            tag = "info"
            prefix = "ℹ️ INFO"
            log_level = logging.INFO
        
        # Log an Logger-Objekt senden
        self.logger.log(log_level, message)
        
        # Log-Eintrag formatieren
        log_entry = f"[{timestamp}] {prefix}: {message}\n"
        
        # Text-Widget aktualisieren
        self.log_text.config(state=tk.NORMAL)
        
        # Tags erstellen, falls noch nicht vorhanden
        if not hasattr(self.log_text, 'tags_created'):
            self.log_text.tag_configure("error", foreground=self.colors["error"])
            self.log_text.tag_configure("warning", foreground=self.colors["warning"])
            self.log_text.tag_configure("success", foreground=self.colors["success"])
            self.log_text.tag_configure("info", foreground=self.colors["text_primary"])
            self.log_text.tags_created = True
        
        # Text einfügen
        self.log_text.insert(tk.END, log_entry, tag)
        
        # Zum Ende scrollen
        self.log_text.see(tk.END)
        
        # Auf read-only setzen
        self.log_text.config(state=tk.DISABLED)
        
        # Letzte Aktivität aktualisieren
        if "activity_list" in self.dashboard_elements:
            self.dashboard_elements["activity_list"].config(state=tk.NORMAL)
            self.dashboard_elements["activity_list"].delete(1.0, tk.END)
            self.dashboard_elements["activity_list"].insert(tk.END, message)
            self.dashboard_elements["activity_list"].config(state=tk.DISABLED)
    
    def _clear_log(self):
        """Löscht den Inhalt des Protokolls"""
        if messagebox.askyesno("Protokoll löschen", "Möchten Sie das Protokoll wirklich löschen?"):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self.log("Protokoll gelöscht.")
    
    def _check_for_new_documents(self):
        """Prüft periodisch, ob neue Dokumente im Eingangsordner liegen"""
        try:
            inbox_dir = self.config["paths"]["input_dir"]
            pdf_count = len([f for f in os.listdir(inbox_dir) if f.lower().endswith('.pdf')])
            
            # Wenn neue Dokumente vorhanden sind, Nachricht anzeigen
            if pdf_count > self.last_inbox_count and pdf_count > 0:
                new_count = pdf_count - self.last_inbox_count
                self.log(f"{new_count} neue Dokumente im Eingangsordner entdeckt.", level="info")
                
                # Benachrichtigung anzeigen wenn aktiviert
                if self.config.get("gui", {}).get("notify_on_new_documents", True):
                    if messagebox.askyesno("Neue Dokumente", 
                                         f"{new_count} neue Dokumente im Eingangsordner entdeckt. Möchten Sie diese jetzt verarbeiten?"):
                        process_documents(self)
            
            # Zustand aktualisieren
            self.last_inbox_count = pdf_count
            
            # Dashboard aktualisieren, wenn sich etwas geändert hat
            if "inbox_card" in self.dashboard_elements:
                current_display = self.dashboard_elements["inbox_card"].count_value.cget("text")
                if pdf_count != int(current_display):
                    self.update_dashboard()
            
        except Exception as e:
            self.log(f"Fehler beim Prüfen auf neue Dokumente: {str(e)}", level="error")
        
        # In 5 Sekunden erneut prüfen
        self.root.after(5000, self._check_for_new_documents)