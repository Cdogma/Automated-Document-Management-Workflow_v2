"""
Chart-Funktionen für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen zum Erstellen und Aktualisieren verschiedener Chart-Typen
für die statistische Auswertung von Dokumenten.
"""

import matplotlib
matplotlib.use("TkAgg")  # Muss vor weiteren matplotlib-Imports stehen
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime

def create_chart_figure(app, parent_frame):
    """
    Erstellt eine neue matplotlib-Figur und Canvas für Charts.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        parent_frame: Das übergeordnete Frame für das Canvas
        
    Returns:
        tuple: (Figure, FigureCanvasTkAgg) Die erstellte Figur und Canvas
    """
    # Neue Figur erstellen
    figure = Figure(figsize=(5, 4), dpi=100)
    figure.patch.set_facecolor(app.colors["background_medium"])
    
    # Canvas erstellen und einbetten
    canvas = FigureCanvasTkAgg(figure, master=parent_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    
    return figure, canvas

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
        return
    
    # Nach Anzahl sortieren (absteigend)
    sorted_types = dict(sorted(types.items(), key=lambda item: item[1], reverse=True))
    
    # Farbpalette für die Balken
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
    
    # Beschriftungen
    ax.set_title("Dokumentenverteilung nach Typ")
    ax.set_xlabel("Dokumenttyp")
    ax.set_ylabel("Anzahl")
    
    # X-Achsen-Beschriftungen rotieren für bessere Lesbarkeit
    ax.set_xticklabels(sorted_types.keys(), rotation=45, ha='right')
    
    # Zahlen über den Balken anzeigen
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),  # 3 Punkte Offset
                   textcoords="offset points",
                   ha='center', va='bottom',
                   color=app.colors["text_primary"])
    
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
        return
    
    # Nach Anzahl sortieren (absteigend)
    sorted_senders = dict(sorted(senders.items(), key=lambda item: item[1], reverse=True))
    
    # Begrenzen auf die Top 10
    if len(sorted_senders) > 10:
        top_senders = dict(list(sorted_senders.items())[:9])
        other_count = sum(dict(list(sorted_senders.items())[9:]).values())
        top_senders["Andere"] = other_count
        sorted_senders = top_senders
    
    # Kreisdiagramm erstellen
    wedges, texts, autotexts = ax.pie(
        sorted_senders.values(),
        autopct='%1.1f%%',
        textprops={'color': app.colors["text_primary"]},
        wedgeprops={'width': 0.5}  # Für einen Donut-Chart
    )
    
    # Legende hinzufügen
    ax.legend(
        wedges,
        sorted_senders.keys(),
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=False,
        labelcolor=app.colors["text_primary"]
    )
    
    # Beschriftung
    ax.set_title("Dokumentenverteilung nach Absender")
    
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
        return
    
    # Größenkategorien in der richtigen Reihenfolge
    size_order = ["<0.5 MB", "0.5-1 MB", "1-5 MB", ">5 MB"]
    ordered_sizes = {}
    for category in size_order:
        if category in sizes:
            ordered_sizes[category] = sizes[category]
        else:
            ordered_sizes[category] = 0
    
    # Farbpalette
    colors = [
        app.colors["success"],
        app.colors["primary"],
        app.colors["warning"],
        app.colors["error"]
    ]
    
    # Balkendiagramm erstellen
    bars = ax.bar(
        ordered_sizes.keys(),
        ordered_sizes.values(),
        color=colors[:len(ordered_sizes)]
    )
    
    # Beschriftungen
    ax.set_title("Dokumentenverteilung nach Größe")
    ax.set_xlabel("Dokumentgröße")
    ax.set_ylabel("Anzahl")
    
    # Zahlen über den Balken anzeigen
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                   xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 3),  # 3 Punkte Offset
                   textcoords="offset points",
                   ha='center', va='bottom',
                   color=app.colors["text_primary"])
    
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
        return
    
    # Daten sortieren und für matplotlib aufbereiten
    dates = []
    counts = []
    for date_str, count in sorted(timeline.items()):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        dates.append(date_obj)
        counts.append(count)
    
    # Linienchart erstellen
    ax.plot(
        dates, counts,
        marker='o',
        linestyle='-',
        color=app.colors["primary"],
        markersize=5,
        markerfacecolor=app.colors["accent"]
    )
    
    # Datumsformatierung
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # Wenn mehr als 7 Datumspunkte, nur einige anzeigen
    if len(dates) > 7:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    
    # Beschriftungen rotieren
    plt = ax.figure.canvas.figure
    plt.autofmt_xdate(rotation=45)
    
    # Beschriftungen
    ax.set_title("Dokumentenaufkommen im Zeitverlauf")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Anzahl")
    
    # Layout anpassen
    figure.tight_layout()