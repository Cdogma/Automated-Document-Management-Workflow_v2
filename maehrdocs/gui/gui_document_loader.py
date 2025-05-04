"""
Dokumentenloader für MaehrDocs
Enthält Funktionen zum Laden und Extrahieren von Dokumentinhalten
"""

import os
import tkinter as tk

from .gui_document_viewer import get_full_document_path

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
        full_path = get_full_document_path(app, file_path)
        
        if os.path.exists(full_path):
            doc = fitz.open(full_path)
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
            text_widget.insert(tk.END, f"Datei nicht gefunden: {full_path}")
        
        text_widget.config(state=tk.DISABLED)
        
    except Exception as e:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"Fehler beim Laden der Datei: {str(e)}")
        text_widget.config(state=tk.DISABLED)

def get_document_metadata(file_path):
    """
    Extrahiert Metadaten aus einem PDF-Dokument
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        dict: Metadaten des Dokuments oder leeres Dictionary bei Fehler
    """
    try:
        import fitz  # PyMuPDF
        
        if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
            return {}
        
        with fitz.open(file_path) as doc:
            # Metadaten extrahieren
            metadata = doc.metadata
            
            # Dokumentinformationen extrahieren
            info = {
                "Seitenanzahl": len(doc),
                "Erstellungsdatum": metadata.get("creationDate", ""),
                "Änderungsdatum": metadata.get("modDate", ""),
                "Format": doc.name.split(".")[-1].upper() if "." in doc.name else "",
                "Verschlüsselt": "Ja" if doc.isEncrypted else "Nein"
            }
            
            # Metadaten und Dokumentinformationen zusammenführen
            combined = {**metadata, **info}
            
            return combined
    
    except Exception:
        return {}

def extract_document_text(file_path):
    """
    Extrahiert Text aus einem PDF-Dokument
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        str: Extrahierter Text oder leerer String bei Fehler
    """
    try:
        import fitz  # PyMuPDF
        
        if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
            return ""
        
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        
        return text
    
    except Exception:
        return ""

def get_document_preview(app, file_path, text_widget, max_chars=2000):
    """
    Lädt eine Vorschau des Dokumentinhalts in ein Text-Widget
    
    Args:
        app: Instanz der GuiApp
        file_path: Pfad zur Datei
        text_widget: Textfeld-Widget
        max_chars: Maximale Anzahl der anzuzeigenden Zeichen
    """
    try:
        # Vollständigen Pfad bestimmen
        full_path = get_full_document_path(app, file_path)
        
        if not os.path.exists(full_path):
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"Datei nicht gefunden: {full_path}")
            text_widget.config(state=tk.DISABLED)
            return
        
        # Text extrahieren
        text = extract_document_text(full_path)
        
        # Text auf max_chars begrenzen
        if len(text) > max_chars:
            preview_text = text[:max_chars] + "...\n\n[Gekürzt - vollständigen Text anzeigen]"
        else:
            preview_text = text
        
        # In Widget anzeigen
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, preview_text)
        text_widget.config(state=tk.DISABLED)
        
    except Exception as e:
        app.log(f"Fehler beim Laden der Dokumentvorschau: {str(e)}", level="error")