"""
Absender-Detail-Dialog für Charts in MaehrDocs
Enthält Funktionen zum Anzeigen von Details für ausgewählte Absender.
"""

import tkinter as tk
import logging

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
            _create_sender_document_list(frame, documents, app)
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

def _create_sender_document_list(frame, documents, app):
    """
    Erstellt eine Liste mit Dokumenten für einen bestimmten Absender.
    
    Args:
        frame: Container-Frame
        documents: Liste der Dokumente
        app: GuiApp-Instanz
    """
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
        command=lambda: _open_selected_document(app, listbox, documents)
    )
    open_btn.pack(side=tk.LEFT, padx=5)
    
    # Event-Handler für Listenauswahl
    def on_select(event):
        if listbox.curselection():
            open_btn.config(state=tk.NORMAL)
        else:
            open_btn.config(state=tk.DISABLED)
    
    listbox.bind('<<ListboxSelect>>', on_select)

def _open_selected_document(app, listbox, documents):
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
                from .gui_document_viewer import open_document
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