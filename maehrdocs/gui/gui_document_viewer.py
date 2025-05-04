"""
Dokumentenansicht für MaehrDocs
Enthält grundlegende Funktionen zum Anzeigen von Dokumenten
"""

import os
import sys
import subprocess
from tkinter import messagebox

def open_document(app, file_path):
    """
    Öffnet ein Dokument mit dem Standardprogramm
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei
    """
    try:
        # Vollständigen Pfad bestimmen
        complete_path = get_full_document_path(app, file_path)
        
        if os.path.exists(complete_path):
            # Plattformabhängiges Öffnen der Datei
            if os.name == 'nt':  # Windows
                os.startfile(complete_path)
            elif os.name == 'posix':  # macOS oder Linux
                subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', complete_path])
        else:
            messagebox.showerror("Fehler", f"Datei nicht gefunden: {complete_path}")
            
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Öffnen der Datei: {str(e)}")
        app.log(f"Fehler beim Öffnen der Datei: {str(e)}", level="error")

def get_full_document_path(app, file_path):
    """
    Bestimmt den vollständigen Pfad zu einem Dokument
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei (kann relativ sein)
        
    Returns:
        str: Vollständiger Pfad zur Datei
    """
    # Wenn schon ein absoluter Pfad, dann direkt zurückgeben
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path
        
    # Prüfen in verschiedenen Ordnern
    for folder in [
        app.config["paths"]["input_dir"], 
        app.config["paths"]["output_dir"], 
        app.config["paths"]["trash_dir"]
    ]:
        potential_path = os.path.join(folder, os.path.basename(file_path))
        if os.path.exists(potential_path):
            return potential_path
    
    # Wenn nicht gefunden, dann den ursprünglichen Pfad zurückgeben
    return file_path

def show_document_info(app, file_path):
    """
    Zeigt Informationen über ein Dokument an
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei
    """
    from .gui_document_loader import get_document_metadata
    
    try:
        full_path = get_full_document_path(app, file_path)
        if not os.path.exists(full_path):
            app.log(f"Datei nicht gefunden: {full_path}", level="error")
            return
            
        # Dokumentinformationen abrufen
        metadata = get_document_metadata(full_path)
        
        # Einfaches Popup mit Dokumentinformationen
        info_text = f"Dateiname: {os.path.basename(full_path)}\n"
        info_text += f"Größe: {os.path.getsize(full_path) / 1024:.1f} KB\n"
        info_text += f"Zuletzt geändert: {os.path.getmtime(full_path)}\n\n"
        
        # Metadaten hinzufügen
        info_text += "Metadaten:\n"
        for key, value in metadata.items():
            if value:
                info_text += f"{key}: {value}\n"
                
        # Popup anzeigen
        messagebox.showinfo("Dokumentinformationen", info_text)
        
    except Exception as e:
        app.log(f"Fehler beim Anzeigen der Dokumentinformationen: {str(e)}", level="error")