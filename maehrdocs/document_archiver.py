"""
Dokumentenarchivierung für MaehrDocs
Enthält Funktionen zum Archivieren von Business- und Barbelegen
in einer strukturierten Ordnerhierarchie basierend auf Jahr und Monat.
"""

import os
import logging
import shutil
from datetime import datetime

def archive_business_document(config, file_path, doc_info, logger=None):
    """
    Archiviert ein Business- oder Bar-Dokument im entsprechenden Monatsordner.
    
    Kopiert das Dokument in eine strukturierte Ordnerhierarchie:
    [business_docs_dir]/[Jahr]_[Kategorie]/[Monat]/[Dateiname]
    
    Args:
        config (dict): Die Anwendungskonfiguration
        file_path (str): Pfad zur PDF-Datei
        doc_info (dict): Extrahierte Dokumenteninformationen
        logger: Optional, Logger-Instanz für die Protokollierung
        
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # Nur fortfahren, wenn die Art des Dokuments Business oder Bar ist
        art = doc_info.get('art', '').lower()
        if art not in ['business', 'bar']:
            return False
        
        # Basispfad für Business-Dokumente
        business_dir = config.get('paths', {}).get('business_docs_dir', '')
        if not business_dir:
            logger.warning("Business-Dokumentenverzeichnis nicht konfiguriert. Archivierung übersprungen.")
            return False
        
        # Datum des Dokuments extrahieren
        date_str = doc_info.get('datum', '')
        if not date_str:
            logger.warning("Datum des Dokuments fehlt. Archivierung übersprungen.")
            return False
        
        try:
            # Datum parsen
            date = datetime.strptime(date_str, "%Y-%m-%d")
            year = date.strftime("%Y")
            month = date.strftime("%m")
            
            # Monatsname für Ordner
            month_names = {
                "01": "01_Januar", "02": "02_Februar", "03": "03_März", 
                "04": "04_April", "05": "05_Mai", "06": "06_Juni",
                "07": "07_Juli", "08": "08_August", "09": "09_September", 
                "10": "10_Oktober", "11": "11_November", "12": "12_Dezember"
            }
            month_folder = month_names.get(month, f"{month}_Monat")
            
            # Zielordner je nach Art (Business oder Bar)
            category_folder = "Business" if art == "business" else "Barbelege"
            target_dir = os.path.join(business_dir, f"{year}_{category_folder}", month_folder)
            
            # Zielordner erstellen, falls nicht vorhanden
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Zieldateiname (gleich wie im Ausgabeordner)
            target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            # Datei kopieren (nicht verschieben, da sie bereits im Ausgabeordner ist)
            shutil.copy2(file_path, target_path)
            
            logger.info(f"Dokument erfolgreich archiviert in: {target_path}")
            return True
            
        except ValueError:
            logger.warning(f"Ungültiges Datumsformat: {date_str}. Archivierung übersprungen.")
            return False
            
    except Exception as e:
        logger.error(f"Fehler beim Archivieren des Business-Dokuments: {str(e)}")
        return False