"""
Kern-Dialog-Funktionen für Charts in MaehrDocs
Enthält die Basisfunktionalität zum Erstellen von Detail-Dialogs für Chart-Elemente.
"""

import tkinter as tk
import logging

def create_detail_dialog(app, title, data, chart_type):
    """
    Erstellt ein Detailfenster für ein geklicktes Chart-Element.
    
    Args:
        app: Die GuiApp-Instanz
        title: Titel des Dialogs
        data: Die anzuzeigenden Daten
        chart_type: Typ des Charts ('type', 'sender', 'size', 'timeline')
    """
    try:
        detail_window = tk.Toplevel(app.root)
        detail_window.title(title)
        detail_window.configure(bg=app.colors["background_medium"])
        
        # Dialog modal machen
        detail_window.transient(app.root)
        detail_window.grab_set()
        
        # Größe setzen
        detail_window.geometry("500x400")
        
        # Hauptframe
        main_frame = tk.Frame(detail_window, bg=app.colors["card_background"], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header erstellen
        header = tk.Label(
            main_frame,
            text=title,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        )
        header.pack(pady=(0, 15))
        
        # Inhalt basierend auf Chart-Typ laden
        _load_dialog_content(main_frame, data, chart_type, app)
        
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
        
        # Focus setzen
        detail_window.focus_set()
        
        # Dialog zentrieren
        _center_dialog(detail_window, app.root)
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Erstellen des Detail-Dialogs: {str(e)}")
        app.messaging.notify(
            f"Fehler beim Anzeigen der Details: {str(e)}", 
            level="error"
        )

def _load_dialog_content(frame, data, chart_type, app):
    """
    Lädt den Content für einen Dialog basierend auf dem Chart-Typ.
    
    Args:
        frame: Der Container-Frame
        data: Die anzuzeigenden Daten
        chart_type: Typ des Charts
        app: Die GuiApp-Instanz
    """
    # Import hier um zirkuläre Abhängigkeiten zu vermeiden
    from .gui_charts_dialog_type import fill_type_detail
    from .gui_charts_dialog_sender import fill_sender_detail
    from .gui_charts_dialog_size import fill_size_detail
    from .gui_charts_dialog_timeline import fill_timeline_detail
    
    # Laden des entsprechenden Contents
    if chart_type == 'type':
        fill_type_detail(frame, data, app)
    elif chart_type == 'sender':
        fill_sender_detail(frame, data, app)
    elif chart_type == 'size':
        fill_size_detail(frame, data, app)
    elif chart_type == 'timeline':
        fill_timeline_detail(frame, data, app)
    else:
        # Fallback für unbekannte Chart-Typen
        tk.Label(
            frame,
            text=f"Unbekannter Chart-Typ: {chart_type}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

def _center_dialog(dialog, parent):
    """
    Zentriert ein Dialog über einem Parent-Fenster.
    
    Args:
        dialog: Das zu zentrierende Dialogfenster
        parent: Das Parent-Fenster
    """
    # Aktualisiere die Fenstergeometrie
    dialog.update_idletasks()
    
    # Hole die Dimensionen
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    
    # Berechne die Position
    x = (parent.winfo_width() // 2) - (width // 2) + parent.winfo_x()
    y = (parent.winfo_height() // 2) - (height // 2) + parent.winfo_y()
    
    # Setze die Position
    dialog.geometry(f"{width}x{height}+{x}+{y}")

def create_info_section(frame, app, title, content, icon=None):
    """
    Erstellt einen Informationsbereich mit optionalem Icon.
    
    Args:
        frame: Container-Frame
        app: GuiApp-Instanz
        title: Titel des Bereichs
        content: Textinhalt
        icon: Optionales Icon
    """
    # Info-Frame
    info_frame = tk.Frame(frame, bg=app.colors["card_background"])
    info_frame.pack(fill=tk.X, pady=10)
    
    # Icon, falls vorhanden
    if icon:
        icon_label = tk.Label(
            info_frame,
            text=icon,
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
    
    # Text-Container
    text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
    text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Titel
    if title:
        tk.Label(
            text_frame,
            text=title,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
    
    # Inhalt
    tk.Label(
        text_frame,
        text=content,
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack(anchor=tk.W)
    
    return info_frame

def create_document_list(frame, app, documents, title="Dokumente"):
    """
    Erstellt eine scrollbare Liste mit Dokumenten.
    
    Args:
        frame: Container-Frame
        app: GuiApp-Instanz
        documents: Liste der Dokumente
        title: Überschrift für die Liste
    """
    # Überschrift
    tk.Label(
        frame,
        text=title,
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack(anchor=tk.W, pady=(15, 5))
    
    # Liste erstellen
    list_frame = tk.Frame(frame, bg=app.colors["background_medium"])
    list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Listbox
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
        
        # Alternierende Farben
        if i % 2 == 0:
            listbox.itemconfig(i, bg=app.colors["background_medium"])
        else:
            listbox.itemconfig(i, bg=app.colors["background_dark"])
    
    return listbox