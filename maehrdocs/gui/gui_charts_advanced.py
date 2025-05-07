"""
Fortgeschrittene Diagramme für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen für komplexere Chart-Typen wie Kreisdiagramme für Absender
und Liniendiagramme für Zeitverläufe.

Diese Datei implementiert die anspruchsvolleren Visualisierungen für die Statistik-
Komponente mit zusätzlicher Interaktivität, Tooltips und verbesserten
Darstellungsoptionen.
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
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    try:
        senders = data.get("senders", {})
        
        # Fehlerbehandlung: Keine Daten
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
        
        # Hellere Farben für besseren Kontrast im Dark Mode
        colors = [
            '#5DA5DA', '#FAA43A', '#60BD68', '#F17CB0', '#B2912F',
            '#B276B2', '#DECF3F', '#F15854', '#4D4D4D', '#1E90FF'
        ]
        
        # Kreisdiagramm erstellen
        wedges, texts, autotexts = ax.pie(
            sorted_senders.values(),
            labels=None,  # Labels in der Legende statt direkt am Kreis
            autopct='%1.1f%%',
            textprops={'color': 'white', 'fontweight': 'bold'},  # Kontrastreiche Prozentangaben
            colors=colors[:len(sorted_senders)],
            wedgeprops={'width': 0.5, 'edgecolor': app.colors["background_medium"]}  # Donut mit Randfarbe
        )
        
        # Schatten hinzufügen für bessere Sichtbarkeit
        for w in wedges:
            w.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground=app.colors["background_dark"])
            ])
        
        # Prozent-Beschriftung optimieren
        for autotext in autotexts:
            autotext.set_path_effects([
                matplotlib.patheffects.withStroke(linewidth=2, foreground=app.colors["background_dark"])
            ])
        
        # Legende hinzufügen mit besserer Positionierung
        legend = ax.legend(
            wedges,
            sorted_senders.keys(),
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            frameon=True,  # Rahmen für bessere Lesbarkeit
            facecolor=app.colors["background_medium"],
            edgecolor=app.colors["text_secondary"]
        )
        
        # Beschriftung
        ax.set_title("Dokumentenverteilung nach Absender")
        
        # Tooltips zu den Kuchenstücken hinzufügen
        for wedge, (sender, count) in zip(wedges, sorted_senders.items()):
            percentage = 100 * count / sum(sorted_senders.values())
            tooltip_text = f"{sender}: {count} Dokumente ({percentage:.1f}%)"
            core.add_tooltip(figure, ax, wedge, tooltip_text)
        
        # Dark Theme anwenden
        core.apply_dark_theme(ax, app, figure)
        
        # Layout anpassen
        figure.tight_layout()
        
        # Daten im Chart-Objekt speichern für Interaktivität
        ax.sender_data = sorted_senders
        ax.documents = data.get("documents", [])
        ax.wedges = wedges  # Für die Interaktivität
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Absender-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Absendergrafik: {type(e).__name__}")

def update_timeline_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Liniendiagramm zur Visualisierung des 
    Dokumentenzeitlaufs.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    try:
        timeline = data.get("timeline", {})
        
        # Fehlerbehandlung: Keine Daten
        if not timeline:
            core.handle_empty_data(ax, app, "Keine Zeitdaten verfügbar")
            return
        
        # Daten sortieren und für matplotlib aufbereiten
        dates = []
        counts = []
        date_dict = {}  # Speichert original Datum zu formatiertem Datum
        
        # Fehlerbehandlung: Ungültige Datumsformate
        for date_str, count in sorted(timeline.items()):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_obj)
                counts.append(count)
                date_dict[date_obj] = date_str  # Für spätere Referenz
            except ValueError:
                # Ungültiges Datum überspringen
                logger = logging.getLogger(__name__)
                logger.warning(f"Ungültiges Datumsformat übersprungen: {date_str}")
                continue
        
        # Prüfen, ob nach der Filterung noch Daten übrig sind
        if not dates:
            core.handle_empty_data(ax, app, "Keine gültigen Zeitdaten verfügbar")
            return
        
        # Linienchart erstellen mit größerer Linienbreite und hellerer Farbe
        line, = ax.plot(
            dates, counts,
            marker='o',
            linestyle='-',
            linewidth=2.5,  # Dickere Linie
            color='#3498db',  # Helleres Blau
            markersize=8,
            markerfacecolor='#f39c12',  # Kontrastreiche Markerfarbe
            markeredgecolor='white',
            markeredgewidth=1.5
        )
        
        # Füllung unter der Linie für bessere Sichtbarkeit
        ax.fill_between(dates, counts, alpha=0.2, color='#3498db')
        
        # Grid für bessere Lesbarkeit
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Datumsformatierung
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # Wenn mehr als 7 Datumspunkte, nur einige anzeigen
        if len(dates) > 7:
            # Wochenweises Raster
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            # Alternativ: Automatische Locator für schönere Achsenbeschriftung
            # Geeignet für längere Zeiträume
            if len(dates) > 30:
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Datenpunkte beschriften
        for i, (date, count) in enumerate(zip(dates, counts)):
            if count > 0:  # Nur beschriften, wenn Wert größer 0
                ax.annotate(f'{count}',
                           xy=(date, count),
                           xytext=(0, 10),
                           textcoords="offset points",
                           ha='center',
                           color='white',
                           bbox=dict(boxstyle="round,pad=0.3", fc=app.colors["primary"], alpha=0.7))
        
        # Tooltips für die Datenpunkte
        scatter = ax.scatter(dates, counts, s=0)  # Unsichtbare Scatter-Punkte für bessere Tooltips
        for date, count in zip(dates, counts):
            # Formatieren für den Tooltip
            date_str = date.strftime("%d.%m.%Y")
            tooltip_text = f"Datum: {date_str}\nDokumente: {count}"
            
            # Tooltip-Bereich erstellen
            # Wir erstellen einen unsichtbaren Kreis um jeden Datenpunkt
            point = matplotlib.patches.Circle((mdates.date2num(date), count), 
                                             radius=0.2, 
                                             transform=ax.get_xaxis_transform(),
                                             alpha=0.0)  # unsichtbar
            ax.add_patch(point)
            
            # Tooltip zum Punkt hinzufügen
            core.add_tooltip(figure, ax, point, tooltip_text)
        
        # Beschriftungen
        ax.set_title("Dokumentenaufkommen im Zeitverlauf")
        ax.set_xlabel("Datum")
        ax.set_ylabel("Anzahl")
        
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
        ax.date_dict = date_dict  # Für Zuordnung formatierter Daten
        ax.documents = data.get("documents", [])
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Aktualisieren des Zeitverlauf-Charts: {str(e)}")
        core.handle_empty_data(ax, app, f"Fehler bei Zeitdarstellung: {type(e).__name__}")