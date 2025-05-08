"""
Interaktive Funktionen für die Statistikvisualisierung in MaehrDocs
Enthält Event-Handler und Detailansichten für die Benutzerinteraktion mit Charts.
"""

import tkinter as tk
import logging
import matplotlib
from datetime import datetime
from . import gui_charts_core as core

def register_chart_events(figure, canvas, ax, app, chart_type):
    """
    Registriert Klick-Events für ein Chart.
    
    Args:
        figure: Die matplotlib-Figur
        canvas: Das FigureCanvasTkAgg-Objekt
        ax: Die Achse mit dem Chart
        app: Die GuiApp-Instanz
        chart_type: Typ des Charts (z.B. 'type', 'sender', 'size', 'timeline')
        
    Returns:
        int: ID des registrierten Event-Handlers
    """
    try:
        def on_click(event):
            # Ignoriere Klicks außerhalb der Achsen
            if event.inaxes != ax:
                return
                
            # Verschiedene Logik je nach Chart-Typ
            if chart_type == 'type':
                handle_type_chart_click(event, ax, app)
            elif chart_type == 'sender':
                handle_sender_chart_click(event, ax, app)
            elif chart_type == 'size':
                handle_size_chart_click(event, ax, app)
            elif chart_type == 'timeline':
                handle_timeline_chart_click(event, ax, app)
        
        # Event-Handler registrieren
        cid = canvas.mpl_connect('button_press_event', on_click)
        return cid
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Registrieren von Chart-Events: {str(e)}")
        return -1

def handle_type_chart_click(event, ax, app):
    """
    Behandelt Klicks auf das Typ-Chart.
    
    Args:
        event: Das Maus-Event
        ax: Die Achse mit dem Chart
        app: Die GuiApp-Instanz
    """
    try:
        if not hasattr(ax, 'type_data'):
            return
            
        # Prüfen, welcher Balken angeklickt wurde
        for artist in ax.containers:
            for i, bar in enumerate(artist):
                contains, _ = bar.contains(event)
                if contains:
                    # Entsprechenden Typ-Namen finden
                    type_names = list(ax.type_data.keys())
                    if i < len(type_names):
                        selected_type = type_names[i]
                        count = ax.type_data[selected_type]
                        
                        # Detailfenster öffnen
                        show_type_details(app, selected_type, count)
                        return
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei Typ-Chart-Klick: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Typ-Details: {str(e)}", 
            level="error"
        )

def handle_sender_chart_click(event, ax, app):
    """
    Behandelt Klicks auf das Absender-Chart.
    
    Args:
        event: Das Maus-Event
        ax: Die Achse mit dem Chart
        app: Die GuiApp-Instanz
    """
    try:
        if not hasattr(ax, 'sender_data') or not hasattr(ax, 'wedges'):
            return
            
        # Prüfen, welches Kuchenstück angeklickt wurde
        for i, wedge in enumerate(ax.wedges):
            contains, _ = wedge.contains(event)
            if contains:
                # Entsprechenden Absender-Namen finden
                sender_names = list(ax.sender_data.keys())
                if i < len(sender_names):
                    selected_sender = sender_names[i]
                    count = ax.sender_data[selected_sender]
                    
                    # Dokumente für diesen Absender filtern
                    documents = []
                    if hasattr(ax, 'documents'):
                        documents = [doc for doc in ax.documents if doc.get('sender') == selected_sender]
                    
                    # Detailfenster öffnen
                    show_sender_details(app, selected_sender, count, documents)
                    return
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei Absender-Chart-Klick: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Absender-Details: {str(e)}", 
            level="error"
        )

def handle_size_chart_click(event, ax, app):
    """
    Behandelt Klicks auf das Größen-Chart.
    
    Args:
        event: Das Maus-Event
        ax: Die Achse mit dem Chart
        app: Die GuiApp-Instanz
    """
    try:
        if not hasattr(ax, 'size_data'):
            return
            
        # Prüfen, welcher Balken angeklickt wurde
        for artist in ax.containers:
            for i, bar in enumerate(artist):
                contains, _ = bar.contains(event)
                if contains:
                    # Entsprechende Größenkategorie finden
                    size_categories = list(ax.size_data.keys())
                    if i < len(size_categories):
                        selected_size = size_categories[i]
                        count = ax.size_data[selected_size]
                        
                        # Dokumente für diese Größenkategorie filtern
                        documents = []
                        if hasattr(ax, 'documents'):
                            # Größenkategorie aus gui_statistics_data.py-Logik nachbilden
                            documents = [
                                doc for doc in ax.documents 
                                if categorize_size(doc.get('size', 0)) == selected_size
                            ]
                        
                        # Detailfenster öffnen
                        show_size_details(app, selected_size, count, documents)
                        return
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei Größen-Chart-Klick: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Größen-Details: {str(e)}", 
            level="error"
        )

