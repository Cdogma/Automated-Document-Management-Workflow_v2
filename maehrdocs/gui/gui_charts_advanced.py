"""
Fortgeschrittene Diagramme für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen für komplexere Chart-Typen wie Kreisdiagramme für Absender
und Liniendiagramme für Zeitverläufe.
"""

import logging
import matplotlib
import matplotlib.dates as mdates
from datetime import datetime
from . import gui_charts_core as core

def update_sender_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Kreisdiagramm zur Visualisierung der 
    Dokumentabsender.
    """
    try:
        senders = data.get("senders", {})
        
        if not senders:
            core.handle_empty_data(ax, app, "Keine Absenderdaten verfügbar")
            return
        
        # Nach Anzahl sortieren (absteigend)
        sorted_senders = dict(sorted(senders.items(), key=lambda item: item[1], reverse=True))
        
        # Begrenzen auf die Top 10
        if len(sorted_senders) > 10:
            top_senders = dict(list(sorted_senders.items())[:9])
            other_count = sum(dict(list(sorted_senders.items())[9:]).values())
            top_senders["Andere"] = other_count
            sorted_senders = top_senders
        
        # Angepasste Farbpalette für bessere Sichtbarkeit im Dark Mode
        colors = [
            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
            '#34495e', '#16a085', '#e67e22', '#8e44ad', '#2980b9'
        ]
        
        # Kreisdiagramm erstellen
        wedges, texts, autotexts = ax.pie(
            sorted_senders.values(),
            labels=None,  # Labels in der Legende
            autopct='%1.1f%%',
            textprops={'color': 'white', 'fontweight': 'bold', 'fontsize': 10},
            colors=colors[:len(sorted_senders)],
            wedgeprops={'width': 0.5, 'edgecolor': app.colors["background_dark"], 'linewidth': 1}
        )
        
        # Schatten für bessere Sichtbarkeit
        for w in wedges:
            w.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground=app.colors["background_dark"])
            ])
        
        # Prozent-Beschriftung optimieren
        for autotext in autotexts:
            autotext.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground=app.colors["background_dark"])
            ])
        
        # Legende mit Dark Theme
        legend = ax.legend(
            wedges,
            sorted_senders.keys(),
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            frameon=True,
            facecolor=app.colors["background_medium"],
            edgecolor=app.colors["text_secondary"],
            labelcolor=app.colors["text_primary"]
        )
        
        # Titel
        ax.set_title("Dokumentenverteilung nach Absender", fontsize=14, color=app.colors["text_primary"])
        
        # Dark Theme anwenden
        core.apply_dark_theme(ax, app, figure)
        
        # Layout anpassen
        figure.tight_layout()
        
        # Daten im Chart-Objekt speichern für Interaktivität
        ax.sender_data = sorted_senders
        ax.documents = data.get("documents", [])
        ax.wedges = wedges
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Absender-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Absendergrafik: {type(e).__name__}")

def update_timeline_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Liniendiagramm zur Visualisierung des 
    Dokumentenzeitlaufs.
    """
    try:
        timeline = data.get("timeline", {})
        
        if not timeline:
            core.handle_empty_data(ax, app, "Keine Zeitdaten verfügbar")
            return
        
        # Daten sortieren und für matplotlib aufbereiten
        dates = []
        counts = []
        date_dict = {}
        
        for date_str, count in sorted(timeline.items()):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_obj)
                counts.append(count)
                date_dict[date_obj] = date_str
            except ValueError:
                logger = logging.getLogger(__name__)
                logger.warning(f"Ungültiges Datumsformat übersprungen: {date_str}")
                continue
        
        if not dates:
            core.handle_empty_data(ax, app, "Keine gültigen Zeitdaten verfügbar")
            return
        
        # Linienchart erstellen
        line, = ax.plot(
            dates, counts,
            marker='o',
            linestyle='-',
            linewidth=2.5,
            color='#3498db',
            markersize=8,
            markerfacecolor='#3498db',
            markeredgecolor='white',
            markeredgewidth=1.5
        )
        
        # Füllung unter der Linie
        ax.fill_between(dates, counts, alpha=0.2, color='#3498db')
        
        # Grid mit dunklem Design
        ax.grid(True, linestyle='--', alpha=0.1, color=app.colors["text_secondary"])
        ax.set_axisbelow(True)
        
        # Datumsformatierung
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # Wenn mehr als 7 Datumspunkte, automatische Locator
        if len(dates) > 7:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Datenpunkte beschriften
        for i, (date, count) in enumerate(zip(dates, counts)):
            if count > 0:
                ax.text(date, count,
                       f'{int(count)}',
                       ha='center', va='bottom',
                       color=app.colors["text_primary"],
                       fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.3", 
                                facecolor=app.colors["background_medium"], 
                                alpha=0.8,
                                edgecolor='none'))
        
        # Beschriftungen
        ax.set_title("Dokumentenaufkommen im Zeitverlauf", fontsize=14, color=app.colors["text_primary"])
        ax.set_xlabel("Datum", color=app.colors["text_primary"])
        ax.set_ylabel("Anzahl", color=app.colors["text_primary"])
        
        # Dark Theme anwenden
        core.apply_dark_theme(ax, app, figure)
        
        # Beschriftungen rotieren
        figure.autofmt_xdate(rotation=45)
        
        # Layout anpassen
        figure.tight_layout()
        
        # Daten im Chart-Objekt speichern für Interaktivität
        ax.timeline_data = timeline
        ax.dates = dates
        ax.counts = counts
        ax.date_dict = date_dict
        ax.documents = data.get("documents", [])
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Zeitverlauf-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Zeitdarstellung: {type(e).__name__}")