"""
Größen-Detail-Dialog für Charts in MaehrDocs
Enthält Funktionen zum Anzeigen von Details für ausgewählte Größenkategorien.
"""

import tkinter as tk
from tkinter import ttk
import logging

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
            _show_size_statistics(frame, documents, app)
            _create_size_document_list(frame, documents, app)
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

def _show_size_statistics(frame, documents, app):
    """
    Zeigt Statistiken zur Dokumentgröße an.
    
    Args:
        frame: Container-Frame
        documents: Liste der Dokumente
        app: GuiApp-Instanz
    """
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

def _create_size_document_list(frame, documents, app):
    """
    Erstellt eine sortierbare Liste mit Dokumenten und deren Größen.
    
    Args:
        frame: Container-Frame
        documents: Liste der Dokumente
        app: GuiApp-Instanz
    """
    # Überschrift
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
        command=lambda: _open_selected_tree_document(app, tree, sorted_docs)
    )
    open_btn.pack(side=tk.LEFT, padx=5)
    
    # Event-Handler für Treeview-Auswahl
    def on_tree_select(event):
        if tree.selection():
            open_btn.config(state=tk.NORMAL)
        else:
            open_btn.config(state=tk.DISABLED)
    
    tree.bind('<<TreeviewSelect>>', on_tree_select)

def _open_selected_tree_document(app, tree, documents):
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