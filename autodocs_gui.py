import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
import threading
import os
import yaml
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

# Versuche TkinterDnD2 zu importieren (optional)
DRAG_DROP_ENABLED = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_ENABLED = True
except ImportError:
    # TkinterDnD2 ist nicht installiert - Drag & Drop wird deaktiviert
    pass

class AutoDocsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MaehrDocs - Automatisches Dokumentenmanagement")
        self.root.geometry("1700x1300")
        
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
        
        # Konfiguration laden
        self.config = self.load_config()
        
        # Haupthintergrund setzen
        self.root.configure(bg=self.colors["background_dark"])
        
        # Hauptframe erstellen
        self.main_frame = tk.Frame(self.root, bg=self.colors["background_dark"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_header()
        self.create_dashboard()
        self.create_control_panel()
        self.create_log_panel()
        self.create_status_bar()
        
        # Initialisiere die Anzeige
        self.update_dashboard()
        
        # Drag & Drop-Unterstützung hinzufügen (wenn verfügbar)
        if DRAG_DROP_ENABLED:
            self.setup_drag_drop()
        else:
            self.log("Drag & Drop nicht verfügbar. Installieren Sie TkinterDnD2 für diese Funktion.", level="warning")
            self.log("pip install tkinterdnd2", level="info")
        
        # Prüfe periodisch auf neue Dokumente
        self.root.after(5000, self.check_for_new_documents)

    def load_config(self):
        """Lädt die Konfigurationsdatei"""
        config_path = "autodocs_config.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            messagebox.showerror("Konfigurationsfehler", f"Fehler beim Laden der Konfiguration: {str(e)}")
            return {
                "paths": {
                    "input_dir": "C:\\Users\\renem\\OneDrive\\09_AutoDocs\\01_InboxDocs",
                    "output_dir": "C:\\Users\\renem\\OneDrive\\09_AutoDocs\\02_FinalDocs",
                    "trash_dir": "C:\\Users\\renem\\OneDrive\\09_AutoDocs\\03_TrashDocs"
                }
            }

    def create_header(self):
        """Erstellt den Kopfbereich der GUI"""
        header_frame = tk.Frame(self.main_frame, bg=self.colors["background_dark"], pady=10)
        header_frame.pack(fill=tk.X)
        
        # Logo/Titel
        title_label = tk.Label(header_frame, 
                              text="MaehrDocs", 
                              font=("Segoe UI", 24, "bold"),
                              fg=self.colors["primary"],
                              bg=self.colors["background_dark"])
        title_label.pack(side=tk.LEFT, padx=10)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Intelligentes Dokumentenmanagement",
                                 font=self.fonts["subheader"],
                                 fg=self.colors["text_secondary"],
                                 bg=self.colors["background_dark"])
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Rechte Seite mit Optionsbuttons
        options_frame = tk.Frame(header_frame, bg=self.colors["background_dark"])
        options_frame.pack(side=tk.RIGHT)
        
        # Einstellungen-Button
        settings_btn = self.create_button(options_frame, "⚙️ Einstellungen", self.open_settings)
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # Hilfe-Button
        help_btn = self.create_button(options_frame, "❓ Hilfe", self.show_help)
        help_btn.pack(side=tk.RIGHT, padx=5)

    def create_dashboard(self):
        """Erstellt das Dashboard mit Statusanzeigen"""
        dashboard_frame = tk.Frame(self.main_frame, bg=self.colors["background_medium"], padx=15, pady=15)
        dashboard_frame.pack(fill=tk.X, pady=10)
        
        # Überschrift
        dashboard_header = tk.Label(dashboard_frame, 
                                   text="Dashboard", 
                                   font=self.fonts["header"],
                                   fg=self.colors["text_primary"],
                                   bg=self.colors["background_medium"])
        dashboard_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Container für die Karten
        cards_frame = tk.Frame(dashboard_frame, bg=self.colors["background_medium"])
        cards_frame.pack(fill=tk.X)
        
        # Karten für Ordner-Status
        self.inbox_card = self.create_status_card(cards_frame, "Eingang", "01_InboxDocs", "📥")
        self.inbox_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.processed_card = self.create_status_card(cards_frame, "Verarbeitet", "02_FinalDocs", "✅")
        self.processed_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.trash_card = self.create_status_card(cards_frame, "Probleme", "03_TrashDocs", "🗑️")
        self.trash_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Letzte Aktivität
        activity_frame = tk.Frame(dashboard_frame, bg=self.colors["card_background"], padx=15, pady=15)
        activity_frame.pack(fill=tk.X, pady=10)
        
        activity_header = tk.Label(activity_frame, 
                                  text="Letzte Aktivität", 
                                  font=self.fonts["subheader"],
                                  fg=self.colors["text_primary"],
                                  bg=self.colors["card_background"])
        activity_header.pack(anchor=tk.W, pady=(0, 10))
        
        self.activity_list = tk.Text(activity_frame, 
                                    height=3, 
                                    bg=self.colors["background_medium"],
                                    fg=self.colors["text_primary"],
                                    font=self.fonts["normal"],
                                    wrap=tk.WORD,
                                    state=tk.DISABLED)
        self.activity_list.pack(fill=tk.X)

    def create_status_card(self, parent, title, folder_suffix, icon):
        """Erstellt eine Statuskarte für einen Ordner"""
        card = tk.Frame(parent, bg=self.colors["card_background"], padx=20, pady=15)
        
        header_frame = tk.Frame(card, bg=self.colors["card_background"])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(header_frame, 
                            text=icon, 
                            font=("Segoe UI", 18),
                            bg=self.colors["card_background"],
                            fg=self.colors["text_primary"])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, 
                             text=title, 
                             font=self.fonts["subheader"],
                             bg=self.colors["card_background"],
                             fg=self.colors["text_primary"])
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Dokumente Anzahl
        count_frame = tk.Frame(card, bg=self.colors["card_background"])
        count_frame.pack(fill=tk.X)
        
        count_label = tk.Label(count_frame, 
                             text="Dokumente:", 
                             font=self.fonts["normal"],
                             bg=self.colors["card_background"],
                             fg=self.colors["text_secondary"])
        count_label.pack(side=tk.LEFT)
        
        count_value = tk.Label(count_frame, 
                             text="Wird geladen...", 
                             font=self.fonts["normal"],
                             bg=self.colors["card_background"],
                             fg=self.colors["primary"])
        count_value.pack(side=tk.LEFT, padx=5)
        
        # Ordnerpfad
        path_frame = tk.Frame(card, bg=self.colors["card_background"], pady=5)
        path_frame.pack(fill=tk.X)
        
        path_label = tk.Label(path_frame, 
                            text="Pfad:", 
                            font=self.fonts["small"],
                            bg=self.colors["card_background"],
                            fg=self.colors["text_secondary"])
        path_label.pack(side=tk.LEFT)
        
        path_value = tk.Label(path_frame, 
                            text="...", 
                            font=self.fonts["small"],
                            bg=self.colors["card_background"],
                            fg=self.colors["text_secondary"])
        path_value.pack(side=tk.LEFT, padx=5)
        
        # Button zum Öffnen des Ordners
        open_btn = self.create_button(card, "Ordner öffnen", lambda f=folder_suffix: self.open_folder(f))
        open_btn.pack(anchor=tk.W, pady=10)
        
        # Speichere Labels für späteren Zugriff
        card.count_value = count_value
        card.path_value = path_value
        card.folder_suffix = folder_suffix
        
        return card

    def create_control_panel(self):
        """Erstellt das Steuerungspanel"""
        control_frame = tk.Frame(self.main_frame, bg=self.colors["background_medium"], padx=15, pady=15)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Überschrift
        control_header = tk.Label(control_frame, 
                                 text="Steuerung", 
                                 font=self.fonts["header"],
                                 fg=self.colors["text_primary"],
                                 bg=self.colors["background_medium"])
        control_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons-Container
        buttons_frame = tk.Frame(control_frame, bg=self.colors["background_medium"])
        buttons_frame.pack(fill=tk.X)
        
        # Verarbeiten-Button
        process_btn = self.create_button(buttons_frame, "🔄 Alle Dokumente verarbeiten", self.process_documents, size="large")
        process_btn.pack(side=tk.LEFT, padx=5)
        
        # Simulation-Button
        simulate_btn = self.create_button(buttons_frame, "🔍 Simulation (Dry-Run)", self.simulate_processing, size="large")
        simulate_btn.pack(side=tk.LEFT, padx=5)
        
        # Datei-Button
        file_btn = self.create_button(buttons_frame, "📄 Einzelne Datei verarbeiten", self.process_single_file, size="large")
        file_btn.pack(side=tk.LEFT, padx=5)
        
        # Rechte Seite
        right_buttons = tk.Frame(buttons_frame, bg=self.colors["background_medium"])
        right_buttons.pack(side=tk.RIGHT)
        
        # Konfiguration-Button
        config_btn = self.create_button(right_buttons, "🔧 Konfiguration zurücksetzen", self.rebuild_config)
        config_btn.pack(side=tk.RIGHT, padx=5)

    def create_log_panel(self):
        """Erstellt den Protokollbereich"""
        log_frame = tk.Frame(self.main_frame, bg=self.colors["background_medium"], padx=15, pady=15)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Überschrift
        log_header = tk.Label(log_frame, 
                             text="Protokoll", 
                             font=self.fonts["header"],
                             fg=self.colors["text_primary"],
                             bg=self.colors["background_medium"])
        log_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Protokollausgabe
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                               height=20,
                                               bg=self.colors["card_background"],
                                               fg=self.colors["text_primary"],
                                               font=self.fonts["code"])
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Button zum Löschen des Protokolls
        clear_btn = self.create_button(log_frame, "🧹 Protokoll löschen", self.clear_log)
        clear_btn.pack(anchor=tk.E, pady=10)

    def create_status_bar(self):
        """Erstellt die Statusleiste am unteren Rand"""
        status_frame = tk.Frame(self.main_frame, bg=self.colors["background_dark"], padx=10, pady=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, 
                                   text="Bereit", 
                                   font=self.fonts["small"],
                                   fg=self.colors["text_secondary"],
                                   bg=self.colors["background_dark"])
        self.status_label.pack(side=tk.LEFT)
        
        # Version und Copyright
        version_label = tk.Label(status_frame, 
                               text="MaehrDocs v2.0 | © 2025", 
                               font=self.fonts["small"],
                               fg=self.colors["text_secondary"],
                               bg=self.colors["background_dark"])
        version_label.pack(side=tk.RIGHT)

    def create_button(self, parent, text, command, size="normal"):
        """Erstellt einen styled Button"""
        if size == "large":
            button = tk.Button(parent, 
                             text=text,
                             font=self.fonts["normal"],
                             bg=self.colors["primary"],
                             fg=self.colors["text_primary"],
                             activebackground=self.colors["accent"],
                             activeforeground=self.colors["text_primary"],
                             relief=tk.FLAT,
                             padx=15,
                             pady=10,
                             cursor="hand2",
                             command=command)
        else:
            button = tk.Button(parent, 
                             text=text,
                             font=self.fonts["small"],
                             bg=self.colors["primary"],
                             fg=self.colors["text_primary"],
                             activebackground=self.colors["accent"],
                             activeforeground=self.colors["text_primary"],
                             relief=tk.FLAT,
                             padx=10,
                             pady=5,
                             cursor="hand2",
                             command=command)
        
        return button

    def update_dashboard(self):
        """Aktualisiert die Anzeigen im Dashboard"""
        try:
            # Inbox
            inbox_path = self.config["paths"]["input_dir"]
            inbox_count = len([f for f in os.listdir(inbox_path) if f.lower().endswith('.pdf')])
            self.inbox_card.count_value.config(text=str(inbox_count))
            self.inbox_card.path_value.config(text=inbox_path)
            
            # Processed
            processed_path = self.config["paths"]["output_dir"]
            processed_count = len([f for f in os.listdir(processed_path) if f.lower().endswith('.pdf')])
            self.processed_card.count_value.config(text=str(processed_count))
            self.processed_card.path_value.config(text=processed_path)
            
            # Trash
            trash_path = self.config["paths"]["trash_dir"]
            trash_count = len([f for f in os.listdir(trash_path) if f.lower().endswith('.pdf')])
            self.trash_card.count_value.config(text=str(trash_count))
            self.trash_card.path_value.config(text=trash_path)
            
            # Letzte Verarbeitungszeit aktualisieren
            self.status_label.config(text=f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.log(f"Fehler beim Aktualisieren des Dashboards: {str(e)}", level="error")

    def open_folder(self, folder_suffix):
        """Öffnet den angegebenen Ordner im Datei-Explorer"""
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

    def process_documents(self):
        """Verarbeitet alle Dokumente im Eingangsordner"""
        self.run_command_in_thread(["python", "autodocs_v2.py"])

    def simulate_processing(self):
        """Führt eine Simulation (Dry-Run) durch"""
        self.run_command_in_thread(["python", "autodocs_v2.py", "--dry-run"])

    def process_single_file(self):
        """Verarbeitet eine einzelne vom Benutzer ausgewählte Datei"""
        file_path = filedialog.askopenfilename(
            title="PDF-Datei auswählen",
            filetypes=[("PDF-Dateien", "*.pdf")]
        )
        
        if file_path:
            self.run_command_in_thread(["python", "autodocs_v2.py", "--single-file", file_path])

    def rebuild_config(self):
        """Setzt die Konfiguration zurück"""
        if messagebox.askyesno("Konfiguration zurücksetzen", 
                             "Möchten Sie die Konfiguration wirklich zurücksetzen? Alle benutzerdefinierten Einstellungen gehen verloren."):
            self.run_command_in_thread(["python", "autodocs_v2.py", "--rebuild-config"])

    def open_settings(self):
        """Öffnet das Einstellungsfenster"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("MaehrDocs - Einstellungen")
        settings_window.geometry("800x600")
        settings_window.configure(bg=self.colors["background_dark"])
        
        # Einstellungen aus der Konfigurationsdatei laden
        settings_frame = tk.Frame(settings_window, bg=self.colors["background_medium"], padx=20, pady=20)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Überschrift
        header = tk.Label(settings_frame, 
                        text="Einstellungen", 
                        font=self.fonts["header"],
                        fg=self.colors["text_primary"],
                        bg=self.colors["background_medium"])
        header.pack(anchor=tk.W, pady=(0, 20))
        
        # Notebook für Einstellungskategorien
        notebook = ttk.Notebook(settings_frame)
        
        # Allgemeine Einstellungen
        general_frame = tk.Frame(notebook, bg=self.colors["background_medium"])
        notebook.add(general_frame, text="Allgemein")
        
        # Pfade
        self.create_settings_section(general_frame, "Verzeichnisse", [
            {"label": "Eingangsordner", "key": "paths.input_dir", "type": "folder"},
            {"label": "Ausgabeordner", "key": "paths.output_dir", "type": "folder"},
            {"label": "Fehlerordner", "key": "paths.trash_dir", "type": "folder"}
        ])
        
        # OpenAI-Einstellungen
        openai_frame = tk.Frame(notebook, bg=self.colors["background_medium"])
        notebook.add(openai_frame, text="OpenAI")
        
        self.create_settings_section(openai_frame, "API-Einstellungen", [
            {"label": "Modell", "key": "openai.model", "type": "dropdown", 
             "options": ["gpt-3.5-turbo", "gpt-4o", "gpt-4-1106-preview"]},
            {"label": "Temperatur", "key": "openai.temperature", "type": "scale", "from": 0, "to": 1, "resolution": 0.1},
            {"label": "Max. Wiederholungsversuche", "key": "openai.max_retries", "type": "spinbox", "from": 1, "to": 10}
        ])
        
        # Dokumentverarbeitung
        docs_frame = tk.Frame(notebook, bg=self.colors["background_medium"])
        notebook.add(docs_frame, text="Dokumentverarbeitung")
        
        self.create_settings_section(docs_frame, "Verarbeitungsoptionen", [
            {"label": "Max. Dateigröße (MB)", "key": "document_processing.max_file_size_mb", "type": "spinbox", "from": 1, "to": 50},
            {"label": "Ähnlichkeitsschwelle für Duplikate", "key": "document_processing.similarity_threshold", "type": "scale", 
             "from": 0.5, "to": 1.0, "resolution": 0.05}
        ])
        
        # Dokumenttypen
        doctypes_frame = tk.Frame(docs_frame, bg=self.colors["card_background"], padx=15, pady=15)
        doctypes_frame.pack(fill=tk.X, pady=10)
        
        doctypes_header = tk.Label(doctypes_frame, 
                                  text="Gültige Dokumenttypen", 
                                  font=self.fonts["subheader"],
                                  fg=self.colors["text_primary"],
                                  bg=self.colors["card_background"])
        doctypes_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Textfeld für Dokumenttypen
        self.doctypes_text = tk.Text(doctypes_frame, 
                                   height=5, 
                                   bg=self.colors["background_medium"],
                                   fg=self.colors["text_primary"],
                                   font=self.fonts["normal"])
        self.doctypes_text.pack(fill=tk.X)
        
        # Aktuelle Dokumenttypen laden
        try:
            doctypes = self.config.get("document_processing", {}).get("valid_doc_types", [])
            self.doctypes_text.insert(tk.END, "\n".join(doctypes))
        except:
            pass
        
        # Benachrichtigungen
        notifications_frame = tk.Frame(notebook, bg=self.colors["background_medium"])
        notebook.add(notifications_frame, text="Benachrichtigungen")
        
        self.create_settings_section(notifications_frame, "Benachrichtigungsoptionen", [
            {"label": "Popup bei Duplikaten anzeigen", "key": "gui.show_duplicate_popup", "type": "checkbox"},
            {"label": "Benachrichtigung bei Verarbeitungsabschluss", "key": "gui.notify_on_completion", "type": "checkbox"},
            {"label": "Soundeffekte aktivieren", "key": "gui.enable_sounds", "type": "checkbox"}
        ])
        
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        buttons_frame = tk.Frame(settings_frame, bg=self.colors["background_medium"], pady=15)
        buttons_frame.pack(fill=tk.X)
        
        save_btn = self.create_button(buttons_frame, "Speichern", lambda: self.save_settings(settings_window))
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = self.create_button(buttons_frame, "Abbrechen", settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def create_settings_section(self, parent, title, fields):
        """Erstellt einen Abschnitt in den Einstellungen"""
        section_frame = tk.Frame(parent, bg=self.colors["card_background"], padx=15, pady=15)
        section_frame.pack(fill=tk.X, pady=10)
        
        section_header = tk.Label(section_frame, 
                                text=title, 
                                font=self.fonts["subheader"],
                                fg=self.colors["text_primary"],
                                bg=self.colors["card_background"])
        section_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Felder erstellen
        for field in fields:
            field_frame = tk.Frame(section_frame, bg=self.colors["card_background"], pady=5)
            field_frame.pack(fill=tk.X)
            
            label = tk.Label(field_frame, 
                           text=field["label"] + ":", 
                           font=self.fonts["normal"],
                           width=25,
                           anchor=tk.W,
                           fg=self.colors["text_primary"],
                           bg=self.colors["card_background"])
            label.pack(side=tk.LEFT)
            
            # Wert aus Konfiguration holen
            keys = field["key"].split(".")
            value = self.config
            for key in keys:
                value = value.get(key, {})
                
            # Verschiedene Feldtypen
            if field["type"] == "text":
                input_field = tk.Entry(field_frame, 
                                    font=self.fonts["normal"],
                                    bg=self.colors["background_medium"],
                                    fg=self.colors["text_primary"],
                                    insertbackground=self.colors["text_primary"])
                if isinstance(value, str):
                    input_field.insert(0, value)
                    
            elif field["type"] == "folder":
                input_frame = tk.Frame(field_frame, bg=self.colors["card_background"])
                input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                input_field = tk.Entry(input_frame, 
                                    font=self.fonts["normal"],
                                    bg=self.colors["background_medium"],
                                    fg=self.colors["text_primary"],
                                    insertbackground=self.colors["text_primary"])
                input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                if isinstance(value, str):
                    input_field.insert(0, value)
                
                browse_btn = self.create_button(input_frame), "...", lambda f=field["key"]: self.browse_folder(f)
                browse_btn.pack(side=tk.LEFT, padx=5)
                
            elif field["type"] == "dropdown":
                input_field = ttk.Combobox(field_frame, 
                                        values=field["options"],
                                        font=self.fonts["normal"])
                if isinstance(value, str) and value in field["options"]:
                    input_field.set(value)
                else:
                    input_field.current(0)
                    
            elif field["type"] == "spinbox":
                input_field = tk.Spinbox(field_frame, 
                                      from_=field["from"], 
                                      to=field["to"],
                                      font=self.fonts["normal"],
                                      bg=self.colors["background_medium"],
                                      fg=self.colors["text_primary"],
                                      buttonbackground=self.colors["primary"])
                if isinstance(value, (int, float)):
                    input_field.delete(0, tk.END)
                    input_field.insert(0, str(value))
                    
            elif field["type"] == "scale":
                input_field = tk.Scale(field_frame, 
                                     orient=tk.HORIZONTAL, 
                                     from_=field["from"], 
                                     to=field["to"], 
                                     resolution=field["resolution"],
                                     bg=self.colors["card_background"],
                                     fg=self.colors["text_primary"],
                                     highlightthickness=0,
                                     sliderrelief=tk.FLAT,
                                     troughcolor=self.colors["background_medium"])
                if isinstance(value, (int, float)):
                    input_field.set(value)
                    
            elif field["type"] == "checkbox":
                var = tk.BooleanVar(value=bool(value))
                input_field = tk.Checkbutton(field_frame, 
                                          variable=var,
                                          bg=self.colors["card_background"],
                                          activebackground=self.colors["card_background"],
                                          selectcolor=self.colors["background_dark"],
                                          fg=self.colors["text_primary"])
                input_field.var = var
            
            # Feldtyp speichern für späteren Zugriff
            input_field.field_type = field["type"]
            input_field.field_key = field["key"]
            
            if field["type"] != "folder":  # Für Ordnerfelder wurde das bereits gemacht
                input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
            # Speichern für späteren Zugriff
            section_frame.__dict__[field["key"].replace(".", "_")] = input_field

    def browse_folder(self, field_key):
        """Öffnet den Ordnerauswahldialog für ein Einstellungsfeld"""
        folder = filedialog.askdirectory(title="Ordner auswählen")
        if folder:
            # Finde das entsprechende Eingabefeld im aktuellen Fenster
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    for child in widget.winfo_children():
                        if hasattr(child, field_key.replace(".", "_")):
                            field = getattr(child, field_key.replace(".", "_"))
                            field.delete(0, tk.END)
                            field.insert(0, folder)
                            break

    def save_settings(self, settings_window):
        """Speichert die Einstellungen aus dem Einstellungsfenster"""
        try:
            # Alle Eingabefelder im Fenster finden
            for widget in settings_window.winfo_children():
                self.collect_settings_from_widget(widget)
            
            # Dokumenttypen speichern
            if hasattr(self, 'doctypes_text'):
                doctypes = self.doctypes_text.get(1.0, tk.END).strip().split('\n')
                if 'document_processing' not in self.config:
                    self.config['document_processing'] = {}
                self.config['document_processing']['valid_doc_types'] = doctypes
            
            # Konfiguration speichern
            with open("autodocs_config.yaml", 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            
            # Dashboard aktualisieren
            self.update_dashboard()
            
            # Fenster schließen
            settings_window.destroy()
            
            # Bestätigung anzeigen
            messagebox.showinfo("Einstellungen", "Die Einstellungen wurden erfolgreich gespeichert.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {str(e)}")

    def collect_settings_from_widget(self, widget):
        """Sammelt rekursiv alle Einstellungen aus Widgets"""
        # Prüfen, ob das Widget ein Feld mit einem Wert ist
        if hasattr(widget, 'field_key') and hasattr(widget, 'field_type'):
            # Wert entsprechend dem Feldtyp extrahieren
            value = None
            if widget.field_type == 'text' or widget.field_type == 'folder':
                value = widget.get()
            elif widget.field_type == 'dropdown':
                value = widget.get()
            elif widget.field_type == 'spinbox':
                try:
                    value = int(widget.get())
                except ValueError:
                    try:
                        value = float(widget.get())
                    except ValueError:
                        value = widget.get()
            elif widget.field_type == 'scale':
                value = widget.get()
            elif widget.field_type == 'checkbox':
                value = widget.var.get()
                
            # Wert in der Konfiguration speichern
            keys = widget.field_key.split('.')
            current = self.config
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    current[key] = value
                else:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
        
        # Rekursiv für alle Kind-Widgets aufrufen
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                self.collect_settings_from_widget(child)

    def show_help(self):
        """Zeigt ein Hilfefenster an"""
        help_window = tk.Toplevel(self.root)
        help_window.title("MaehrDocs - Hilfe")
        help_window.geometry("800x600")
        help_window.configure(bg=self.colors["background_dark"])
        
        help_frame = tk.Frame(help_window, bg=self.colors["background_medium"], padx=20, pady=20)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Überschrift
        header = tk.Label(help_frame, 
                        text="Hilfe und Dokumentation", 
                        font=self.fonts["header"],
                        fg=self.colors["text_primary"],
                        bg=self.colors["background_medium"])
        header.pack(anchor=tk.W, pady=(0, 20))
        
        # Hilfetext
        help_text = scrolledtext.ScrolledText(help_frame, 
                                           font=self.fonts["normal"],
                                           bg=self.colors["card_background"],
                                           fg=self.colors["text_primary"],
                                           padx=15,
                                           pady=15)
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
        close_btn = self.create_button(help_frame, "Schließen", help_window.destroy)
        close_btn.pack(anchor=tk.E, pady=10)

    def run_command_in_thread(self, command):
        """Führt einen Befehl in einem separaten Thread aus"""
        # Status aktualisieren
        self.status_label.config(text="Verarbeitung läuft...")
        
        # Log protokollieren
        self.log(f"Führe Befehl aus: {' '.join(command)}")
        
        # Thread starten
        thread = threading.Thread(target=self._run_command, args=(command,))
        thread.daemon = True
        thread.start()

    def _run_command(self, command):
        """Führt den eigentlichen Befehl aus und aktualisiert das Protokoll"""
        try:
            # Prozess starten und Ausgabe erfassen
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Ausgabe in Echtzeit verarbeiten
            for line in process.stdout:
                self.log(line.strip())
                
                # Auf Duplikate prüfen
                if "DUPLICATE DETECTED" in line:
                    self.handle_duplicate_from_log(line)
                
            # Auf Fehler prüfen
            for line in process.stderr:
                self.log(line.strip(), level="error")
                
            # Auf Prozessende warten
            process.wait()
            
            # Ergebnis anzeigen
            if process.returncode == 0:
                self.log("Verarbeitung erfolgreich abgeschlossen.", level="success")
                self.status_label.config(text="Bereit")
                
                # Dashboard aktualisieren
                self.root.after(1000, self.update_dashboard)
                
                # Benachrichtigung anzeigen wenn aktiviert
                if self.config.get("gui", {}).get("notify_on_completion", True):
                    messagebox.showinfo("Verarbeitung abgeschlossen", 
                                      "Die Dokumentenverarbeitung wurde erfolgreich abgeschlossen.")
            else:
                self.log(f"Verarbeitung mit Fehlercode {process.returncode} beendet.", level="error")
                self.status_label.config(text="Fehler aufgetreten")
                
        except Exception as e:
            self.log(f"Fehler bei der Ausführung: {str(e)}", level="error")
            self.status_label.config(text="Fehler aufgetreten")

    def handle_duplicate_from_log(self, log_line):
        """Verarbeitet Duplikatbenachrichtigungen aus der Protokollausgabe"""
        try:
            # Aus dem Log-Text die relevanten Informationen extrahieren
            # Format könnte sein: "DUPLICATE DETECTED: [Original: file1.pdf] [Duplicate: file2.pdf] [Similarity: 0.92]"
            if "[Original:" in log_line and "[Duplicate:" in log_line and "[Similarity:" in log_line:
                # Original-Datei extrahieren
                original_start = log_line.find("[Original:") + 10
                original_end = log_line.find("]", original_start)
                original_file = log_line[original_start:original_end].strip()
                
                # Duplikat-Datei extrahieren
                duplicate_start = log_line.find("[Duplicate:") + 11
                duplicate_end = log_line.find("]", duplicate_start)
                duplicate_file = log_line[duplicate_start:duplicate_end].strip()
                
                # Ähnlichkeitswert extrahieren
                similarity_start = log_line.find("[Similarity:") + 12
                similarity_end = log_line.find("]", similarity_start)
                similarity_str = log_line[similarity_start:similarity_end].strip()
                similarity_score = float(similarity_str) * 100  # In Prozent umwandeln
                
                # Popup anzeigen, wenn aktiviert
                if self.config.get("gui", {}).get("show_duplicate_popup", True):
                    self.show_duplicate_alert(original_file, duplicate_file, similarity_score)
        except Exception as e:
            self.log(f"Fehler bei der Verarbeitung der Duplikatbenachrichtigung: {str(e)}", level="error")

    def show_duplicate_alert(self, original_file, duplicate_file, similarity_score):
        """Zeigt einen Popup-Dialog an, wenn ein Duplikat gefunden wurde"""
        message = f"Duplikat gefunden!\n\nOriginaldatei: {original_file}\nDuplikatdatei: {duplicate_file}\nÄhnlichkeit: {similarity_score:.2f}%"
        
        # Fenster erstellen
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Duplikat erkannt")
        alert_window.geometry("600x400")
        alert_window.configure(bg=self.colors["background_dark"])
        alert_window.grab_set()  # Modal machen
        
        # Fensterinhalt
        alert_frame = tk.Frame(alert_window, bg=self.colors["background_medium"], padx=20, pady=20)
        alert_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon
        warning_label = tk.Label(alert_frame, 
                               text="⚠️", 
                               font=("Segoe UI", 48),
                               fg=self.colors["warning"],
                               bg=self.colors["background_medium"])
        warning_label.pack(pady=10)
        
        # Überschrift
        header = tk.Label(alert_frame, 
                        text="Duplikat erkannt", 
                        font=self.fonts["header"],
                        fg=self.colors["warning"],
                        bg=self.colors["background_medium"])
        header.pack(pady=10)
        
        # Nachricht
        message_frame = tk.Frame(alert_frame, bg=self.colors["card_background"], padx=15, pady=15)
        message_frame.pack(fill=tk.X, pady=10)
        
        # Originaldatei
        original_label = tk.Label(message_frame, 
                                text="Originaldatei:", 
                                font=self.fonts["normal"],
                                fg=self.colors["text_secondary"],
                                bg=self.colors["card_background"])
        original_label.pack(anchor=tk.W)
        
        original_value = tk.Label(message_frame, 
                                text=original_file, 
                                font=self.fonts["normal"],
                                fg=self.colors["text_primary"],
                                bg=self.colors["card_background"])
        original_value.pack(anchor=tk.W, padx=20, pady=(0, 10))
        
        # Duplikatdatei
        duplicate_label = tk.Label(message_frame, 
                                 text="Duplikatdatei:", 
                                 font=self.fonts["normal"],
                                 fg=self.colors["text_secondary"],
                                 bg=self.colors["card_background"])
        duplicate_label.pack(anchor=tk.W)
        
        duplicate_value = tk.Label(message_frame, 
                                 text=duplicate_file, 
                                 font=self.fonts["normal"],
                                 fg=self.colors["text_primary"],
                                 bg=self.colors["card_background"])
        duplicate_value.pack(anchor=tk.W, padx=20, pady=(0, 10))
        
        # Ähnlichkeit
        similarity_label = tk.Label(message_frame, 
                                  text="Ähnlichkeit:", 
                                  font=self.fonts["normal"],
                                  fg=self.colors["text_secondary"],
                                  bg=self.colors["card_background"])
        similarity_label.pack(anchor=tk.W)
        
        similarity_value = tk.Label(message_frame, 
                                  text=f"{similarity_score:.2f}%", 
                                  font=self.fonts["normal"],
                                  fg=self.colors["warning"],
                                  bg=self.colors["card_background"])
        similarity_value.pack(anchor=tk.W, padx=20)
        
        # Buttons
        buttons_frame = tk.Frame(alert_frame, bg=self.colors["background_medium"], pady=10)
        buttons_frame.pack(fill=tk.X)
        
        # Button zum Vergleichen der Dokumente
        compare_btn = self.create_button(buttons_frame, "Dokumente vergleichen", 
                                      lambda: self.compare_documents(original_file, duplicate_file))
        compare_btn.pack(side=tk.LEFT, padx=5)
        
        # Button zum Öffnen des Originals
        open_original_btn = self.create_button(buttons_frame, "Original öffnen", 
                                           lambda: self.open_document(original_file))
        open_original_btn.pack(side=tk.LEFT, padx=5)
        
        # Button zum Öffnen des Duplikats
        open_duplicate_btn = self.create_button(buttons_frame, "Duplikat öffnen", 
                                             lambda: self.open_document(duplicate_file))
        open_duplicate_btn.pack(side=tk.LEFT, padx=5)
        
        # Button zum Schließen
        close_btn = self.create_button(buttons_frame, "Schließen", alert_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Soundeffekt abspielen, wenn aktiviert
        if self.config.get("gui", {}).get("enable_sounds", False):
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except ImportError:
                # Nicht auf Windows oder winsound nicht verfügbar
                pass

    def compare_documents(self, original_file, duplicate_file):
        """Öffnet ein Fenster zum visuellen Vergleich zweier Dokumente"""
        compare_window = tk.Toplevel(self.root)
        compare_window.title(f"Dokumentenvergleich")
        compare_window.geometry("1200x800")
        compare_window.configure(bg=self.colors["background_dark"])
        
        compare_frame = tk.Frame(compare_window, bg=self.colors["background_medium"], padx=15, pady=15)
        compare_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Überschrift
        header = tk.Label(compare_frame, 
                        text="Dokumentenvergleich", 
                        font=self.fonts["header"],
                        fg=self.colors["text_primary"],
                        bg=self.colors["background_medium"])
        header.pack(anchor=tk.W, pady=(0, 15))
        
        # Zwei Spalten für die Dokumente
        docs_frame = tk.Frame(compare_frame, bg=self.colors["background_medium"])
        docs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Original
        left_frame = tk.Frame(docs_frame, bg=self.colors["card_background"], padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        left_header = tk.Label(left_frame, 
                             text=f"Original: {os.path.basename(original_file)}", 
                             font=self.fonts["subheader"],
                             fg=self.colors["text_primary"],
                             bg=self.colors["card_background"])
        left_header.pack(anchor=tk.W, pady=(0, 10))
        
        left_text = scrolledtext.ScrolledText(left_frame, 
                                           bg=self.colors["background_dark"],
                                           fg=self.colors["text_primary"],
                                           font=self.fonts["code"])
        left_text.pack(fill=tk.BOTH, expand=True)
        
        # Rechte Spalte - Duplikat
        right_frame = tk.Frame(docs_frame, bg=self.colors["card_background"], padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        right_header = tk.Label(right_frame, 
                              text=f"Duplikat: {os.path.basename(duplicate_file)}", 
                              font=self.fonts["subheader"],
                              fg=self.colors["text_primary"],
                              bg=self.colors["card_background"])
        right_header.pack(anchor=tk.W, pady=(0, 10))
        
        right_text = scrolledtext.ScrolledText(right_frame, 
                                            bg=self.colors["background_dark"],
                                            fg=self.colors["text_primary"],
                                            font=self.fonts["code"])
        right_text.pack(fill=tk.BOTH, expand=True)
        
        # Button zum Schließen
        close_btn = self.create_button(compare_frame, "Fenster schließen", compare_window.destroy)
        close_btn.pack(anchor=tk.E, pady=10)
        
        # Inhalt der Dokumente in einem Thread laden
        threading.Thread(target=self._load_document_contents, 
                       args=(original_file, duplicate_file, left_text, right_text)).start()

    def _load_document_contents(self, original_file, duplicate_file, left_text, right_text):
        """Lädt den Inhalt der Dokumente für den Vergleich"""
        try:
            # Original-Dokument laden
            self.load_document_content(original_file, left_text)
            
            # Duplikat-Dokument laden
            self.load_document_content(duplicate_file, right_text)
            
            # Unterschiede hervorheben
            self.highlight_differences(left_text, right_text)
            
        except Exception as e:
            self.log(f"Fehler beim Laden der Dokumenteninhalte: {str(e)}", level="error")

    def load_document_content(self, file_path, text_widget):
        """Lädt den Inhalt eines Dokuments in ein Text-Widget"""
        try:
            # PDF-Inhalt extrahieren
            import fitz  # PyMuPDF
            
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            
            # Vollständigen Pfad bestimmen
            if not os.path.isabs(file_path):
                # Prüfen in verschiedenen Ordnern
                for folder in [self.config["paths"]["input_dir"], 
                             self.config["paths"]["output_dir"], 
                             self.config["paths"]["trash_dir"]]:
                    potential_path = os.path.join(folder, file_path)
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
            
            if os.path.exists(file_path):
                doc = fitz.open(file_path)
                text = ""
                
                for page in doc:
                    text += page.get_text()
                
                text_widget.insert(tk.END, text)
                
                # PDF-Metadaten anzeigen
                text_widget.insert(tk.END, "\n\n--- Metadaten ---\n")
                for key, value in doc.metadata.items():
                    if value:
                        text_widget.insert(tk.END, f"{key}: {value}\n")
                        
                doc.close()
            else:
                text_widget.insert(tk.END, f"Datei nicht gefunden: {file_path}")
            
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"Fehler beim Laden der Datei: {str(e)}")
            text_widget.config(state=tk.DISABLED)

    def highlight_differences(self, left_text, right_text):
        """Hebt Unterschiede zwischen zwei Textfenstern hervor"""
        try:
            # Text aus beiden Widgets holen
            left_text.config(state=tk.NORMAL)
            right_text.config(state=tk.NORMAL)
            
            left_content = left_text.get(1.0, tk.END)
            right_content = right_text.get(1.0, tk.END)
            
            # Texte in Zeilen aufteilen
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()
            
            # Unterschiede finden (einfache Implementierung)
            import difflib
            differ = difflib.Differ()
            diff = list(differ.compare(left_lines, right_lines))
            
            # Text löschen und neu einfügen
            left_text.delete(1.0, tk.END)
            right_text.delete(1.0, tk.END)
            
            # Tags für die Formatierung erstellen
            left_text.tag_configure("difference", background=self.colors["error"], foreground="white")
            right_text.tag_configure("difference", background=self.colors["error"], foreground="white")
            
            # Unterschiedliche Zeilen hervorheben
            for line in diff:
                if line.startswith('  '):  # Gemeinsame Zeile
                    left_text.insert(tk.END, line[2:] + "\n")
                    right_text.insert(tk.END, line[2:] + "\n")
                elif line.startswith('- '):  # Nur links
                    left_text.insert(tk.END, line[2:] + "\n", "difference")
                elif line.startswith('+ '):  # Nur rechts
                    right_text.insert(tk.END, line[2:] + "\n", "difference")
            
            left_text.config(state=tk.DISABLED)
            right_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log(f"Fehler beim Hervorheben von Unterschieden: {str(e)}", level="error")

    def open_document(self, file_path):
        """Öffnet ein Dokument mit dem Standardprogramm"""
        try:
            # Vollständigen Pfad bestimmen
            if not os.path.isabs(file_path):
                # Prüfen in verschiedenen Ordnern
                for folder in [self.config["paths"]["input_dir"], 
                             self.config["paths"]["output_dir"], 
                             self.config["paths"]["trash_dir"]]:
                    potential_path = os.path.join(folder, file_path)
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
            
            if os.path.exists(file_path):
                # Plattformabhängiges Öffnen der Datei
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS oder Linux
                    subprocess.call(['open'
                                     if sys.platform == 'darwin' else 'xdg-open', file_path])
            else:
                messagebox.showerror("Fehler", f"Datei nicht gefunden: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Datei: {str(e)}")

    def log(self, message, level="info"):
        """Fügt eine Nachricht zum Protokoll hinzu"""
        if not hasattr(self, 'log_text'):
            return
            
        # Aktuelle Zeit
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Farbe je nach Level
        tag = None
        if level == "error":
            tag = "error"
            prefix = "❌ FEHLER"
        elif level == "warning":
            tag = "warning"
            prefix = "⚠️ WARNUNG"
        elif level == "success":
            tag = "success"
            prefix = "✅ ERFOLG"
        else:
            tag = "info"
            prefix = "ℹ️ INFO"
        
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
        if hasattr(self, 'activity_list'):
            self.activity_list.config(state=tk.NORMAL)
            self.activity_list.delete(1.0, tk.END)
            self.activity_list.insert(tk.END, message)
            self.activity_list.config(state=tk.DISABLED)

    def clear_log(self):
        """Löscht den Inhalt des Protokolls"""
        if messagebox.askyesno("Protokoll löschen", "Möchten Sie das Protokoll wirklich löschen?"):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self.log("Protokoll gelöscht.")

    def setup_drag_drop(self):
        """Richtet Drag & Drop-Funktionalität ein (erfordert tkinterdnd2)"""
        if DRAG_DROP_ENABLED:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.handle_drop)
        else:
            self.log("Drag & Drop nicht verfügbar. TkinterDnD2 ist nicht installiert.", level="warning")

    def handle_drop(self, event):
        """Verarbeitet gedropte Dateien"""
        if not DRAG_DROP_ENABLED:
            return
            
        # Liste der gedropten Dateien
        files = event.data
        
        # Windows-Pfade verarbeiten
        if os.name == 'nt':
            files = files.replace('{', '').replace('}', '')
            file_list = files.split()
        else:
            file_list = files.split()
        
        # PDF-Filter
        pdf_files = [f for f in file_list if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            messagebox.showinfo("Keine PDFs", "Es wurden keine PDF-Dateien zum Verarbeiten gefunden.")
            return
            
        # Bestätigung
        if len(pdf_files) == 1:
            answer = messagebox.askyesno("Datei verarbeiten", 
                                       f"Möchten Sie die Datei '{os.path.basename(pdf_files[0])}' verarbeiten?")
            if answer:
                self.run_command_in_thread(["python", "autodocs_v2.py", "--single-file", pdf_files[0]])
        else:
            # Bei mehreren Dateien fragen, ob man sie in den Eingangsordner kopieren möchte
            answer = messagebox.askyesno("Dateien verarbeiten", 
                                       f"Möchten Sie {len(pdf_files)} PDF-Dateien in den Eingangsordner kopieren?")
            if answer:
                self.copy_files_to_inbox(pdf_files)

    def copy_files_to_inbox(self, file_list):
        """Kopiert Dateien in den Eingangsordner"""
        inbox_dir = self.config["paths"]["input_dir"]
        
        # Fortschrittsfenster erstellen
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Dateien werden kopiert...")
        progress_window.geometry("400x200")
        progress_window.configure(bg=self.colors["background_dark"])
        progress_window.grab_set()  # Modal machen
        
        progress_frame = tk.Frame(progress_window, bg=self.colors["background_medium"], padx=20, pady=20)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Beschreibung
        label = tk.Label(progress_frame, 
                       text=f"Kopiere {len(file_list)} Dateien in den Eingangsordner...", 
                       font=self.fonts["normal"],
                       fg=self.colors["text_primary"],
                       bg=self.colors["background_medium"])
        label.pack(pady=10)
        
        # Fortschrittsbalken
        progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        progress.pack(pady=10)
        
        # Dateiname
        file_label = tk.Label(progress_frame, 
                            text="", 
                            font=self.fonts["small"],
                            fg=self.colors["text_secondary"],
                            bg=self.colors["background_medium"])
        file_label.pack(pady=5)
        
        # In einem Thread kopieren
        def copy_thread():
            success_count = 0
            error_count = 0
            
            for i, file_path in enumerate(file_list):
                try:
                    # UI aktualisieren
                    progress['value'] = (i / len(file_list)) * 100
                    file_name = os.path.basename(file_path)
                    file_label.config(text=f"Kopiere: {file_name}")
                    
                    # Datei kopieren
                    dest_path = os.path.join(inbox_dir, file_name)
                    shutil.copy2(file_path, dest_path)
                    
                    # Log
                    self.log(f"Datei kopiert: {file_name}")
                    success_count += 1
                    
                except Exception as e:
                    self.log(f"Fehler beim Kopieren von {os.path.basename(file_path)}: {str(e)}", level="error")
                    error_count += 1
                    
                # Kurze Pause für die UI
                time.sleep(0.1)
            
            # Fertig
            progress['value'] = 100
            file_label.config(text="Kopiervorgang abgeschlossen")
            
            # Abschlussmeldung
            if error_count == 0:
                messagebox.showinfo("Kopiervorgang abgeschlossen", 
                                  f"Alle {success_count} Dateien wurden erfolgreich in den Eingangsordner kopiert.")
            else:
                messagebox.showwarning("Kopiervorgang mit Fehlern abgeschlossen", 
                                     f"{success_count} Dateien erfolgreich kopiert, {error_count} Fehler aufgetreten.")
            
            # Fenster schließen
            progress_window.destroy()
            
            # Dashboard aktualisieren
            self.update_dashboard()
            
            # Fragen, ob die Dateien verarbeitet werden sollen
            if success_count > 0 and messagebox.askyesno("Dateien verarbeiten", 
                                                      f"Möchten Sie die {success_count} kopierten Dateien jetzt verarbeiten?"):
                self.process_documents()
        
        # Thread starten
        thread = threading.Thread(target=copy_thread)
        thread.daemon = True
        thread.start()

    def check_for_new_documents(self):
        """Prüft periodisch, ob neue Dokumente im Eingangsordner liegen"""
        try:
            inbox_dir = self.config["paths"]["input_dir"]
            pdf_count = len([f for f in os.listdir(inbox_dir) if f.lower().endswith('.pdf')])
            
            # Zustand speichern, falls noch nicht vorhanden
            if not hasattr(self, 'last_inbox_count'):
                self.last_inbox_count = pdf_count
            
            # Wenn neue Dokumente vorhanden sind, Nachricht anzeigen
            if pdf_count > self.last_inbox_count and pdf_count > 0:
                new_count = pdf_count - self.last_inbox_count
                self.log(f"{new_count} neue Dokumente im Eingangsordner entdeckt.", level="info")
                
                # Benachrichtigung anzeigen wenn aktiviert
                if self.config.get("gui", {}).get("notify_on_new_documents", True):
                    if messagebox.askyesno("Neue Dokumente", 
                                        f"{new_count} neue Dokumente im Eingangsordner entdeckt. Möchten Sie diese jetzt verarbeiten?"):
                        self.process_documents()
            
            # Zustand aktualisieren
            self.last_inbox_count = pdf_count
            
            # Dashboard aktualisieren, wenn sich etwas geändert hat
            if pdf_count != int(self.inbox_card.count_value.cget("text")):
                self.update_dashboard()
            
        except Exception as e:
            self.log(f"Fehler beim Prüfen auf neue Dokumente: {str(e)}", level="error")
        
        # In 5 Sekunden erneut prüfen
        self.root.after(5000, self.check_for_new_documents)


# GUI starten, wenn das Skript direkt ausgeführt wird
if __name__ == "__main__":
    # Bei Verwendung von TkinterDnD2
    if DRAG_DROP_ENABLED:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = AutoDocsGUI(root)
    root.mainloop()