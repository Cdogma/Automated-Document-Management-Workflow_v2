"""
Chart-Funktionen für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen zum Erstellen und Aktualisieren verschiedener Chart-Typen
für die statistische Auswertung von Dokumenten mit verbesserter Dark-Theme-Unterstützung.
"""

import matplotlib
matplotlib.use("TkAgg")  # Muss vor weiteren matplotlib-Imports stehen
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime

def create_chart_figure(app, parent_frame):
    """
    Erstellt eine neue matplotlib-Figur und Canvas für Charts mit Dark-Theme-Unterstützung.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        parent_frame: Das übergeordnete Frame für das Canvas
        
    Returns:
        tuple: (Figure, FigureCanvasTkAgg) Die erstellte Figur und Canvas
    """
    # Neue Figur erstellen
    figure = Figure(figsize=(5, 4), dpi=100)
    
    # Dark Theme Anpassungen
    bg_color = app.colors["background_medium"]
    text_color = app.colors["text_primary"]
    
    figure.patch.set_facecolor(bg_color)
    
    # Canvas erstellen und einbetten
    canvas = FigureCanvasTkAgg(figure, master=parent_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    return figure, canvas

def _apply_dark_theme(ax, app, figure):
    """
    Wendet Dark-Theme-Styling auf ein Achsenobjekt an.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    # Farben aus dem App-Theme
    bg_color = app.colors["background_medium"]
    text_color = app.colors["text_primary"]
    
    # Hintergrund transparent machen
    ax.set_facecolor('none')
    
    # Textfarben anpassen
    ax.title.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    
    # Tick-Labels anpassen
    for tick in ax.get_xticklabels():
        tick.set_color(text_color)
    for tick in ax.get_yticklabels():
        tick.set_color(text_color)
    
    # Achsenfarben anpassen
    ax.spines['bottom'].set_color(text_color)
    ax.spines['top'].set_color(text_color)
    ax.spines['left'].set_color(text_color)
    ax.spines['right'].set_color(text_color)
    
    # Ticks anpassen
    ax.tick_params(axis='x', colors=text_color)
    ax.tick_params(axis='y', colors=text_color)
    
    # Grid-Linien anpassen, falls vorhanden
    if ax.get_xgridlines():
        for line in ax.get_xgridlines():
            line.set_color(app.colors["text_secondary"])
            line.set_alpha(0.2)
    
    if ax.get_ygridlines():
        for line in ax.get_ygridlines():
            line.set_color(app.colors["text_secondary"])
            line.set_alpha(0.2)
    
    # Legende anpassen, falls vorhanden
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor(bg_color)
        legend.get_frame().set_alpha(0.8)
        for text in legend.get_texts():
            text.set_color(text_color)

def update_type_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumenttypen.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    types = data["types"]
    if not types:
        ax.text(0.5, 0.5, "Keine Daten verfügbar", 
               horizontalalignment='center',
               verticalalignment='center',
               color=app.colors["text_primary"],
               transform=ax.transAxes)
        _apply_dark_theme(ax, app, figure)
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
    
    # Dark Theme anwenden
    _apply_dark_theme(ax, app, figure)
    
    # Layout anpassen
    figure.tight_layout()

def update_sender_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumentabsender.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    senders = data["senders"]
    if not senders:
        ax.text(0.5, 0.5, "Keine Daten verfügbar", 
               horizontalalignment='center',
               verticalalignment='center',
               color=app.colors["text_primary"],
               transform=ax.transAxes)
        _apply_dark_theme(ax, app, figure)
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
    
    # Dark Theme anwenden
    _apply_dark_theme(ax, app, figure)
    
    # Layout anpassen
    figure.tight_layout()

def update_size_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung der Dokumentgrößen.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    sizes = data["sizes"]
    if not sizes:
        ax.text(0.5, 0.5, "Keine Daten verfügbar", 
               horizontalalignment='center',
               verticalalignment='center',
               color=app.colors["text_primary"],
               transform=ax.transAxes)
        _apply_dark_theme(ax, app, figure)
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
    
    # Dark Theme anwenden
    _apply_dark_theme(ax, app, figure)
    
    # Layout anpassen
    figure.tight_layout()

def update_timeline_chart(ax, data, app, figure):
    """
    Aktualisiert ein Achsenobjekt mit einem Chart zur Visualisierung des Dokumentenzeitlaufs.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        data: Die gesammelten Dokumentendaten
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    timeline = data["timeline"]
    if not timeline:
        ax.text(0.5, 0.5, "Keine Daten verfügbar", 
               horizontalalignment='center',
               verticalalignment='center',
               color=app.colors["text_primary"],
               transform=ax.transAxes)
        _apply_dark_theme(ax, app, figure)
        return
    
    # Daten sortieren und für matplotlib aufbereiten
    dates = []
    counts = []
    for date_str, count in sorted(timeline.items()):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        dates.append(date_obj)
        counts.append(count)
    
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
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    
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
    
    # Beschriftungen
    ax.set_title("Dokumentenaufkommen im Zeitverlauf")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Anzahl")
    
    # Dark Theme anwenden
    _apply_dark_theme(ax, app, figure)
    
    # Beschriftungen rotieren - KORRIGIERT
    figure.autofmt_xdate(rotation=45)
    
    # Layout anpassen
    figure.tight_layout()