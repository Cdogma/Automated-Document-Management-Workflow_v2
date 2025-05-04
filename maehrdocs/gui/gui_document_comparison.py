"""
Dokumentenvergleich für MaehrDocs
Enthält Funktionen zum Vergleichen von PDF-Dokumenten
"""

import os
import tkinter as tk
from tkinter import scrolledtext
import threading

from .gui_buttons import create_button
from .gui_document_loader import load_document_content

def compare_documents(app, original_file, duplicate_file):
    """
    Öffnet ein Fenster zum visuellen Vergleich zweier Dokumente
    
    Args:
        app: Instanz der GuiApp
        original_file: Pfad zur Originaldatei
        duplicate_file: Pfad zur Duplikatdatei
    """
    compare_window = tk.Toplevel(app.root)
    compare_window.title(f"Dokumentenvergleich")
    compare_window.geometry("1200x800")
    compare_window.configure(bg=app.colors["background_dark"])
    
    compare_frame = tk.Frame(
        compare_window, 
        bg=app.colors["background_medium"], 
        padx=15, 
        pady=15
    )
    compare_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Überschrift
    header = tk.Label(
        compare_frame, 
        text="Dokumentenvergleich", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    header.pack(anchor=tk.W, pady=(0, 15))
    
    # Zwei Spalten für die Dokumente
    docs_frame = tk.Frame(compare_frame, bg=app.colors["background_medium"])
    docs_frame.pack(fill=tk.BOTH, expand=True)
    
    # Linke Spalte - Original
    left_frame = create_document_panel(
        app, 
        docs_frame, 
        f"Original: {os.path.basename(original_file)}"
    )
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    # Rechte Spalte - Duplikat
    right_frame = create_document_panel(
        app, 
        docs_frame, 
        f"Duplikat: {os.path.basename(duplicate_file)}"
    )
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    # Button zum Schließen
    close_btn = create_button(
        app,
        compare_frame, 
        "Fenster schließen", 
        compare_window.destroy
    )
    close_btn.pack(anchor=tk.E, pady=10)
    
    # Inhalt der Dokumente in einem Thread laden
    threading.Thread(
        target=load_and_compare_contents, 
        args=(app, original_file, duplicate_file, left_frame.text, right_frame.text)
    ).start()
    
    return compare_window

def create_document_panel(app, parent, title):
    """
    Erstellt ein Panel für die Anzeige eines Dokuments
    
    Args:
        app: Instanz der GuiApp
        parent: Parent-Widget
        title: Titel des Panels
        
    Returns:
        tk.Frame: Das erstellte Panel
    """
    panel = tk.Frame(
        parent, 
        bg=app.colors["card_background"], 
        padx=10, 
        pady=10
    )
    
    header = tk.Label(
        panel, 
        text=title, 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    header.pack(anchor=tk.W, pady=(0, 10))
    
    text = scrolledtext.ScrolledText(
        panel, 
        bg=app.colors["background_dark"],
        fg=app.colors["text_primary"],
        font=app.fonts["code"]
    )
    text.pack(fill=tk.BOTH, expand=True)
    
    # Speichere Textfeld als Attribut
    panel.text = text
    
    return panel

def load_and_compare_contents(app, original_file, duplicate_file, left_text, right_text):
    """
    Lädt den Inhalt der Dokumente und hebt Unterschiede hervor
    
    Args:
        app: Instanz der GuiApp
        original_file: Pfad zur Originaldatei
        duplicate_file: Pfad zur Duplikatdatei
        left_text: Textfeld für die Originaldatei
        right_text: Textfeld für die Duplikatdatei
    """
    try:
        # Original-Dokument laden
        load_document_content(app, original_file, left_text)
        
        # Duplikat-Dokument laden
        load_document_content(app, duplicate_file, right_text)
        
        # Unterschiede hervorheben
        highlight_differences(app, left_text, right_text)
        
    except Exception as e:
        app.log(f"Fehler beim Laden der Dokumenteninhalte: {str(e)}", level="error")

def highlight_differences(app, left_text, right_text):
    """
    Hebt Unterschiede zwischen zwei Textfenstern hervor
    
    Args:
        app: Instanz der GuiApp
        left_text: Textfeld mit dem Originaltext
        right_text: Textfeld mit dem Vergleichstext
    """
    try:
        # Text aus beiden Widgets holen
        left_text.config(state=tk.NORMAL)
        right_text.config(state=tk.NORMAL)
        
        left_content = left_text.get(1.0, tk.END)
        right_content = right_text.get(1.0, tk.END)
        
        # Texte in Zeilen aufteilen
        left_lines = left_content.splitlines()
        right_lines = right_content.splitlines()
        
        # Unterschiede finden
        import difflib
        differ = difflib.Differ()
        diff = list(differ.compare(left_lines, right_lines))
        
        # Text löschen und neu einfügen
        left_text.delete(1.0, tk.END)
        right_text.delete(1.0, tk.END)
        
        # Tags für die Formatierung erstellen
        left_text.tag_configure("difference", background=app.colors["error"], foreground="white")
        right_text.tag_configure("difference", background=app.colors["error"], foreground="white")
        
        # Unterschiedliche Zeilen hervorheben
        for line in diff:
            if line.startswith('  '):  # Gemeinsame Zeile
                left_text.insert(tk.END, line[2:] + "\n")
                right_text.insert(tk.END, line[2:] + "\n")
            elif line.startswith('- '):  # Nur links
                left_text.insert(tk.END, line[2:] + "\n", "difference")
            elif line.startswith('+ '):  # Nur rechts
                right_text.insert(tk.END, line[2:] + "\n", "difference")
        
        left_text.config(state=tk.DISABLED)
        right_text.config(state=tk.DISABLED)
        
    except Exception as e:
        app.log(f"Fehler beim Hervorheben von Unterschieden: {str(e)}", level="error")