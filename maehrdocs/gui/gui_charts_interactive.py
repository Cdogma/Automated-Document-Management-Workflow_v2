"""
Interaktive Funktionen für die Statistikvisualisierung in MaehrDocs
Enthält Event-Handler und Detailansichten für die Benutzerinteraktion mit Charts.

Diese Datei implementiert die interaktiven Elemente der Statistikvisualisierung,
insbesondere Klick-Event-Handler für detaillierte Datenansichten und
Implementierungen der verschiedenen Detaildialoge.
"""

import tkinter as tk
from tkinter import ttk
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

def show_type_details(app, type_name, count):
    """
    Zeigt Details für einen ausgewählten Dokumenttyp an.
    
    Args:
        app: Die GuiApp-Instanz
        type_name: Name des Dokumenttyps
        count: Anzahl der Dokumente dieses Typs
    """
    try:
        # Detailierte Daten für den Dialog
        data = {
            "type": type_name,
            "count": count
        }
        
        # Dialog-Titel
        title = f"Details für Dokumenttyp: {type_name}"
        
        # Detail-Dialog anzeigen
        core.create_detail_dialog(app, title, data, 'type')
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Anzeigen der Typ-Details: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Typ-Details: {str(e)}", 
            level="error"
        )

def show_sender_details(app, sender_name, count, documents):
    """
    Zeigt Details für einen ausgewählten Absender an.
    
    Args:
        app: Die GuiApp-Instanz
        sender_name: Name des Absenders
        count: Anzahl der Dokumente von diesem Absender
        documents: Liste der Dokumente von diesem Absender
    """
    try:
        # Detailierte Daten für den Dialog
        data = {
            "sender": sender_name,
            "count": count,
            "documents": documents
        }
        
        # Dialog-Titel
        title = f"Details für Absender: {sender_name}"
        
        # Detail-Dialog anzeigen
        core.create_detail_dialog(app, title, data, 'sender')
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Anzeigen der Absender-Details: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Absender-Details: {str(e)}", 
            level="error"
        )

def show_size_details(app, size_category, count, documents):
    """
    Zeigt Details für eine ausgewählte Größenkategorie an.
    
    Args:
        app: Die GuiApp-Instanz
        size_category: Größenkategorie (z.B. "<0.5 MB")
        count: Anzahl der Dokumente in dieser Größenkategorie
        documents: Liste der Dokumente in dieser Größenkategorie
    """
    try:
        # Detailierte Daten für den Dialog
        data = {
            "size_category": size_category,
            "count": count,
            "documents": documents
        }
        
        # Dialog-Titel
        title = f"Details für Größenkategorie: {size_category}"
        
        # Detail-Dialog anzeigen
        core.create_detail_dialog(app, title, data, 'size')
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Anzeigen der Größen-Details: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Größen-Details: {str(e)}", 
            level="error"
        )

def show_timeline_details(app, date, date_str, count, documents):
    """
    Zeigt Details für ein ausgewähltes Datum an.
    
    Args:
        app: Die GuiApp-Instanz
        date: Das Datum als datetime-Objekt
        date_str: Das Datum als String
        count: Anzahl der Dokumente an diesem Datum
        documents: Liste der Dokumente an diesem Datum
    """
    try:
        # Formatiertes Datum für Anzeige
        formatted_date = date.strftime("%d.%m.%Y")
        
        # Detailierte Daten für den Dialog
        data = {
            "date": date,
            "date_str": date_str,
            "formatted_date": formatted_date,
            "count": count,
            "documents": documents
        }
        
        # Dialog-Titel
        title = f"Details für Datum: {formatted_date}"
        
        # Detail-Dialog anzeigen
        core.create_detail_dialog(app, title, data, 'timeline')
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Anzeigen der Zeitverlauf-Details: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Zeitverlauf-Details: {str(e)}", 
            level="error"
        )

# Hilfsfunktion für die Größenkategorisierung (aus gui_statistics_data.py übernommen)
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

