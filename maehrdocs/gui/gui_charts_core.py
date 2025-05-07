"""
Kernkomponenten für Chart-Funktionen in MaehrDocs
Enthält grundlegende Funktionen und Hilfsmethoden, die von allen Chart-Typen 
verwendet werden, einschließlich Chart-Erstellung, Theme-Anwendung und 
Fehlerbehandlung.

Diese Datei dient als Basis für alle Chart-Darstellungen und stellt einen
einheitlichen Stil und robuste Fehlerbehandlung für die gesamte
Statistikvisualisierung sicher.
"""

import matplotlib
matplotlib.use("TkAgg")  # Muss vor weiteren matplotlib-Imports stehen
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging

# Globale Variablen für interaktive Charts
active_tooltips = {}  # Speichert aktive Tooltips, um sie später entfernen zu können

def create_chart_figure(app, parent_frame):
    """
    Erstellt eine neue matplotlib-Figur und Canvas für Charts mit Dark-Theme-Unterstützung.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        parent_frame: Das übergeordnete Frame für das Canvas
        
    Returns:
        tuple: (Figure, FigureCanvasTkAgg) Die erstellte Figur und Canvas
    """
    try:
        # Neue Figur erstellen
        figure = Figure(figsize=(5, 4), dpi=100)
        
        # Dark Theme Anpassungen
        bg_color = app.colors["background_medium"]
        
        figure.patch.set_facecolor(bg_color)
        
        # Canvas erstellen und einbetten
        canvas = FigureCanvasTkAgg(figure, master=parent_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        return figure, canvas
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Erstellen des Chart-Figure: {str(e)}")
        # Fallback: Leere Figure und Canvas
        empty_figure = Figure(figsize=(5, 4), dpi=100)
        empty_canvas = FigureCanvasTkAgg(empty_figure, master=parent_frame)
        empty_canvas.get_tk_widget().pack(fill="both", expand=True)
        return empty_figure, empty_canvas

def apply_dark_theme(ax, app, figure):
    """
    Wendet Dark-Theme-Styling auf ein Achsenobjekt an.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        app: Die Hauptanwendung (GuiApp-Instanz)
        figure: Die matplotlib-Figur, die die Achse enthält
    """
    try:
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
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Fehler beim Anwenden des Dark-Themes: {str(e)}")
        # Kein Fallback nötig, da dies nur das Styling betrifft

def handle_empty_data(ax, app, message="Keine Daten verfügbar"):
    """
    Zeigt eine Nachricht an, wenn keine Daten für ein Chart verfügbar sind.
    
    Args:
        ax: Die matplotlib-Achse für das Chart
        app: Die Hauptanwendung (GuiApp-Instanz)
        message: Die anzuzeigende Nachricht
    """
    try:
        ax.clear()  # Achse leeren
        ax.set_axis_off()  # Achsen ausblenden
        
        # Nachricht mit besserer Sichtbarkeit im Dark Mode anzeigen
        ax.text(0.5, 0.5, message, 
               horizontalalignment='center',
               verticalalignment='center',
               fontsize=12,
               color=app.colors["text_primary"],
               bbox=dict(boxstyle="round,pad=0.5", 
                         fc=app.colors["card_background"], 
                         ec=app.colors["text_secondary"],
                         alpha=0.7),
               transform=ax.transAxes)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Anzeigen der 'Keine Daten'-Nachricht: {str(e)}")
        # Notfall-Fallback: Einfache Nachricht ohne Styling
        try:
            ax.clear()
            ax.text(0.5, 0.5, "Fehler: Keine Daten", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        except:
            pass  # Letzter Versuch gescheitert, nichts mehr zu tun

def add_tooltip(figure, ax, element, text):
    """
    Fügt einem Chart-Element einen Tooltip hinzu.
    
    Erstellt einen Tooltip, der beim Hovern über ein Chart-Element angezeigt wird.
    
    Args:
        figure: Die matplotlib-Figur
        ax: Die Achse mit dem Chart
        element: Das Element, zu dem der Tooltip hinzugefügt werden soll
        text: Der anzuzeigende Text
        
    Returns:
        Das Tooltip-Objekt (für späteres Entfernen)
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.offsetbox import AnnotationBbox, TextArea
        
        # Tooltip erstellen
        tooltip = ax.annotate(
            text,
            xy=(0, 0),  # Wird während des Hoverns aktualisiert
            xytext=(20, 20),  # Offset vom Cursor
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", 
                     fc="white", 
                     ec="gray", 
                     alpha=0.9),
            fontsize=10,
            color="black",
            visible=False  # Initial unsichtbar
        )
        
        # Event-Handler für Mouseover
        def on_hover(event):
            if event.inaxes == ax:
                contains, details = element.contains(event)
                if contains:
                    tooltip.set_visible(True)
                    tooltip.xy = (event.xdata, event.ydata)
                    figure.canvas.draw_idle()
                else:
                    if tooltip.get_visible():
                        tooltip.set_visible(False)
                        figure.canvas.draw_idle()
        
        # Event-Handler registrieren
        cid = figure.canvas.mpl_connect('motion_notify_event', on_hover)
        
        # Tooltip und Connection-ID in globalem Dict speichern
        global active_tooltips
        tooltip_id = id(element)
        active_tooltips[tooltip_id] = (tooltip, cid)
        
        return tooltip
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Fehler beim Hinzufügen eines Tooltips: {str(e)}")
        return None

def create_detail_dialog(app, title, data, chart_type):
    """
    Erstellt ein Detailfenster für ein geklicktes Chart-Element.
    
    Zeigt ein modales Dialog-Fenster mit detaillierten Informationen an.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        title: Titel des Dialogs
        data: Anzuzeigende Daten (Format abhängig vom Chart-Typ)
        chart_type: Typ des Charts (z.B. 'type', 'sender', 'size', 'timeline')
    """
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Neues Toplevel-Fenster erstellen
        detail_window = tk.Toplevel(app.root)
        detail_window.title(title)
        detail_window.configure(bg=app.colors["background_medium"])
        
        # Modal machen
        detail_window.transient(app.root)
        detail_window.grab_set()
        
        # Größe setzen
        detail_window.geometry("500x400")
        
        # Hauptframe
        main_frame = tk.Frame(detail_window, bg=app.colors["card_background"], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Label(
            main_frame,
            text=title,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        )
        header.pack(pady=(0, 15))
        
        # Inhalt je nach Chart-Typ
        if chart_type == 'type':
            _fill_type_detail(main_frame, data, app)
        elif chart_type == 'sender':
            _fill_sender_detail(main_frame, data, app)
        elif chart_type == 'size':
            _fill_size_detail(main_frame, data, app)
        elif chart_type == 'timeline':
            _fill_timeline_detail(main_frame, data, app)
        
        # Schließen-Button
        close_btn = tk.Button(
            main_frame,
            text="Schließen",
            font=app.fonts["normal"],
            bg=app.colors["primary"],
            fg=app.colors["text_primary"],
            relief=tk.FLAT,
            command=detail_window.destroy
        )
        close_btn.pack(pady=15)
        
        # Fenster in den Vordergrund
        detail_window.focus_set()
        
        # Position zentrieren
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (app.root.winfo_width() // 2) - (width // 2) + app.root.winfo_x()
        y = (app.root.winfo_height() // 2) - (height // 2) + app.root.winfo_y()
        detail_window.geometry(f"{width}x{height}+{x}+{y}")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Erstellen des Detail-Dialogs: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Details: {str(e)}", 
            level="error"
        )

def _fill_type_detail(frame, data, app):
    """Hilfsfunktion zum Füllen des Typ-Detail-Dialogs"""
    # Wird in gui_charts_interactive.py implementiert
    tk.Label(
        frame,
        text="Detailansicht wird geladen...",
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack()

def _fill_sender_detail(frame, data, app):
    """Hilfsfunktion zum Füllen des Absender-Detail-Dialogs"""
    # Wird in gui_charts_interactive.py implementiert
    tk.Label(
        frame,
        text="Detailansicht wird geladen...",
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack()

def _fill_size_detail(frame, data, app):
    """Hilfsfunktion zum Füllen des Größen-Detail-Dialogs"""
    # Wird in gui_charts_interactive.py implementiert
    tk.Label(
        frame,
        text="Detailansicht wird geladen...",
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack()

def _fill_timeline_detail(frame, data, app):
    """Hilfsfunktion zum Füllen des Zeitverlauf-Detail-Dialogs"""
    # Wird in gui_charts_interactive.py implementiert
    tk.Label(
        frame,
        text="Detailansicht wird geladen...",
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack()