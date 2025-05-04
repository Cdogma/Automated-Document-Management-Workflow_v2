"""
Dokumentenansicht und -vergleich für MaehrDocs
Enthält Funktionen zum Anzeigen und Vergleichen von PDF-Dokumenten
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from .gui_components import create_button

def open_document(app, file_path):
    """
    Öffnet ein Dokument mit dem Standardprogramm
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei
    """
    try:
        # Vollständigen Pfad bestimmen
        if not os.path.isabs(file_path):
            # Prüfen in verschiedenen Ordnern
            for folder in [
                app.config["paths"]["input_dir"], 
                app.config["paths"]["output_dir"], 
                app.config["paths"]["trash_dir"]
            ]:
                potential_path = os.path.join(folder, file_path)
                if os.path.exists(potential_path):
                    file_path = potential_path
                    break
        
        if os.path.exists(file_path):
            # Plattformabhängiges Öffnen der Datei
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS oder Linux
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', file_path])
        else:
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {file_path}")
            
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Öffnen der Datei: {str(e)}")
        app.log(f"Fehler beim Öffnen der Datei: {str(e)}", level="error")

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
    left_frame = tk.Frame(
        docs_frame, 
        bg=app.colors["card_background"], 
        padx=10, 
        pady=10
    )
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    left_header = tk.Label(
        left_frame, 
        text=f"Original: {os.path.basename(original_file)}", 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    left_header.pack(anchor=tk.W, pady=(0, 10))
    
    left_text = scrolledtext.ScrolledText(
        left_frame, 
        bg=app.colors["background_dark"],
        fg=app.colors["text_primary"],
        font=app.fonts["code"]
    )
    left_text.pack(fill=tk.BOTH, expand=True)
    
    # Rechte Spalte - Duplikat
    right_frame = tk.Frame(
        docs_frame, 
        bg=app.colors["card_background"], 
        padx=10, 
        pady=10
    )
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    right_header = tk.Label(
        right_frame, 
        text=f"Duplikat: {os.path.basename(duplicate_file)}", 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    right_header.pack(anchor=tk.W, pady=(0, 10))
    
    right_text = scrolledtext.ScrolledText(
        right_frame, 
        bg=app.colors["background_dark"],
        fg=app.colors["text_primary"],
        font=app.fonts["code"]
    )
    right_text.pack(fill=tk.BOTH, expand=True)
    
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
        target=_load_document_contents, 
        args=(app, original_file, duplicate_file, left_text, right_text)
    ).start()

def _load_document_contents(app, original_file, duplicate_file, left_text, right_text):
    """
    Lädt den Inhalt der Dokumente für den Vergleich
    
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

def load_document_content(app, file_path, text_widget):
    """
    Lädt den Inhalt eines Dokuments in ein Text-Widget
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei
        text_widget: Textfeld-Widget
    """
    try:
        # PDF-Inhalt extrahieren
        import fitz  # PyMuPDF
        
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        # Vollständigen Pfad bestimmen
        if not os.path.isabs(file_path):
            # Prüfen in verschiedenen Ordnern
            for folder in [
                app.config["paths"]["input_dir"], 
                app.config["paths"]["output_dir"], 
                app.config["paths"]["trash_dir"]
            ]:
                potential_path = os.path.join(folder, file_path)
                if os.path.exists(potential_path):
                    file_path = potential_path
                    break
        
        if os.path.exists(file_path):
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            text_widget.insert(tk.END, text)
            
            # PDF-Metadaten anzeigen
            text_widget.insert(tk.END, "\n\n--- Metadaten ---\n")
            for key, value in doc.metadata.items():
                if value:
                    text_widget.insert(tk.END, f"{key}: {value}\n")
                    
            doc.close()
        else:
            text_widget.insert(tk.END, f"Datei nicht gefunden: {file_path}")
        
        text_widget.config(state=tk.DISABLED)
        
    except Exception as e:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"Fehler beim Laden der Datei: {str(e)}")
        text_widget.config(state=tk.DISABLED)

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