# Implementierungen der Detail-Dialog-Funktionen aus gui_charts_core.py
def fill_type_detail(frame, data, app):
    """
    Füllt den Detail-Dialog für einen Dokumenttyp mit Inhalten.
    
    Args:
        frame: Das übergeordnete Frame
        data: Die anzuzeigenden Daten
        app: Die GuiApp-Instanz
    """
    try:
        type_name = data.get("type", "Unbekannt")
        count = data.get("count", 0)
        
        # Basisdaten anzeigen
        info_frame = tk.Frame(frame, bg=app.colors["card_background"])
        info_frame.pack(fill=tk.X, pady=10)
        
        # Typ-Icon (symbolisch)
        icon_label = tk.Label(
            info_frame,
            text="📄",  # Dokumentsymbol
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
        
        # Textinformationen
        text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Typ-Name
        tk.Label(
            text_frame,
            text=type_name,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Anzahl
        tk.Label(
            text_frame,
            text=f"Dokumente: {count}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Prozentsatz-Berechnung könnte hier ergänzt werden, wenn die Gesamtzahl bekannt ist
        
        # Informationstext
        if count > 0:
            beschreibung = get_type_description(type_name)
            
            # Beschreibungsrahmen
            desc_frame = tk.Frame(frame, bg=app.colors["background_medium"], padx=10, pady=10)
            desc_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                desc_frame,
                text="Beschreibung:",
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W)
            
            tk.Label(
                desc_frame,
                text=beschreibung,
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"],
                wraplength=460,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=5)
            
            # Tipps
            tk.Label(
                frame,
                text="Tipps zur Verwendung:",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=(10, 5))
            
            tipps = [
                f"• Filterung: Nutzen Sie die Filteroptionen, um nur Dokumente vom Typ '{type_name}' anzuzeigen",
                f"• Sortierung: Dokumente vom Typ '{type_name}' können Sie im Dashboard nach Datum sortieren",
                f"• Archivierung: Bei {type_name}-Dokumenten empfiehlt sich eine Aufbewahrung von 10 Jahren"
            ]
            
            for tipp in tipps:
                tk.Label(
                    frame,
                    text=tipp,
                    font=app.fonts["small"],
                    bg=app.colors["card_background"],
                    fg=app.colors["text_primary"],
                    wraplength=460,
                    justify=tk.LEFT
                ).pack(anchor=tk.W, pady=2)
        else:
            # Keine Dokumente vorhanden
            tk.Label(
                frame,
                text="Keine Dokumente von diesem Typ vorhanden.",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["warning"]
            ).pack(pady=20)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Füllen des Typ-Detail-Dialogs: {str(e)}")
        
        # Fehleranzeige
        tk.Label(
            frame,
            text=f"Fehler beim Laden der Details: {str(e)}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

def fill_sender_detail(frame, data, app):
    """
    Füllt den Detail-Dialog für einen Absender mit Inhalten.
    
    Args:
        frame: Das übergeordnete Frame
        data: Die anzuzeigenden Daten
        app: Die GuiApp-Instanz
    """
    try:
        sender_name = data.get("sender", "Unbekannt")
        count = data.get("count", 0)
        documents = data.get("documents", [])
        
        # Basisdaten anzeigen
        info_frame = tk.Frame(frame, bg=app.colors["card_background"])
        info_frame.pack(fill=tk.X, pady=10)
        
        # Absender-Icon
        icon_label = tk.Label(
            info_frame,
            text="👤",  # Personen-/Organisationssymbol
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
        
        # Textinformationen
        text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Absender-Name
        tk.Label(
            text_frame,
            text=sender_name,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Anzahl
        tk.Label(
            text_frame,
            text=f"Dokumente: {count}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Dokumentenliste, falls Dokumente vorhanden sind
        if documents:
            # Überschrift
            tk.Label(
                frame,
                text="Dokumente:",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=(15, 5))
            
            # Scrollbare Liste
            list_frame = tk.Frame(frame, bg=app.colors["background_medium"])
            list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Listbox mit Dokumenten
            listbox = tk.Listbox(
                list_frame,
                font=app.fonts["small"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"],
                selectbackground=app.colors["primary"],
                selectforeground=app.colors["text_primary"],
                height=8,
                yscrollcommand=scrollbar.set
            )
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            # Dokumente einfügen
            for i, doc in enumerate(documents):
                filename = doc.get("filename", "Unbekannte Datei")
                listbox.insert(tk.END, filename)
                
                # Alternierende Farben für bessere Lesbarkeit
                if i % 2 == 0:
                    listbox.itemconfig(i, bg=app.colors["background_medium"])
                else:
                    listbox.itemconfig(i, bg=app.colors["background_dark"])
            
            # Funktionsbuttons unterhalb der Liste
            btn_frame = tk.Frame(frame, bg=app.colors["card_background"])
            btn_frame.pack(fill=tk.X, pady=10)
            
            # Öffnen-Button
            open_btn = tk.Button(
                btn_frame,
                text="Dokument öffnen",
                font=app.fonts["small"],
                bg=app.colors["primary"],
                fg=app.colors["text_primary"],
                relief=tk.FLAT,
                state=tk.DISABLED,  # Initial deaktiviert
                command=lambda: open_selected_document(app, listbox, documents)
            )
            open_btn.pack(side=tk.LEFT, padx=5)
            
            # Event-Handler für Listenauswahl
            def on_select(event):
                if listbox.curselection():
                    open_btn.config(state=tk.NORMAL)
                else:
                    open_btn.config(state=tk.DISABLED)
            
            listbox.bind('<<ListboxSelect>>', on_select)
            
        else:
            # Keine Dokumente vorhanden
            tk.Label(
                frame,
                text="Keine detaillierten Dokumentinformationen verfügbar.",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["warning"]
            ).pack(pady=20)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Füllen des Absender-Detail-Dialogs: {str(e)}")
        
        # Fehleranzeige
        tk.Label(
            frame,
            text=f"Fehler beim Laden der Details: {str(e)}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

def fill_size_detail(frame, data, app):
    """
    Füllt den Detail-Dialog für eine Größenkategorie mit Inhalten.
    
    Args:
        frame: Das übergeordnete Frame
        data: Die anzuzeigenden Daten
        app: Die GuiApp-Instanz
    """
    try:
        size_category = data.get("size_category", "Unbekannt")
        count = data.get("count", 0)
        documents = data.get("documents", [])
        
        # Basisdaten anzeigen
        info_frame = tk.Frame(frame, bg=app.colors["card_background"])
        info_frame.pack(fill=tk.X, pady=10)
        
        # Größen-Icon
        icon_label = tk.Label(
            info_frame,
            text="📏",  # Maßband-Symbol für Größe
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
        
        # Textinformationen
        text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Größenkategorie
        tk.Label(
            text_frame,
            text=f"Größenkategorie: {size_category}",
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Anzahl
        tk.Label(
            text_frame,
            text=f"Dokumente: {count}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Statistikinformationen
        if documents:
            # Gesamtgröße berechnen
            total_size = sum(doc.get("size", 0) for doc in documents)
            avg_size = total_size / len(documents) if len(documents) > 0 else 0
            
            # Statistikrahmen
            stats_frame = tk.Frame(frame, bg=app.colors["background_medium"], padx=10, pady=10)
            stats_frame.pack(fill=tk.X, pady=10)
            
            # Statistiken anzeigen
            tk.Label(
                stats_frame,
                text="Statistik:",
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W)
            
            # Gesamtgröße
            tk.Label(
                stats_frame,
                text=f"Gesamtgröße: {total_size:.2f} MB",
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=2)
            
            # Durchschnittsgröße
            tk.Label(
                stats_frame,
                text=f"Durchschnittsgröße: {avg_size:.2f} MB",
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=2)
            
            # Dokumentenliste
            tk.Label(
                frame,
                text="Dokumente (nach Größe sortiert):",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=(15, 5))
            
            # Sortiere Dokumente nach Größe (absteigend)
            sorted_docs = sorted(documents, key=lambda d: d.get("size", 0), reverse=True)
            
            # Treeview für sortierbare Liste
            columns = ("filename", "size", "date")
            
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
            tree.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Spaltenüberschriften
            tree.heading("filename", text="Dateiname")
            tree.heading("size", text="Größe (MB)")
            tree.heading("date", text="Datum")
            
            # Spaltenbreiten
            tree.column("filename", width=250)
            tree.column("size", width=100)
            tree.column("date", width=100)
            
            # Dokumente einfügen
            for i, doc in enumerate(sorted_docs):
                filename = doc.get("filename", "Unbekannte Datei")
                size = doc.get("size", 0)
                size_str = f"{size:.2f}"
                
                # Datum formatieren, falls vorhanden
                date_str = ""
                if "mtime" in doc and hasattr(doc["mtime"], "strftime"):
                    date_str = doc["mtime"].strftime("%d.%m.%Y")
                
                tree.insert("", tk.END, values=(filename, size_str, date_str))
                
                # Alternierende Farben für Treeview
                if i % 2 == 1:
                    tree.tag_configure('odd_row', background=app.colors["background_dark"])
                    tree.item(tree.get_children()[-1], tags=('odd_row',))
            
            # Funktionsbuttons unter der Liste
            btn_frame = tk.Frame(frame, bg=app.colors["card_background"])
            btn_frame.pack(fill=tk.X, pady=10)
            
            # Öffnen-Button
            open_btn = tk.Button(
                btn_frame,
                text="Dokument öffnen",
                font=app.fonts["small"],
                bg=app.colors["primary"],
                fg=app.colors["text_primary"],
                relief=tk.FLAT,
                state=tk.DISABLED,  # Initial deaktiviert
                command=lambda: open_selected_tree_document(app, tree, sorted_docs)
            )
            open_btn.pack(side=tk.LEFT, padx=5)
            
            # Event-Handler für Treeview-Auswahl
            def on_tree_select(event):
                if tree.selection():
                    open_btn.config(state=tk.NORMAL)
                else:
                    open_btn.config(state=tk.DISABLED)
            
            tree.bind('<<TreeviewSelect>>', on_tree_select)
            
        else:
            # Keine Dokumente vorhanden
            tk.Label(
                frame,
                text="Keine detaillierten Dokumentinformationen verfügbar.",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["warning"]
            ).pack(pady=20)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Füllen des Größen-Detail-Dialogs: {str(e)}")
        
        # Fehleranzeige
        tk.Label(
            frame,
            text=f"Fehler beim Laden der Details: {str(e)}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

def fill_timeline_detail(frame, data, app):
    """
    Füllt den Detail-Dialog für ein Datum mit Inhalten.
    
    Args:
        frame: Das übergeordnete Frame
        data: Die anzuzeigenden Daten
        app: Die GuiApp-Instanz
    """
    try:
        formatted_date = data.get("formatted_date", "Unbekanntes Datum")
        count = data.get("count", 0)
        documents = data.get("documents", [])
        
        # Basisdaten anzeigen
        info_frame = tk.Frame(frame, bg=app.colors["card_background"])
        info_frame.pack(fill=tk.X, pady=10)
        
        # Datums-Icon
        icon_label = tk.Label(
            info_frame,
            text="📅",  # Kalender-Symbol
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
        
        # Textinformationen
        text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Datum
        tk.Label(
            text_frame,
            text=formatted_date,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Anzahl
        tk.Label(
            text_frame,
            text=f"Dokumente: {count}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Dokumentenliste, falls Dokumente vorhanden sind
        if documents:
            # Überschrift
            tk.Label(
                frame,
                text="Dokumente an diesem Tag:",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W, pady=(15, 5))
            
            # Treeview für sortierbare Liste
            columns = ("filename", "type", "sender")
            
            tree = ttk.Treeview(frame, columns=columns, show="headings", height=6)
            tree.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Spaltenüberschriften
            tree.heading("filename", text="Dateiname")
            tree.heading("type", text="Typ")
            tree.heading("sender", text="Absender")
            
            # Spaltenbreiten
            tree.column("filename", width=250)
            tree.column("type", width=100)
            tree.column("sender", width=150)
            
            # Dokumente einfügen
            for i, doc in enumerate(documents):
                filename = doc.get("filename", "Unbekannte Datei")
                doc_type = doc.get("type", "")
                sender = doc.get("sender", "")
                
                tree.insert("", tk.END, values=(filename, doc_type, sender))
                
                # Alternierende Farben für Treeview
                if i % 2 == 1:
                    tree.tag_configure('odd_row', background=app.colors["background_dark"])
                    tree.item(tree.get_children()[-1], tags=('odd_row',))
            
            # Funktionsbuttons unter der Liste
            btn_frame = tk.Frame(frame, bg=app.colors["card_background"])
            btn_frame.pack(fill=tk.X, pady=10)
            
            # Öffnen-Button
            open_btn = tk.Button(
                btn_frame,
                text="Dokument öffnen",
                font=app.fonts["small"],
                bg=app.colors["primary"],
                fg=app.colors["text_primary"],
                relief=tk.FLAT,
                state=tk.DISABLED,  # Initial deaktiviert
                command=lambda: open_selected_tree_document(app, tree, documents)
            )
            open_btn.pack(side=tk.LEFT, padx=5)
            
            # Event-Handler für Treeview-Auswahl
            def on_tree_select(event):
                if tree.selection():
                    open_btn.config(state=tk.NORMAL)
                else:
                    open_btn.config(state=tk.DISABLED)
            
            tree.bind('<<TreeviewSelect>>', on_tree_select)
            
        else:
            # Keine Dokumente vorhanden
            tk.Label(
                frame,
                text="Keine detaillierten Dokumentinformationen verfügbar.",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["warning"]
            ).pack(pady=20)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Füllen des Zeitverlauf-Detail-Dialogs: {str(e)}")
        
        # Fehleranzeige
        tk.Label(
            frame,
            text=f"Fehler beim Laden der Details: {str(e)}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

# Hilfsfunktionen für die Detail-Dialoge

def open_selected_document(app, listbox, documents):
    """
    Öffnet das ausgewählte Dokument aus einer Listbox.
    
    Args:
        app: Die GuiApp-Instanz
        listbox: Die Listbox mit der Auswahl
        documents: Liste der Dokumente
    """
    try:
        # Index des ausgewählten Elements
        idx = listbox.curselection()[0]
        
        # Entsprechendes Dokument finden
        if idx < len(documents):
            doc = documents[idx]
            if "path" in doc:
                # Dokument öffnen (nutze bestehende Funktionalität)
                from maehrdocs.gui.gui_document_viewer import open_document
                open_document(app, doc["path"])
            else:
                app.messaging.notify(
                    "Pfad zum Dokument nicht verfügbar.", 
                    level="warning"
                )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Öffnen des Dokuments: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Öffnen des Dokuments: {str(e)}", 
            level="error"
        )

def open_selected_tree_document(app, tree, documents):
    """
    Öffnet das ausgewählte Dokument aus einem Treeview.
    
    Args:
        app: Die GuiApp-Instanz
        tree: Der Treeview mit der Auswahl
        documents: Liste der Dokumente
    """
    try:
        # ID des ausgewählten Elements
        selection = tree.selection()[0]
        
        # Index des ausgewählten Elements ermitteln
        idx = tree.index(selection)
        
        # Entsprechendes Dokument finden
        if idx < len(documents):
            doc = documents[idx]
            if "path" in doc:
                # Dokument öffnen (nutze bestehende Funktionalität)
                from maehrdocs.gui.gui_document_viewer import open_document
                open_document(app, doc["path"])
            else:
                app.messaging.notify(
                    "Pfad zum Dokument nicht verfügbar.", 
                    level="warning"
                )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Öffnen des Dokuments: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Öffnen des Dokuments: {str(e)}", 
            level="error"
        )

def get_type_description(type_name):
    """
    Gibt eine Beschreibung für einen Dokumenttyp zurück.
    
    Args:
        type_name: Name des Dokumenttyps
        
    Returns:
        str: Beschreibung des Dokumenttyps
    """
    # Standardbeschreibungen für einige gängige Dokumenttypen
    descriptions = {
        "Rechnung": "Eine Rechnung ist ein kaufmännisches Dokument, das die Forderung eines Verkäufers gegenüber dem Käufer über den Kaufpreis aus einem Kaufvertrag dokumentiert.",
        "Vertrag": "Ein Vertrag ist eine rechtlich bindende Vereinbarung zwischen zwei oder mehr Parteien.",
        "Brief": "Ein Brief ist ein schriftliches Dokument, das als Kommunikationsmittel zwischen Sender und Empfänger dient.",
        "Bescheid": "Ein Bescheid ist ein Verwaltungsakt einer Behörde, der rechtliche Wirkung entfaltet.",
        "Dokument": "Ein allgemeines Dokument, das Informationen in strukturierter Form enthält.",
        "Antrag": "Ein Antrag ist ein schriftliches Gesuch an eine Behörde oder Organisation.",
        "Meldung": "Eine Meldung ist eine offizielle Mitteilung oder Benachrichtigung."
    }
    
    # Fallback-Beschreibung
    return descriptions.get(
        type_name, 
        f"Keine spezifische Beschreibung für den Dokumenttyp '{type_name}' verfügbar."
    )

# Überschreiben der Funktionen aus gui_charts_core.py
core._fill_type_detail = fill_type_detail
core._fill_sender_detail = fill_sender_detail
core._fill_size_detail = fill_size_detail
core._fill_timeline_detail = fill_timeline_detail