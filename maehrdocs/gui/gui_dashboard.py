"""
Dashboard-Funktionalität für MaehrDocs
Erstellt das Dashboard mit Statuskarten und Aktivitätsanzeige
"""

import tkinter as tk
from .gui_cards import create_status_card
from .gui_statistics import create_statistics_panel

def create_dashboard(app, parent, config, open_folder_callback):
    """
    Erstellt das Dashboard mit Statusanzeigen
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        config: Konfigurationsdaten
        open_folder_callback: Callback-Funktion zum Öffnen von Ordnern
        
    Returns:
        dict: Dictionary mit allen erstellten Dashboard-Elementen
    """
    dashboard_elements = {}
    
    dashboard_frame = tk.Frame(parent, bg=app.colors["background_medium"], padx=15, pady=15)
    dashboard_frame.pack(fill=tk.X, pady=10)
    
    # Überschrift
    dashboard_header = tk.Label(
        dashboard_frame, 
        text="Dashboard", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    dashboard_header.pack(anchor=tk.W, pady=(0, 10))
    
    # Container für die Karten
    cards_frame = tk.Frame(dashboard_frame, bg=app.colors["background_medium"])
    cards_frame.pack(fill=tk.X)
    
    # Karten für Ordner-Status
    inbox_card = create_status_card(app, cards_frame, "Eingang", "01_InboxDocs", "📥")
    inbox_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    dashboard_elements["inbox_card"] = inbox_card
    
    processed_card = create_status_card(app, cards_frame, "Verarbeitet", "02_FinalDocs", "✅")
    processed_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    dashboard_elements["processed_card"] = processed_card
    
    trash_card = create_status_card(app, cards_frame, "Probleme", "03_TrashDocs", "🗑️")
    trash_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    dashboard_elements["trash_card"] = trash_card
    
    # Letzte Aktivität
    activity_frame = tk.Frame(dashboard_frame, bg=app.colors["card_background"], padx=15, pady=15)
    activity_frame.pack(fill=tk.X, pady=10)
    
    activity_header = tk.Label(
        activity_frame, 
        text="Letzte Aktivität", 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    activity_header.pack(anchor=tk.W, pady=(0, 10))
    
    activity_list = tk.Text(
        activity_frame, 
        height=3, 
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        font=app.fonts["normal"],
        wrap=tk.WORD,
        state=tk.DISABLED
    )
    activity_list.pack(fill=tk.X)
    dashboard_elements["activity_list"] = activity_list
    
    # NEU: Statistik-Panel hinzufügen
    statistics_frame = tk.Frame(dashboard_frame, bg=app.colors["background_medium"], pady=10)
    statistics_frame.pack(fill=tk.BOTH, expand=True)
    
    # Statistik-Panel erstellen
    stats_elements = create_statistics_panel(app, statistics_frame)
    dashboard_elements["statistics_panel"] = stats_elements["stats_frame"]
    
    return dashboard_elements