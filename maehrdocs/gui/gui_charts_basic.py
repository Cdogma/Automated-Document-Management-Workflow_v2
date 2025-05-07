"""
Basisdiagramme für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen für einfache Chart-Typen wie Balkendiagramme für 
Dokumenttypen und Größenverteilungen.

Diese Datei implementiert die grundlegenden Visualisierungen für die Statistik-
Komponente mit Fehlerbehandlung und Dark-Theme-Unterstützung.
"""

import logging
from . import gui_charts_core as core

def update_type_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumenttypen.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    try:
        types = data.get("types", {})
        
        # Fehlerbehandlung: Keine Daten
        if not types:
            core.handle_empty_data(ax, app, "Keine Dokumenttypen verfügbar")
            return
        
        # Nach Anzahl sortieren (absteigend)
        sorted_types = dict(sorted(types.items(), key=lambda item: item[1], reverse=True))
        
        # Farbpalette für die Balken - heller und kontrastreicher für Dark Mode
        colors = [
            app.colors["primary"],
            app.colors["accent"],
            app.colors["success"],
            app.colors["warning"],
            app.colors["error"]
        ]
        
        # Begrenzen auf die Top 10
        if len(sorted_types) > 10:
            top_types = dict(list(sorted_types.items())[:9])
            other_count = sum(dict(list(sorted_types.items())[9:]).values())
            top_types["Andere"] = other_count
            sorted_types = top_types
        
        # Balkendiagramm erstellen
        bars = ax.bar(
            sorted_types.keys(),
            sorted_types.values(),
            color=colors[:len(sorted_types)]
        )
        
        # Grid für bessere Lesbarkeit
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        
        # Beschriftungen
        ax.set_title("Dokumentenverteilung nach Typ")
        ax.set_xlabel("Dokumenttyp")
        ax.set_ylabel("Anzahl")
        
        # X-Achsen-Beschriftungen rotieren für bessere Lesbarkeit
        ax.set_xticklabels(sorted_types.keys(), rotation=45, ha='right')
        
        # Zahlen über den Balken anzeigen - mit kontrastreichem Hintergrund
        for bar in bars:
            height = bar.get_height()
            # Hellerer und besser sichtbarer Text für Balken-Beschriftungen
            ax.annotate(f'{height}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 Punkte Offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       color='white',  # Immer weiß für besseren Kontrast
                       bbox=dict(boxstyle="round,pad=0.3", fc=app.colors["primary"], alpha=0.7))
        
        # Tooltips zu den Balken hinzufügen
        for bar, (type_name, count) in zip(bars, sorted_types.items()):
            tooltip_text = f"{type_name}: {count} Dokumente"
            core.add_tooltip(figure, ax, bar, tooltip_text)
        
        # Dark Theme anwenden
        core.apply_dark_theme(ax, app, figure)
        
        # Layout anpassen
        figure.tight_layout()
        
        # Daten im Chart-Objekt speichern für Interaktivität
        ax.type_data = sorted_types
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Typ-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Typendarstellung: {type(e).__name__}")

def update_size_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumentgrößen.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    try:
        sizes = data.get("sizes", {})
        
        # Fehlerbehandlung: Keine Daten
        if not sizes:
            core.handle_empty_data(ax, app, "Keine Größendaten verfügbar")
            return
        
        # Größenkategorien in der richtigen Reihenfolge
        size_order = ["<0.5 MB", "0.5-1 MB", "1-5 MB", ">5 MB"]
        ordered_sizes = {}
        for category in size_order:
            if category in sizes:
                ordered_sizes[category] = sizes[category]
            else:
                ordered_sizes[category] = 0
        
        # Klarere, hellere Farbpalette für besseren Kontrast
        colors = [
            '#4CAF50',  # Hellgrün
            '#2196F3',  # Hellblau
            '#FFC107',  # Amber
            '#F44336'   # Rot
        ]
        
        # Balkendiagramm erstellen
        bars = ax.bar(
            ordered_sizes.keys(),
            ordered_sizes.values(),
            color=colors[:len(ordered_sizes)],
            edgecolor=app.colors["background_dark"],  # Kanten für bessere Sichtbarkeit
            linewidth=1
        )
        
        # Grid für bessere Lesbarkeit
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        
        # Beschriftungen
        ax.set_title("Dokumentenverteilung nach Größe")
        ax.set_xlabel("Dokumentgröße")
        ax.set_ylabel("Anzahl")
        
        # Zahlen über den Balken anzeigen - mit kontrastreichem Hintergrund
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),  # 3 Punkte Offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       color='white',  # Weiß für besten Kontrast
                       bbox=dict(boxstyle="round,pad=0.3", fc=app.colors["primary"], alpha=0.7))
        
        # Tooltips zu den Balken hinzufügen
        for bar, (size_category, count) in zip(bars, ordered_sizes.items()):
            tooltip_text = f"{size_category}: {count} Dokumente"
            core.add_tooltip(figure, ax, bar, tooltip_text)
        
        # Dark Theme anwenden
        core.apply_dark_theme(ax, app, figure)
        
        # Layout anpassen
        figure.tight_layout()
        
        # Daten im Chart-Objekt speichern für Interaktivität
        ax.size_data = ordered_sizes
        ax.documents = data.get("documents", [])
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Größen-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Größendarstellung: {type(e).__name__}")