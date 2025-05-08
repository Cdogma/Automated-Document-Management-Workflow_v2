"""
Basisdiagramme für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen für einfache Chart-Typen wie Balkendiagramme für 
Dokumenttypen und Größenverteilungen.
"""

import logging
from . import gui_charts_core as core

def update_type_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumenttypen.
    """
    try:
        types = data.get("types", {})
        
        if not types:
            core.handle_empty_data(ax, app, "Keine Dokumenttypen verfügbar")
            return
        
        sorted_types = dict(sorted(types.items(), key=lambda item: item[1], reverse=True))
        
        # Angepasste Farbpalette für bessere Sichtbarkeit im Dark Mode
        colors = [
            '#3498db',  # Hellblau
            '#2ecc71',  # Grün
            '#e74c3c',  # Rot
            '#f39c12',  # Orange
            '#9b59b6',  # Violett
        ]
        
        if len(sorted_types) > 10:
            top_types = dict(list(sorted_types.items())[:9])
            other_count = sum(dict(list(sorted_types.items())[9:]).values())
            top_types["Andere"] = other_count
            sorted_types = top_types
        
        # Balkendiagramm erstellen
        bars = ax.bar(
            sorted_types.keys(),
            sorted_types.values(),
            color=colors[:len(sorted_types)],
            edgecolor='none',
            alpha=0.9
        )
        
        # Grid mit dunklem Design
        ax.yaxis.grid(True, linestyle='--', alpha=0.1, color=app.colors["text_secondary"])
        ax.set_axisbelow(True)
        
        # Beschriftungen
        ax.set_title("Dokumentenverteilung nach Typ", fontsize=14, color=app.colors["text_primary"])
        ax.set_xlabel("Dokumenttyp", color=app.colors["text_primary"])
        ax.set_ylabel("Anzahl", color=app.colors["text_primary"])
        
        # X-Achsen-Beschriftungen rotieren
        ax.set_xticklabels(sorted_types.keys(), rotation=45, ha='right')
        
        # Zahlen über den Balken anzeigen
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom',
                       color=app.colors["text_primary"],
                       fontsize=10)
        
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
    """
    try:
        sizes = data.get("sizes", {})
        
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
        
        # Angepasste Farbpalette für bessere Sichtbarkeit
        colors = [
            '#2ecc71',  # Grün
            '#3498db',  # Blau
            '#f39c12',  # Orange
            '#e74c3c'   # Rot
        ]
        
        # Balkendiagramm erstellen
        bars = ax.bar(
            ordered_sizes.keys(),
            ordered_sizes.values(),
            color=colors[:len(ordered_sizes)],
            edgecolor='none',
            alpha=0.9
        )
        
        # Grid mit dunklem Design
        ax.yaxis.grid(True, linestyle='--', alpha=0.1, color=app.colors["text_secondary"])
        ax.set_axisbelow(True)
        
        # Beschriftungen
        ax.set_title("Dokumentenverteilung nach Größe", fontsize=14, color=app.colors["text_primary"])
        ax.set_xlabel("Dokumentgröße", color=app.colors["text_primary"])
        ax.set_ylabel("Anzahl", color=app.colors["text_primary"])
        
        # Zahlen über den Balken anzeigen
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom',
                       color=app.colors["text_primary"],
                       fontsize=10)
        
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