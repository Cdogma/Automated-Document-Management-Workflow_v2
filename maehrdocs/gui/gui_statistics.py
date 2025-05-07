"""
Statistikmodul für MaehrDocs
Enthält Funktionen zur statistischen Auswertung und Visualisierung von Dokumentenbeständen.

Dieses Modul integriert die Datensammlung und Chart-Funktionalitäten und bietet
eine grafische Schnittstelle zur Anzeige von Statistiken über verarbeitete Dokumente.
"""

import tkinter as tk
from tkinter import ttk
import logging

# Lokale Importe
from .gui_buttons import create_button
from .gui_cards import create_section_frame
from .gui_statistics_data import collect_data
from .gui_statistics_charts import (
    create_chart_figure,
    update_type_chart,
    update_sender_chart,
    update_size_chart,
    update_timeline_chart
)

def create_statistics_panel(app, parent):
    """
    Erstellt das Statistik-Panel für die Dokumentenanalyse.
    
    Erzeugt ein Panel mit verschiedenen Statistiken und Visualisierungen
    zum Dokumentenbestand, einschließlich Diagrammen zur Verteilung nach
    Typ, Absender, Größe und Zeitverlauf.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        parent: Das übergeordnete Widget
        
    Returns:
        dict: Dictionary mit den erstellten Panel-Elementen
    """
    logger = logging.getLogger(__name__)
    logger.info("Erstelle Statistik-Panel")
    
    # Statistik-Panel-Elemente
    panel_elements = {}
    
    # Hauptframe für das Statistik-Panel
    stats_frame = tk.Frame(parent, bg=app.colors["background_medium"], padx=15, pady=15)
    panel_elements["stats_frame"] = stats_frame
    
    # Überschrift
    header_frame = tk.Frame(stats_frame, bg=app.colors["background_medium"])
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    header = tk.Label(
        header_frame, 
        text="Dokumentenstatistik", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    header.pack(side=tk.LEFT)
    panel_elements["header"] = header
    
    # Filteroptionen
    filter_frame = tk.Frame(header_frame, bg=app.colors["background_medium"])
    filter_frame.pack(side=tk.RIGHT)
    
    filter_label = tk.Label(
        filter_frame,
        text="Zeitraum:",
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    filter_label.pack(side=tk.LEFT, padx=5)
    
    periods = ["Alle", "Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr"]
    period_var = tk.StringVar(value=periods[0])
    period_dropdown = ttk.Combobox(
        filter_frame, 
        textvariable=period_var,
        values=periods,
        state="readonly",
        width=15
    )
    period_dropdown.pack(side=tk.LEFT, padx=5)
    panel_elements["period_var"] = period_var
    
    # Button zum Aktualisieren
    refresh_button = create_button(
        app,
        filter_frame,
        "Aktualisieren",
        lambda: update_statistics(app, panel_elements)
    )
    refresh_button.pack(side=tk.LEFT, padx=5)
    
    # Container für die Chart-Frames
    charts_container = tk.Frame(stats_frame, bg=app.colors["background_medium"])
    charts_container.pack(fill=tk.BOTH, expand=True)
    panel_elements["charts_container"] = charts_container
    
    # Chart für Dokumententypen
    type_frame = create_section_frame(app, charts_container, "Dokumententypen")
    type_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Figure und Canvas für Typ-Chart erstellen
    figure, canvas = create_chart_figure(app, type_frame)
    panel_elements["type_figure"] = figure
    panel_elements["type_canvas"] = canvas
    
    # Chart für Absender
    sender_frame = create_section_frame(app, charts_container, "Absender")
    sender_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Figure und Canvas für Absender-Chart erstellen
    figure, canvas = create_chart_figure(app, sender_frame)
    panel_elements["sender_figure"] = figure
    panel_elements["sender_canvas"] = canvas
    
    # Zweite Reihe von Charts
    charts_container2 = tk.Frame(stats_frame, bg=app.colors["background_medium"])
    charts_container2.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Chart für Dateigrößen
    size_frame = create_section_frame(app, charts_container2, "Dateigrößen")
    size_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Figure und Canvas für Größen-Chart erstellen
    figure, canvas = create_chart_figure(app, size_frame)
    panel_elements["size_figure"] = figure
    panel_elements["size_canvas"] = canvas
    
    # Chart für Zeitverlauf
    timeline_frame = create_section_frame(app, charts_container2, "Zeitverlauf")
    timeline_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Figure und Canvas für Zeitverlauf-Chart erstellen
    figure, canvas = create_chart_figure(app, timeline_frame)
    panel_elements["timeline_figure"] = figure
    panel_elements["timeline_canvas"] = canvas
    
    # Statistiken initial laden
    update_statistics(app, panel_elements)
    
    # Event-Binding für Periodenänderung
    period_dropdown.bind("<<ComboboxSelected>>", 
                        lambda e: update_statistics(app, panel_elements))
    
    return panel_elements

def update_statistics(app, panel_elements):
    """
    Aktualisiert alle Statistiken und Charts im Panel.
    
    Sammelt die Dokumentendaten basierend auf dem ausgewählten Zeitraum
    und aktualisiert alle Visualisierungen mit den neuen Daten.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        panel_elements: Dictionary mit den Panel-Elementen
    """
    logger = logging.getLogger(__name__)
    
    # Ausgewählten Zeitraum abrufen
    period = panel_elements["period_var"].get()
    logger.info(f"Aktualisiere Statistiken für Zeitraum: {period}")
    
    # Daten sammeln
    data = collect_data(app, period)
    
    # Charts aktualisieren
    # Typ-Chart
    figure = panel_elements["type_figure"]
    figure.clear()
    ax = figure.add_subplot(111)
    update_type_chart(ax, data, app, figure)
    panel_elements["type_canvas"].draw()
    
    # Absender-Chart
    figure = panel_elements["sender_figure"]
    figure.clear()
    ax = figure.add_subplot(111)
    update_sender_chart(ax, data, app, figure)
    panel_elements["sender_canvas"].draw()
    
    # Größen-Chart
    figure = panel_elements["size_figure"]
    figure.clear()
    ax = figure.add_subplot(111)
    update_size_chart(ax, data, app, figure)
    panel_elements["size_canvas"].draw()
    
    # Zeitverlauf-Chart
    figure = panel_elements["timeline_figure"]
    figure.clear()
    ax = figure.add_subplot(111)
    update_timeline_chart(ax, data, app, figure)
    panel_elements["timeline_canvas"].draw()
    
    logger.info("Statistiken aktualisiert")