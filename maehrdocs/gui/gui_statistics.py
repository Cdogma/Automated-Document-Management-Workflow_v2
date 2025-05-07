"""
Statistikkomponente für MaehrDocs GUI
Enthält Funktionen zum Erstellen und Anzeigen von statistischen Auswertungen
über verarbeitete Dokumente mit erweiterten Filtermöglichkeiten.
"""

import tkinter as tk
from tkinter import ttk
import logging

# Eigene Module importieren
from .gui_statistics_data import collect_data, clear_cache
from .gui_statistics_charts import (
    create_chart_figure,
    update_type_chart,
    update_sender_chart,
    update_size_chart,
    update_timeline_chart
)

class StatisticsPanel:
    """
    Klasse zur Darstellung von Dokumentenstatistiken.
    
    Diese Klasse erstellt und verwaltet ein Panel mit Statistiken und
    Visualisierungen der verarbeiteten Dokumente, einschließlich:
    - Verteilung nach Dokumenttyp
    - Verteilung nach Absender
    - Verteilung nach Dokumentgröße
    - Zeitverlauf des Dokumentenaufkommens
    
    Mit erweiterten Filtermöglichkeiten für:
    - Zeitraum (Alle, Heute, Diese Woche, etc.)
    - Dokumenttyp
    - Absender
    """
    
    def __init__(self, app, parent_frame):
        """
        Initialisiert das Statistik-Panel.
        
        Args:
            app: Die Hauptanwendung (GuiApp-Instanz)
            parent_frame: Das übergeordnete Frame für das Panel
        """
        self.app = app
        self.parent_frame = parent_frame
        self.logger = logging.getLogger(__name__)
        
        # Filter-Optionen
        self.time_periods = ["Alle", "Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr"]
        self.selected_period = tk.StringVar(value=self.time_periods[0])
        self.selected_type = tk.StringVar(value="Alle Typen")
        self.selected_sender = tk.StringVar(value="Alle Absender")
        
        # Filterlisten für Typ und Absender (werden später befüllt)
        self.doc_types = ["Alle Typen"]
        self.senders = ["Alle Absender"]
        
        # UI erstellen
        self._create_ui()
        
        # Initial Daten laden und Charts anzeigen
        self.update_charts()
    
    def _create_ui(self):
        """Erstellt die Benutzeroberfläche des Statistik-Panels."""
        # Hauptframe
        self.frame = tk.Frame(self.parent_frame, bg=self.app.colors["card_background"], padx=15, pady=15)
        self.frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Header mit Titel und Filteroption
        header_frame = tk.Frame(self.frame, bg=self.app.colors["card_background"])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Titel
        title_label = tk.Label(
            header_frame, 
            text="Dokumentenstatistik", 
            font=self.app.fonts["subheader"],
            fg=self.app.colors["text_primary"],
            bg=self.app.colors["card_background"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Filter-Bereich
        filter_frame = tk.Frame(self.frame, bg=self.app.colors["card_background"], pady=10)
        filter_frame.pack(fill=tk.X)
        
        # Zeitraum-Filter
        period_frame = tk.Frame(filter_frame, bg=self.app.colors["card_background"])
        period_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        period_label = tk.Label(
            period_frame, 
            text="Zeitraum:", 
            font=self.app.fonts["normal"],
            fg=self.app.colors["text_primary"],
            bg=self.app.colors["card_background"]
        )
        period_label.pack(side=tk.LEFT, padx=(0, 5))
        
        period_dropdown = ttk.Combobox(
            period_frame,
            textvariable=self.selected_period,
            values=self.time_periods,
            state="readonly",
            width=12
        )
        period_dropdown.pack(side=tk.LEFT)
        period_dropdown.bind("<<ComboboxSelected>>", lambda e: self._on_filter_change())
        
        # Typ-Filter
        type_frame = tk.Frame(filter_frame, bg=self.app.colors["card_background"])
        type_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        type_label = tk.Label(
            type_frame, 
            text="Dokumenttyp:", 
            font=self.app.fonts["normal"],
            fg=self.app.colors["text_primary"],
            bg=self.app.colors["card_background"]
        )
        type_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.type_dropdown = ttk.Combobox(
            type_frame,
            textvariable=self.selected_type,
            values=self.doc_types,
            state="readonly",
            width=15
        )
        self.type_dropdown.pack(side=tk.LEFT)
        self.type_dropdown.bind("<<ComboboxSelected>>", lambda e: self._on_filter_change())
        
        # Absender-Filter
        sender_frame = tk.Frame(filter_frame, bg=self.app.colors["card_background"])
        sender_frame.pack(side=tk.LEFT)
        
        sender_label = tk.Label(
            sender_frame, 
            text="Absender:", 
            font=self.app.fonts["normal"],
            fg=self.app.colors["text_primary"],
            bg=self.app.colors["card_background"]
        )
        sender_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.sender_dropdown = ttk.Combobox(
            sender_frame,
            textvariable=self.selected_sender,
            values=self.senders,
            state="readonly",
            width=20
        )
        self.sender_dropdown.pack(side=tk.LEFT)
        self.sender_dropdown.bind("<<ComboboxSelected>>", lambda e: self._on_filter_change())
        
        # Reset-Button
        reset_button = tk.Button(
            filter_frame,
            text="Filter zurücksetzen",
            font=self.app.fonts["small"],
            bg=self.app.colors["primary"],
            fg=self.app.colors["text_primary"],
            activebackground=self.app.colors["accent"],
            activeforeground=self.app.colors["text_primary"],
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2",
            command=self._reset_filters
        )
        reset_button.pack(side=tk.RIGHT)
        
        # Container für Charts
        self.charts_frame = tk.Frame(self.frame, bg=self.app.colors["card_background"])
        self.charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid für Charts (2x2)
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.columnconfigure(1, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)
        self.charts_frame.rowconfigure(1, weight=1)
        
        # Einzelne Chart-Frames
        self.type_chart_frame = tk.Frame(self.charts_frame, bg=self.app.colors["background_medium"])
        self.type_chart_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.sender_chart_frame = tk.Frame(self.charts_frame, bg=self.app.colors["background_medium"])
        self.sender_chart_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.size_chart_frame = tk.Frame(self.charts_frame, bg=self.app.colors["background_medium"])
        self.size_chart_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.timeline_chart_frame = tk.Frame(self.charts_frame, bg=self.app.colors["background_medium"])
        self.timeline_chart_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Matplotlib-Figuren erstellen
        self.type_figure, self.type_canvas = create_chart_figure(self.app, self.type_chart_frame)
        self.sender_figure, self.sender_canvas = create_chart_figure(self.app, self.sender_chart_frame)
        self.size_figure, self.size_canvas = create_chart_figure(self.app, self.size_chart_frame)
        self.timeline_figure, self.timeline_canvas = create_chart_figure(self.app, self.timeline_chart_frame)
    
    def _on_filter_change(self):
        """Wird aufgerufen, wenn sich ein Filter ändert."""
        self.update_charts()
    
    def _reset_filters(self):
        """Setzt alle Filter auf die Standardwerte zurück."""
        self.selected_period.set(self.time_periods[0])
        self.selected_type.set("Alle Typen")
        self.selected_sender.set("Alle Absender")
        self.update_charts()
    
    def _update_filter_options(self, data):
        """
        Aktualisiert die Dropdown-Listen für Dokumenttyp und Absender
        basierend auf den verfügbaren Daten.
        
        Args:
            data: Die gesammelten Dokumentendaten
        """
        # Dokumenttypen für das Dropdown sammeln
        types = ["Alle Typen"]
        types.extend(sorted(data["types"].keys()))
        
        # Absender für das Dropdown sammeln
        senders = ["Alle Absender"]
        senders.extend(sorted(data["senders"].keys()))
        
        # Werte im Dropdown aktualisieren, ohne die aktuelle Auswahl zu verlieren
        current_type = self.selected_type.get()
        self.type_dropdown['values'] = types
        if current_type not in types:
            self.selected_type.set("Alle Typen")
        
        current_sender = self.selected_sender.get()
        self.sender_dropdown['values'] = senders
        if current_sender not in senders:
            self.selected_sender.set("Alle Absender")
    
    def update_charts(self):
        """Aktualisiert alle Charts mit aktuellen Daten und angewandten Filtern."""
        try:
            # Daten sammeln für den ausgewählten Zeitraum
            period = self.selected_period.get()
            data = collect_data(self.app, period)
            
            # Filter-Dropdown-Optionen aktualisieren
            self._update_filter_options(data)
            
            # Zusätzliche Filter anwenden
            filtered_data = self._apply_filters(data)
            
            # Charts aktualisieren
            # Typ-Chart
            self.type_figure.clear()
            type_ax = self.type_figure.add_subplot(111)
            update_type_chart(type_ax, filtered_data, self.app, self.type_figure)
            self.type_canvas.draw()
            
            # Absender-Chart
            self.sender_figure.clear()
            sender_ax = self.sender_figure.add_subplot(111)
            update_sender_chart(sender_ax, filtered_data, self.app, self.sender_figure)
            self.sender_canvas.draw()
            
            # Größen-Chart
            self.size_figure.clear()
            size_ax = self.size_figure.add_subplot(111)
            update_size_chart(size_ax, filtered_data, self.app, self.size_figure)
            self.size_canvas.draw()
            
            # Zeitverlauf-Chart
            self.timeline_figure.clear()
            timeline_ax = self.timeline_figure.add_subplot(111)
            update_timeline_chart(timeline_ax, filtered_data, self.app, self.timeline_figure)
            self.timeline_canvas.draw()
            
            # Log generieren
            filter_info = f"Zeitraum: {period}"
            if self.selected_type.get() != "Alle Typen":
                filter_info += f", Typ: {self.selected_type.get()}"
            if self.selected_sender.get() != "Alle Absender":
                filter_info += f", Absender: {self.selected_sender.get()}"
                
            self.logger.debug(f"Statistiken aktualisiert mit Filtern: {filter_info}")
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Aktualisierung der Statistiken: {str(e)}")
    
    def _apply_filters(self, data):
        """
        Wendet die ausgewählten Filter auf die Daten an.
        
        Args:
            data: Die ursprünglichen Dokumentendaten
            
        Returns:
            dict: Die gefilterten Daten
        """
        # Wenn keine zusätzlichen Filter aktiv sind, original Daten zurückgeben
        if (self.selected_type.get() == "Alle Typen" and 
            self.selected_sender.get() == "Alle Absender"):
            return data
        
        # Tiefe Kopie der Datenstruktur erstellen für die Filterung
        filtered_data = {
            "types": {},
            "senders": {},
            "sizes": {},
            "timeline": {},
            "documents": []
        }
        
        # Filter anwenden
        selected_type = self.selected_type.get()
        selected_sender = self.selected_sender.get()
        
        # Dokumente filtern
        for doc in data["documents"]:
            # Typ-Filter anwenden
            if selected_type != "Alle Typen" and doc["type"] != selected_type:
                continue
                
            # Absender-Filter anwenden
            if selected_sender != "Alle Absender" and doc["sender"] != selected_sender:
                continue
                
            # Dokument aufnehmen, da es die Filter besteht
            filtered_data["documents"].append(doc)
            
            # Statistik-Akkumulatoren aktualisieren
            # Typ zählen
            if doc["type"] in filtered_data["types"]:
                filtered_data["types"][doc["type"]] += 1
            else:
                filtered_data["types"][doc["type"]] = 1
            
            # Absender zählen
            if doc["sender"] in filtered_data["senders"]:
                filtered_data["senders"][doc["sender"]] += 1
            else:
                filtered_data["senders"][doc["sender"]] = 1
            
            # Größe kategorisieren und zählen
            size_category = doc.get("size_category", "")
            if not size_category:
                from .gui_statistics_data import categorize_size
                size_category = categorize_size(doc["size"])
                
            if size_category in filtered_data["sizes"]:
                filtered_data["sizes"][size_category] += 1
            else:
                filtered_data["sizes"][size_category] = 1
            
            # Datum für Zeitverlauf
            if hasattr(doc["mtime"], "strftime"):
                date_key = doc["mtime"].strftime("%Y-%m-%d")
                if date_key in filtered_data["timeline"]:
                    filtered_data["timeline"][date_key] += 1
                else:
                    filtered_data["timeline"][date_key] = 1
        
        return filtered_data

def create_statistics_panel(app, parent_frame):
    """
    Erstellt ein Statistik-Panel im Dashboard.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        parent_frame: Das übergeordnete Frame für das Panel
        
    Returns:
        dict: Dictionary mit allen erstellten Statistik-Elementen
    """
    try:
        # Statistik-Panel erstellen
        stats_panel = StatisticsPanel(app, parent_frame)
        
        # Cache leeren, falls vorhanden
        clear_cache()
        
        # Elemente zurückgeben
        return {
            "stats_frame": stats_panel.frame,
            "stats_panel": stats_panel
        }
    except Exception as e:
        app.logger.error(f"Fehler beim Erstellen des Statistik-Panels: {str(e)}")
        
        # Leeres Frame erstellen im Fehlerfall
        error_frame = tk.Frame(parent_frame, bg=app.colors["card_background"], padx=15, pady=15)
        error_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        error_label = tk.Label(
            error_frame,
            text="Fehler beim Laden der Statistik-Komponente",
            font=app.fonts["normal"],
            fg=app.colors["error"],
            bg=app.colors["card_background"]
        )
        error_label.pack(pady=20)
        
        return {
            "stats_frame": error_frame
        }