def handle_timeline_chart_click(event, ax, app):
    """
    Behandelt Klicks auf das Zeitverlauf-Chart.
    
    Args:
        event: Das Maus-Event
        ax: Die Achse mit dem Chart
        app: Die GuiApp-Instanz
    """
    try:
        if not hasattr(ax, 'timeline_data') or not hasattr(ax, 'dates') or not hasattr(ax, 'counts'):
            return
            
        # Testen, ob wir in der Nähe eines Datenpunkts sind
        min_distance = float('inf')
        closest_idx = -1
        
        for i, (date, count) in enumerate(zip(ax.dates, ax.counts)):
            # X-Koordinaten in Dateneinheiten
            date_num = matplotlib.dates.date2num(date)
            # Umwandeln der Klick-Position in Datenkoordinaten
            click_x_data = event.xdata
            click_y_data = event.ydata
            
            # Berechne Abstand (quadratische Distanz) zum Datenpunkt
            distance = (date_num - click_x_data)**2 + (count - click_y_data)**2
            
            if distance < min_distance:
                min_distance = distance
                closest_idx = i
        
        # Wenn ein naher Punkt gefunden wurde und die Distanz gering genug ist
        threshold = 0.04  # Schwellenwert für Klickgenauigkeit
        if closest_idx >= 0 and min_distance < threshold:
            selected_date = ax.dates[closest_idx]
            count = ax.counts[closest_idx]
            
            # Original-Datums-String suchen
            date_str = selected_date.strftime("%Y-%m-%d")  # Fallback
            if hasattr(ax, 'date_dict') and selected_date in ax.date_dict:
                date_str = ax.date_dict[selected_date]
            
            # Dokumente für dieses Datum filtern
            documents = []
            if hasattr(ax, 'documents'):
                # Toleranz für Datumsvergleich (manchmal können Datumskonvertierungen ungenau sein)
                documents = []
                for doc in ax.documents:
                    if hasattr(doc.get('mtime'), 'strftime'):
                        doc_date_str = doc['mtime'].strftime("%Y-%m-%d")
                        if doc_date_str == date_str:
                            documents.append(doc)
            
            # Detailfenster öffnen
            show_timeline_details(app, selected_date, date_str, count, documents)
            return
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei Zeitverlauf-Chart-Klick: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Zeitverlauf-Details: {str(e)}", 
            level="error"
        )

# Hilfsfunktion wird hier definiert (statt separat importiert)
def categorize_size(file_size):
    """
    Kategorisiert eine Dateigröße in eine Größenkategorie.
    
    Args:
        file_size: Dateigröße in MB
        
    Returns:
        str: Größenkategorie
    """
    if file_size < 0.5:
        return "<0.5 MB"
    elif file_size < 1:
        return "0.5-1 MB"
    elif file_size < 5:
        return "1-5 MB"
    else:
        return ">5 MB"
        
# --- Hier kommen die Aufruf-Funktionen für die Detail-Dialoge ---

def show_type_details(app, type_name, count):
    """Zeigt Details für einen ausgewählten Dokumenttyp an."""
    data = {"type": type_name, "count": count}
    title = f"Details für Dokumenttyp: {type_name}"
    core.create_detail_dialog(app, title, data, 'type')

def show_sender_details(app, sender_name, count, documents):
    """Zeigt Details für einen ausgewählten Absender an."""
    data = {
        "sender": sender_name,
        "count": count,
        "documents": documents
    }
    title = f"Details für Absender: {sender_name}"
    core.create_detail_dialog(app, title, data, 'sender')

def show_size_details(app, size_category, count, documents):
    """Zeigt Details für eine ausgewählte Größenkategorie an."""
    data = {
        "size_category": size_category,
        "count": count,
        "documents": documents
    }
    title = f"Details für Größenkategorie: {size_category}"
    core.create_detail_dialog(app, title, data, 'size')

def show_timeline_details(app, date, date_str, count, documents):
    """Zeigt Details für ein ausgewähltes Datum an."""
    formatted_date = date.strftime("%d.%m.%Y")
    data = {
        "date": date,
        "date_str": date_str,
        "formatted_date": formatted_date,
        "count": count,
        "documents": documents
    }
    title = f"Details für Datum: {formatted_date}"
    core.create_detail_dialog(app, title, data, 'timeline')