def show_duplicate_alert(app, original_file, duplicate_file, similarity_score):
    """
    Zeigt einen Popup-Dialog an, wenn ein Duplikat gefunden wurde
    
    Args:
        app: Instanz der GuiApp
        original_file: Pfad zur Originaldatei
        duplicate_file: Pfad zur Duplikatdatei
        similarity_score: Ähnlichkeitswert (0-1)
    """
    similarity_percent = similarity_score * 100  # In Prozent umrechnen
    
    # Fenster erstellen
    alert_window = tk.Toplevel(app.root)
    alert_window.title("Duplikat erkannt")
    alert_window.geometry("600x400")
    alert_window.configure(bg=app.colors["background_dark"])
    alert_window.grab_set()  # Modal machen
    
    # Fensterinhalt
    alert_frame = tk.Frame(
        alert_window, 
        bg=app.colors["background_medium"], 
        padx=20, 
        pady=20
    )
    alert_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Icon
    warning_label = tk.Label(
        alert_frame, 
        text="⚠️", 
        font=("Segoe UI", 48),
        fg=app.colors["warning"],
        bg=app.colors["background_medium"]
    )
    warning_label.pack(pady=10)
    
    # Überschrift
    header = tk.Label(
        alert_frame, 
        text="Duplikat erkannt", 
        font=app.fonts["header"],
        fg=app.colors["warning"],
        bg=app.colors["background_medium"]
    )
    header.pack(pady=10)
    
    # Nachricht
    message_frame = tk.Frame(
        alert_frame, 
        bg=app.colors["card_background"], 
        padx=15, 
        pady=15
    )
    message_frame.pack(fill=tk.X, pady=10)
    
    # Originaldatei
    original_label = tk.Label(
        message_frame, 
        text="Originaldatei:", 
        font=app.fonts["normal"],
        fg=app.colors["text_secondary"],
        bg=app.colors["card_background"]
    )
    original_label.pack(anchor=tk.W)
    
    original_value = tk.Label(
        message_frame, 
        text=os.path.basename(original_file), 
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    original_value.pack(anchor=tk.W, padx=20, pady=(0, 10))
    
    # Duplikatdatei
    duplicate_label = tk.Label(
        message_frame, 
        text="Duplikatdatei:", 
        font=app.fonts["normal"],
        fg=app.colors["text_secondary"],
        bg=app.colors["card_background"]
    )
    duplicate_label.pack(anchor=tk.W)
    
    duplicate_value = tk.Label(
        message_frame, 
        text=os.path.basename(duplicate_file), 
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    duplicate_value.pack(anchor=tk.W, padx=20, pady=(0, 10))
    
    # Ähnlichkeit
    similarity_label = tk.Label(
        message_frame, 
        text="Ähnlichkeit:", 
        font=app.fonts["normal"],
        fg=app.colors["text_secondary"],
        bg=app.colors["card_background"]
    )
    similarity_label.pack(anchor=tk.W)
    
    similarity_value = tk.Label(
        message_frame, 
        text=f"{similarity_percent:.2f}%", 
        font=app.fonts["normal"],
        fg=app.colors["warning"],
        bg=app.colors["card_background"]
    )
    similarity_value.pack(anchor=tk.W, padx=20)
    
    # Buttons
    buttons_frame = tk.Frame(alert_frame, bg=app.colors["background_medium"], pady=10)
    buttons_frame.pack(fill=tk.X)
    
    # Button zum Vergleichen der Dokumente
    compare_btn = create_button(
        app,
        buttons_frame, 
        "Dokumente vergleichen", 
        lambda: compare_documents(app, original_file, duplicate_file)
    )
    compare_btn.pack(side=tk.LEFT, padx=5)
    
    # Button zum Öffnen des Originals
    open_original_btn = create_button(
        app,
        buttons_frame, 
        "Original öffnen", 
        lambda: open_document(app, original_file)
    )
    open_original_btn.pack(side=tk.LEFT, padx=5)
    
    # Button zum Öffnen des Duplikats
    open_duplicate_btn = create_button(
        app,
        buttons_frame, 
        "Duplikat öffnen", 
        lambda: open_document(app, duplicate_file)
    )
    open_duplicate_btn.pack(side=tk.LEFT, padx=5)
    
    # Button zum Schließen
    close_btn = create_button(
        app,
        buttons_frame, 
        "Schließen", 
        alert_window.destroy
    )
    close_btn.pack(side=tk.RIGHT, padx=5)
    
    # Soundeffekt abspielen, wenn aktiviert
    if app.config.get("gui", {}).get("enable_sounds", False):
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except ImportError:
            # Nicht auf Windows oder winsound nicht verfügbar
            pass