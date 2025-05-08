"""
Kernkomponenten für Chart-Funktionen in MaehrDocs
Enthält grundlegende Funktionen und Hilfsmethoden, die von allen Chart-Typen 
verwendet werden, einschließlich Chart-Erstellung, Theme-Anwendung und 
Fehlerbehandlung.
"""

import matplotlib
matplotlib.use("TkAgg")  
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
import tkinter as tk
from tkinter import ttk

# Globale Matplotlib-Einstellungen für dunkles Theme
matplotlib.rcParams.update({
    'figure.facecolor': '#161B22',
    'axes.facecolor': '#161B22',
    'savefig.facecolor': '#161B22',
    'text.color': '#F9FAFB',
    'axes.labelcolor': '#F9FAFB',
    'xtick.color': '#F9FAFB',
    'ytick.color': '#F9FAFB',
    'grid.color': '#9CA3AF',
    'grid.alpha': 0.2,
    'lines.color': '#3B82F6',
})

# Globale Variablen für interaktive Charts
active_tooltips = {}

def create_chart_figure(app, parent_frame):
    """
    Erstellt eine neue matplotlib-Figur und Canvas für Charts mit Dark-Theme-Unterstützung.
    """
    try:
        figure = Figure(figsize=(5, 4), dpi=100)
        figure.patch.set_facecolor(app.colors["background_medium"])
        
        canvas = FigureCanvasTkAgg(figure, master=parent_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.get_tk_widget().configure(bg=app.colors["background_medium"])
        
        return figure, canvas
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Erstellen des Chart-Figure: {str(e)}")
        empty_figure = Figure(figsize=(5, 4), dpi=100)
        empty_figure.patch.set_facecolor(app.colors["background_medium"])
        empty_canvas = FigureCanvasTkAgg(empty_figure, master=parent_frame)
        empty_canvas.get_tk_widget().pack(fill="both", expand=True)
        empty_canvas.get_tk_widget().configure(bg=app.colors["background_medium"])
        return empty_figure, empty_canvas

def apply_dark_theme(ax, app, figure):
    """
    Wendet Dark-Theme-Styling auf ein Achsenobjekt an.
    """
    try:
        bg_color = app.colors["background_medium"]
        text_color = app.colors["text_primary"]
        
        ax.set_facecolor(bg_color)
        ax.title.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        
        for tick in ax.get_xticklabels():
            tick.set_color(text_color)
        for tick in ax.get_yticklabels():
            tick.set_color(text_color)
        
        for spine in ax.spines.values():
            spine.set_edgecolor(app.colors["text_secondary"])
            spine.set_alpha(0.3)
        
        ax.tick_params(axis='x', colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        
        if ax.get_xgridlines():
            for line in ax.get_xgridlines():
                line.set_color(app.colors["text_secondary"])
                line.set_alpha(0.1)
        
        if ax.get_ygridlines():
            for line in ax.get_ygridlines():
                line.set_color(app.colors["text_secondary"])
                line.set_alpha(0.1)
        
        legend = ax.get_legend()
        if legend:
            legend.get_frame().set_facecolor(bg_color)
            legend.get_frame().set_alpha(0.8)
            for text in legend.get_texts():
                text.set_color(text_color)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Fehler beim Anwenden des Dark-Themes: {str(e)}")

def handle_empty_data(ax, app, message="Keine Daten verfügbar"):
    """
    Zeigt eine Nachricht an, wenn keine Daten für ein Chart verfügbar sind.
    """
    try:
        ax.clear()
        ax.set_axis_off()
        
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
        try:
            ax.clear()
            ax.text(0.5, 0.5, "Fehler: Keine Daten", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
        except:
            pass

def add_tooltip(figure, ax, element, text):
    """
    Fügt einem Chart-Element einen Tooltip hinzu.
    """
    try:
        tooltip = ax.annotate(
            text,
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", 
                     fc="white", 
                     ec="gray", 
                     alpha=0.9),
            fontsize=10,
            color="black",
            visible=False
        )
        
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
        
        cid = figure.canvas.mpl_connect('motion_notify_event', on_hover)
        
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
    """
    try:
        detail_window = tk.Toplevel(app.root)
        detail_window.title(title)
        detail_window.configure(bg=app.colors["background_medium"])
        
        detail_window.transient(app.root)
        detail_window.grab_set()
        
        detail_window.geometry("500x400")
        
        main_frame = tk.Frame(detail_window, bg=app.colors["card_background"], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        detail_window.focus_set()
        
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
    """Füllt den Detail-Dialog für einen Dokumenttyp mit Inhalten."""
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

def _fill_sender_detail(frame, data, app):
    """Füllt den Detail-Dialog für einen Absender mit Inhalten."""
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

def _fill_size_detail(frame, data, app):
    """Füllt den Detail-Dialog für eine Größenkategorie mit Inhalten."""
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

def _fill_timeline_detail(frame, data, app):
    """Füllt den Detail-Dialog für ein Datum mit Inhalten."""
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