import tkinter as tk
import logging
import os
import threading
from tkinter import filedialog, scrolledtext, messagebox

# Prüfe, ob TkinterDnD2 installiert ist für Drag & Drop Funktionalität
DRAG_DROP_ENABLED = False
try:
    import tkinterdnd2
    DRAG_DROP_ENABLED = True
except ImportError:
    pass

class GuiManager:
    def __init__(self, config_manager, document_processor):
        """Initialisiert die GUI mit Konfiguration und Dokumentenprozessor"""
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.document_processor = document_processor
        self.logger = logging.getLogger(__name__)
        
        # Farbschema
        self.colors = {
            "background_dark": "#0D1117",
            "background_medium": "#161B22",
            "card_background": "#1F2937",
            "primary": "#3B82F6",
            "accent": "#60A5FA",
            "text_primary": "#F9FAFB",
            "text_secondary": "#9CA3AF",
            "success": "#10B981",
            "warning": "#FBBF24",
            "error": "#EF4444"
        }
        
        # GUI-Elemente
        self.root = None
        self.log_area = None
        self.status_labels = {}
        self.processing = False
    
    def setup_gui(self):
        """Richtet die GUI ein"""
        # Initialisiere das Hauptfenster mit TkinterDnD wenn verfügbar, sonst normales Tk
        if DRAG_DROP_ENABLED:
            self.root = tkinterdnd2.Tk()
        else:
            self.root = tk.Tk()
            self.logger.warning("TkinterDnD2 nicht installiert. Drag & Drop wird deaktiviert.")
        
        self.root.title("MaehrDocs - Dokumentenmanagementsystem")
        self.root.geometry("1700x1300")
        self.root.configure(bg=self.colors["background_dark"])
        
        # Haupt-Frame mit Padding
        main_frame = tk.Frame(self.root, bg=self.colors["background_dark"])
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = tk.Label(
            main_frame, 
            text="MaehrDocs", 
            font=("Helvetica", 24, "bold"), 
            bg=self.colors["background_dark"], 
            fg=self.colors["text_primary"]
        )
        title_label.pack(pady=(0, 20))
        
        # Oberer Bereich: Konfiguration und Status
        top_frame = tk.Frame(main_frame, bg=self.colors["background_dark"])
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Konfigurationsbereich
        self._create_config_section(top_frame)
        
        # Status-Bereich
        self._create_status_section(top_frame)
        
        # Mittlerer Bereich: Drag & Drop und Aktionsbuttons
        middle_frame = tk.Frame(main_frame, bg=self.colors["card_background"], bd=1, relief=tk.RAISED)
        middle_frame.pack(fill=tk.X, pady=(0, 20), ipady=20)
        
        # Drag & Drop Bereich
        self._create_drag_drop_area(middle_frame)
        
        # Aktionsbuttons
        self._create_action_buttons(middle_frame)
        
        # Unterer Bereich: Protokollbereich
        bottom_frame = tk.Frame(main_frame, bg=self.colors["background_dark"])
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Protokollbereich
        self._create_log_area(bottom_frame)
        
        # Drag & Drop Setup, wenn verfügbar
        if DRAG_DROP_ENABLED:
            self._setup_drag_drop()
        
        # Aktualisiere den Status
        self._update_status()
        
        return self.root
    
    def _create_config_section(self, parent):
        """Erstellt den Konfigurationsbereich"""
        config_frame = tk.LabelFrame(
            parent, 
            text="Konfiguration", 
            font=("Helvetica", 12), 
            bg=self.colors["card_background"], 
            fg=self.colors["text_primary"],
            padx=10, 
            pady=10
        )
        config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Konfigurationsfelder erstellen
        config_fields = [
            {"label": "Eingangsordner:", "key": "input_dir"},
            {"label": "Ausgabeordner:", "key": "output_dir"},
            {"label": "Papierkorb:", "key": "trash_dir"}
        ]
        
        for field in config_fields:
            field_frame = tk.Frame(config_frame, bg=self.colors["card_background"])
            field_frame.pack(fill=tk.X, pady=(0, 5))
            
            label = tk.Label(
                field_frame, 
                text=field["label"], 
                width=15, 
                anchor="w", 
                bg=self.colors["card_background"], 
                fg=self.colors["text_primary"]
            )
            label.pack(side=tk.LEFT)
            
            entry_var = tk.StringVar()
            entry_var.set(self.config["paths"][field["key"]])
            
            entry = tk.Entry(
                field_frame, 
                textvariable=entry_var, 
                width=50, 
                bg=self.colors["background_medium"], 
                fg=self.colors["text_primary"],
                insertbackground=self.colors["text_primary"]
            )
            entry.pack(side=tk.LEFT, padx=(5, 5))
            
            browse_btn = self._create_button(
                field_frame, 
                "...", 
                lambda f=field["key"]: self._browse_folder(f)
            )
    
    def _browse_folder(self, config_key):
        """Öffnet einen Dialog zur Ordnerauswahl"""
        folder = filedialog.askdirectory()
        if folder:
            self.config["paths"][config_key] = folder
            self.config_manager.save_config(self.config)
            self._update_status()
            self.log(f"Ordner für {config_key} wurde auf {folder} gesetzt.")
    
    def _create_status_section(self, parent):
        """Erstellt den Statusbereich"""
        status_frame = tk.LabelFrame(
            parent, 
            text="Status", 
            font=("Helvetica", 12), 
            bg=self.colors["card_background"], 
            fg=self.colors["text_primary"],
            padx=10, 
            pady=10
        )
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Status-Felder erstellen
        status_fields = [
            {"label": "Dokumente im Eingangsordner:", "key": "input_count"},
            {"label": "Verarbeitete Dokumente:", "key": "output_count"},
            {"label": "Dokumente im Papierkorb:", "key": "trash_count"}
        ]
        
        for field in status_fields:
            field_frame = tk.Frame(status_frame, bg=self.colors["card_background"])
            field_frame.pack(fill=tk.X, pady=(0, 5))
            
            label = tk.Label(
                field_frame, 
                text=field["label"], 
                width=25, 
                anchor="w", 
                bg=self.colors["card_background"], 
                fg=self.colors["text_primary"]
            )
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                field_frame, 
                text="0", 
                width=10, 
                anchor="w", 
                bg=self.colors["card_background"], 
                fg=self.colors["success"]
            )
            value_label.pack(side=tk.LEFT)
            
            self.status_labels[field["key"]] = value_label
    
    def _create_drag_drop_area(self, parent):
        """Erstellt den Drag & Drop Bereich"""
        drop_frame = tk.Frame(parent, bg=self.colors["background_medium"], height=100)
        drop_frame.pack(fill=tk.X, padx=20, pady=10)
        
        drop_label = tk.Label(
            drop_frame, 
            text="Ziehe PDF-Dateien hierher oder klicke auf 'Datei auswählen'", 
            bg=self.colors["background_medium"], 
            fg=self.colors["text_primary"],
            height=5
        )
        drop_label.pack(fill=tk.BOTH, expand=True)
        
        self.drop_area = drop_frame
    
    def _create_action_buttons(self, parent):
        """Erstellt die Aktionsbuttons"""
        button_frame = tk.Frame(parent, bg=self.colors["card_background"])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Dateien auswählen
        select_btn = self._create_button(
            button_frame, 
            "Datei auswählen", 
            self._select_files
        )
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Alle verarbeiten
        process_all_btn = self._create_button(
            button_frame, 
            "Alle verarbeiten", 
            lambda: self._process_all_documents(False)
        )
        process_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Simulation
        simulation_btn = self._create_button(
            button_frame, 
            "Simulation", 
            lambda: self._process_all_documents(True)
        )
        simulation_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Konfiguration zurücksetzen
        reset_config_btn = self._create_button(
            button_frame, 
            "Konfiguration zurücksetzen", 
            self._reset_config,
            bg=self.colors["warning"]
        )
        reset_config_btn.pack(side=tk.RIGHT)
    
    def _create_log_area(self, parent):
        """Erstellt den Protokollbereich"""
        log_frame = tk.LabelFrame(
            parent, 
            text="Protokoll", 
            font=("Helvetica", 12), 
            bg=self.colors["card_background"], 
            fg=self.colors["text_primary"],
            padx=10, 
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, 
            bg=self.colors["background_medium"], 
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            height=15
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)
    
    def _setup_drag_drop(self):
        """Richtet Drag & Drop ein, wenn verfügbar"""
        if DRAG_DROP_ENABLED:
            self.drop_area.drop_target_register('DND_Files')
            self.drop_area.dnd_bind('<<Drop>>', self._handle_drop)
    
    def _handle_drop(self, event):
        """Verarbeitet gedropte Dateien"""
        if not DRAG_DROP_ENABLED:
            return
            
        files = event.data
        if files:
            # Bereinige die Dateiliste (unter Windows enthält sie geschweifte Klammern)
            if files[0] == '{' and files[-1] == '}':
                files = files[1:-1]
            
            # Teile mehrere Dateien auf
            file_list = files.split('} {')
            
            # Verarbeite jede Datei
            for file in file_list:
                if file.lower().endswith('.pdf'):
                    self._process_single_file(file)
                else:
                    self.log(f"Ignoriere Nicht-PDF-Datei: {file}", level=logging.WARNING)
    
    def _select_files(self):
        """Öffnet einen Dialog zur Dateiauswahl"""
        files = filedialog.askopenfilenames(filetypes=[("PDF Dateien", "*.pdf")])
        if files:
            for file in files:
                self._process_single_file(file)
    
    def _process_single_file(self, file_path):
        """Verarbeitet eine einzelne Datei"""
        if self.processing:
            self.log("Es läuft bereits eine Verarbeitung. Bitte warten.", level=logging.WARNING)
            return
            
        self.log(f"Verarbeite Datei: {file_path}")
        
        # Starte die Verarbeitung in einem separaten Thread
        threading.Thread(target=self._process_file_thread, args=(file_path,)).start()
    
    def _process_file_thread(self, file_path):
        """Verarbeitet eine Datei in einem separaten Thread"""
        self.processing = True
        try:
            result = self.document_processor.process_document(file_path)
            
            if result:
                self.log(f"Dokument verarbeitet: {file_path} → {result['new_filename']}")
                if result['is_duplicate']:
                    self.log(f"Duplikat erkannt: Ähnlich zu {result['duplicate_path']}", level=logging.WARNING)
            else:
                self.log(f"Fehler bei der Verarbeitung von {file_path}", level=logging.ERROR)
                
        except Exception as e:
            self.log(f"Fehler: {str(e)}", level=logging.ERROR)
        finally:
            self.processing = False
            self._update_status()
    
    def _process_all_documents(self, dry_run=False):
        """Verarbeitet alle Dokumente im Eingangsordner"""
        if self.processing:
            self.log("Es läuft bereits eine Verarbeitung. Bitte warten.", level=logging.WARNING)
            return
            
        mode = "Simulation" if dry_run else "Verarbeitung"
        self.log(f"{mode} aller Dokumente im Eingangsordner gestartet...")
        
        # Starte die Verarbeitung in einem separaten Thread
        threading.Thread(target=self._process_all_thread, args=(dry_run,)).start()
    
    def _process_all_thread(self, dry_run):
        """Verarbeitet alle Dokumente in einem separaten Thread"""
        self.processing = True
        try:
            results = self.document_processor.process_all_documents(dry_run=dry_run)
            
            if results:
                self.log(f"{len(results)} Dokumente verarbeitet.")
                
                # Zeige Details für jedes Dokument
                for result in results:
                    filename = os.path.basename(result['original_file'])
                    self.log(f"Dokument: {filename} → {result['new_filename']}")
                    
                    if result['is_duplicate']:
                        self.log(f"  Duplikat erkannt: Ähnlich zu {os.path.basename(result['duplicate_path'])}", 
                                level=logging.WARNING)
            else:
                self.log("Keine Dokumente verarbeitet oder Fehler aufgetreten.", level=logging.WARNING)
                
        except Exception as e:
            self.log(f"Fehler: {str(e)}", level=logging.ERROR)
        finally:
            self.processing = False
            self._update_status()
    
    def _reset_config(self):
        """Setzt die Konfiguration zurück"""
        if messagebox.askyesno("Bestätigung", "Möchten Sie die Konfiguration wirklich zurücksetzen?"):
            self.config = self.config_manager.create_default_config()
            self.log("Konfiguration zurückgesetzt.")
            self._update_status()
    
    def _update_status(self):
        """Aktualisiert die Statusanzeige"""
        try:
            # Zähle Dateien in den Ordnern
            input_count = len([f for f in os.listdir(self.config["paths"]["input_dir"]) 
                            if f.lower().endswith('.pdf')])
            output_count = len([f for f in os.listdir(self.config["paths"]["output_dir"]) 
                             if f.lower().endswith('.pdf')])
            trash_count = len([f for f in os.listdir(self.config["paths"]["trash_dir"]) 
                            if f.lower().endswith('.pdf')])
            
            # Aktualisiere die Statuslabels
            self.status_labels["input_count"].config(text=str(input_count))
            self.status_labels["output_count"].config(text=str(output_count))
            self.status_labels["trash_count"].config(text=str(trash_count))
            
        except Exception as e:
            self.log(f"Fehler beim Aktualisieren des Status: {str(e)}", level=logging.ERROR)
    
    def _create_button(self, parent, text, command, bg=None):
        """Hilfsmethode zum Erstellen eines einheitlichen Buttons"""
        if bg is None:
            bg = self.colors["primary"]
            
        return tk.Button(
            parent, 
            text=text, 
            command=command, 
            bg=bg, 
            fg=self.colors["text_primary"],
            padx=10, 
            pady=5, 
            relief=tk.FLAT
        )
    
    def log(self, message, level=logging.INFO):
        """Fügt eine Nachricht zum Protokollbereich hinzu"""
        # Logging an das Logger-Objekt
        self.logger.log(level, message)
        
        # Protokollfarbe basierend auf dem Level
        color = self.colors["text_primary"]
        if level == logging.WARNING:
            color = self.colors["warning"]
        elif level == logging.ERROR:
            color = self.colors["error"]
        elif level == logging.INFO:
            color = self.colors["text_secondary"]
        
        # Füge die Nachricht zum GUI-Log hinzu
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{message}\n", (level,))
        self.log_area.tag_config(level, foreground=color)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        # Aktualisiere die GUI
        self.root.update_idletasks()