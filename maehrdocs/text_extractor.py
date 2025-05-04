"""
Textextraktion aus PDF-Dokumenten für MaehrDocs
"""

import os
import logging
import fitz  # PyMuPDF

class TextExtractor:
    """
    Klasse zur Extraktion von Text aus PDF-Dokumenten
    """
    
    def __init__(self):
        """
        Initialisiert den TextExtractor
        """
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, file_path):
        """
        Extrahiert Text aus einer PDF-Datei
        
        Args:
            file_path (str): Pfad zur PDF-Datei
            
        Returns:
            str: Extrahierter Text oder None bei Fehler
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Datei existiert nicht: {file_path}")
                return None
                
            if not file_path.lower().endswith('.pdf'):
                self.logger.error(f"Datei ist keine PDF: {file_path}")
                return None
                
            text = ""
            with fitz.open(file_path) as doc:
                # Metadaten für Debugging
                self.logger.debug(f"PDF-Metadaten: {doc.metadata}")
                
                # Dokumentinformationen
                self.logger.debug(f"Seitenanzahl: {len(doc)}")
                
                # Text aus jeder Seite extrahieren
                for page_num, page in enumerate(doc):
                    page_text = page.get_text()
                    self.logger.debug(f"Seite {page_num+1}: {len(page_text)} Zeichen extrahiert")
                    text += page_text
                    
            if not text.strip():
                self.logger.warning(f"Extrahierter Text ist leer: {file_path}")
                
            return text
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren des Textes aus {file_path}: {str(e)}")
            return None
    
    def get_pdf_metadata(self, file_path):
        """
        Extrahiert Metadaten aus einer PDF-Datei
        
        Args:
            file_path (str): Pfad zur PDF-Datei
            
        Returns:
            dict: Metadaten oder leeres Dictionary bei Fehler
        """
        try:
            if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
                return {}
                
            with fitz.open(file_path) as doc:
                return doc.metadata
                
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren der Metadaten aus {file_path}: {str(e)}")
            return {}
    
    def is_valid_pdf(self, file_path, max_size_mb=20):
        """
        Prüft, ob eine Datei eine gültige PDF ist und die Größenbeschränkung einhält
        
        Args:
            file_path (str): Pfad zur zu prüfenden Datei
            max_size_mb (int): Maximale Dateigröße in MB
            
        Returns:
            bool: True, wenn die Datei eine gültige PDF ist und die Größenbeschränkung einhält
        """
        try:
            # Existenz prüfen
            if not os.path.exists(file_path):
                self.logger.error(f"Datei existiert nicht: {file_path}")
                return False
                
            # Endung prüfen
            if not file_path.lower().endswith('.pdf'):
                self.logger.error(f"Datei ist keine PDF: {file_path}")
                return False
                
            # Größe prüfen
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                self.logger.warning(f"Datei zu groß ({file_size_mb:.2f} MB): {file_path}")
                return False
                
            # Versuche, die Datei als PDF zu öffnen
            with fitz.open(file_path) as doc:
                # Prüfe, ob mindestens eine Seite vorhanden ist
                if len(doc) == 0:
                    self.logger.warning(f"PDF enthält keine Seiten: {file_path}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei der PDF-Validierung von {file_path}: {str(e)}")
            return False