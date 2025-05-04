# gui_settings_dialog.py
"""
Einstellungsdialog für MaehrDocs
Erstellt ein Fenster zur Konfiguration der Anwendung
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yaml
from .gui_buttons import create_button
from .gui_settings_components import create_settings_section, collect_settings_from_widget, search_and_update_field

def open_settings(app):
    """
    Öffnet das Einstellungsfenster
    
    Args:
        app: Instanz der GuiApp
    """
    settings_window = tk.Toplevel(app.root)
    settings_window.title("MaehrDocs - Einstellungen")
    settings_window.geometry("800x600")
    settings_window.configure(bg=app.colors["background_dark"])
    
    # Einstellungen aus der Konfigurationsdatei laden
    settings_frame = tk.Frame(settings_window, bg=app.colors["background_medium"], padx=20, pady=20)
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Überschrift
    header = tk.Label(
        settings_frame, 
        text="Einstellungen", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    header.pack(anchor=tk.W, pady=(0, 20))
    
    # Notebook für Einstellungskategorien
    notebook = ttk.Notebook(settings_frame)
    
    # Einstellungs-Tabs erstellen
    create_general_tab(app, notebook)
    create_openai_tab(app, notebook)
    create_document_tab(app, notebook)
    create_notifications_tab(app, notebook)
    
    notebook.pack(fill=tk.BOTH, expand=True)
    
    # Buttons
    buttons_frame = tk.Frame(settings_frame, bg=app.colors["background_medium"], pady=15)
    buttons_frame.pack(fill=tk.X)
    
    save_btn = create_button(
        app,
        buttons_frame, 
        "Speichern", 
        lambda: save_settings(app, settings_window)
    )
    save_btn.pack(side=tk.RIGHT, padx=5)
    
    cancel_btn = create_button(
        app,
        buttons_frame, 
        "Abbrechen", 
        settings_window.destroy
    )
    cancel_btn.pack(side=tk.RIGHT, padx=5)

def create_general_tab(app, notebook):
    """
    Erstellt den Tab für allgemeine Einstellungen
    
    Args:
        app: Instanz der GuiApp
        notebook: ttk.Notebook-Widget
    """
    general_frame = tk.Frame(notebook, bg=app.colors["background_medium"])
    notebook.add(general_frame, text="Allgemein")
    
    # Pfade
    paths_section = create_settings_section(app, general_frame, "Verzeichnisse", [
        {"label": "Eingangsordner", "key": "paths.input_dir", "type": "folder"},
        {"label": "Ausgabeordner", "key": "paths.output_dir", "type": "folder"},
        {"label": "Fehlerordner", "key": "paths.trash_dir", "type": "folder"}
    ])

def create_openai_tab(app, notebook):
    """
    Erstellt den Tab für OpenAI-Einstellungen
    
    Args:
        app: Instanz der GuiApp
        notebook: ttk.Notebook-Widget
    """
    openai_frame = tk.Frame(notebook, bg=app.colors["background_medium"])
    notebook.add(openai_frame, text="OpenAI")
    
    openai_section = create_settings_section(app, openai_frame, "API-Einstellungen", [
        {"label": "Modell", "key": "openai.model", "type": "dropdown", 
         "options": ["gpt-3.5-turbo", "gpt-4o", "gpt-4-1106-preview"]},
        {"label": "Temperatur", "key": "openai.temperature", "type": "scale", 
         "from": 0, "to": 1, "resolution": 0.1},
        {"label": "Max. Wiederholungsversuche", "key": "openai.max_retries", 
         "type": "spinbox", "from": 1, "to": 10}
    ])

def create_document_tab(app, notebook):
    """
    Erstellt den Tab für Dokumentverarbeitungseinstellungen
    
    Args:
        app: Instanz der GuiApp
        notebook: ttk.Notebook-Widget
    """
    docs_frame = tk.Frame(notebook, bg=app.colors["background_medium"])
    notebook.add(docs_frame, text="Dokumentverarbeitung")
    
    docs_section = create_settings_section(app, docs_frame, "Verarbeitungsoptionen", [
        {"label": "Max. Dateigröße (MB)", "key": "document_processing.max_file_size_mb", 
         "type": "spinbox", "from": 1, "to": 50},
        {"label": "Ähnlichkeitsschwelle für Duplikate", "key": "document_processing.similarity_threshold", 
         "type": "scale", "from": 0.5, "to": 1.0, "resolution": 0.05}
    ])
    
    # Dokumenttypen
    doctypes_frame = tk.Frame(docs_frame, bg=app.colors["card_background"], padx=15, pady=15)
    doctypes_frame.pack(fill=tk.X, pady=10)
    
    doctypes_header = tk.Label(
        doctypes_frame, 
        text="Gültige Dokumenttypen", 
        font=app.fonts["subheader"],
        fg=app.colors["text_primary"],
        bg=app.colors["card_background"]
    )
    doctypes_header.pack(anchor=tk.W, pady=(0, 10))
    
    # Textfeld für Dokumenttypen
    doctypes_text = tk.Text(
        doctypes_frame, 
        height=5, 
        bg=app.colors["background_medium"],
        fg=app.colors["text_primary"],
        font=app.fonts["normal"]
    )
    doctypes_text.pack(fill=tk.X)
    
    # Aktuelle Dokumenttypen laden
    try:
        doctypes = app.config.get("document_processing", {}).get("valid_doc_types", [])
        doctypes_text.insert(tk.END, "\n".join(doctypes))
    except:
        app.log("Fehler beim Laden der Dokumenttypen", level="error")
    
    # Speichern der Referenz auf Dokumenttypen
    app.doctypes_text = doctypes_text

def create_notifications_tab(app, notebook):
    """
    Erstellt den Tab für Benachrichtigungseinstellungen
    
    Args:
        app: Instanz der GuiApp
        notebook: ttk.Notebook-Widget
    """
    notifications_frame = tk.Frame(notebook, bg=app.colors["background_medium"])
    notebook.add(notifications_frame, text="Benachrichtigungen")
    
    notifications_section = create_settings_section(app, notifications_frame, "Benachrichtigungsoptionen", [
        {"label": "Popup bei Duplikaten anzeigen", "key": "gui.show_duplicate_popup", "type": "checkbox"},
        {"label": "Benachrichtigung bei Verarbeitungsabschluss", "key": "gui.notify_on_completion", "type": "checkbox"},
        {"label": "Soundeffekte aktivieren", "key": "gui.enable_sounds", "type": "checkbox"}
    ])

def save_settings(app, settings_window):
    """
    Speichert die Einstellungen aus dem Einstellungsfenster
    
    Args:
        app: Instanz der GuiApp
        settings_window: Das Einstellungsfenster
    """
    try:
        # Alle Eingabefelder im Fenster finden
        collect_settings_from_widget(app, settings_window)
        
        # Dokumenttypen speichern
        if hasattr(app, 'doctypes_text'):
            doctypes = app.doctypes_text.get(1.0, tk.END).strip().split('\n')
            if 'document_processing' not in app.config:
                app.config['document_processing'] = {}
            app.config['document_processing']['valid_doc_types'] = doctypes
        
        # Konfiguration speichern
        app.config_manager.save_config(app.config)
        
        # Dashboard aktualisieren
        app.update_dashboard()
        
        # Fenster schließen
        settings_window.destroy()
        
        # Bestätigung anzeigen
        messagebox.showinfo("Einstellungen", "Die Einstellungen wurden erfolgreich gespeichert.")
        
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Speichern der Einstellungen: {str(e)}")
        app.log(f"Fehler beim Speichern der Einstellungen: {str(e)}", level="error")

def browse_folder(app, field_key):
    """
    Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld
    
    Args:
        app: Instanz der GuiApp
        field_key: Schlüssel des betroffenen Feldes
    """
    folder = filedialog.askdirectory(title="Ordner auswählen")
    if folder:
        # Für alle Top-Level-Fenster durchsuchen
        for widget in app.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                # Für alle Widgets im Fenster
                for child in widget.winfo_children():
                    # Rekursiv nach dem Feld suchen
                    if hasattr(child, 'winfo_children'):
                        search_and_update_field(child, field_key, folder)