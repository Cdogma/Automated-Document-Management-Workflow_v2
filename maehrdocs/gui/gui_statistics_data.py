"""
Datensammlung für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen zum Sammeln und Aufbereiten von Dokumentendaten
für die statistische Auswertung.
"""

import os
import logging
from datetime import datetime, timedelta

def collect_data(app, period="Alle"):
    """
    Sammelt Dokumentendaten für die statistische Analyse.
    
    Durchsucht die Dokumentenordner, filtert nach dem ausgewählten Zeitraum
    und sammelt relevante Metadaten zur Visualisierung.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        period: Zeitraum für die Filterung ("Alle", "Heute", usw.)
        
    Returns:
        dict: Gesammelte Dokumentendaten für die Analyse
    """
    logger = logging.getLogger(__name__)
    
    # Dokumentendaten sammeln
    data = {
        "types": {},        # Dokumenttypen und deren Anzahl
        "senders": {},      # Absender und deren Anzahl
        "sizes": {},        # Größenbereiche und deren Anzahl
        "timeline": {},     # Datum und Anzahl der Dokumente
        "documents": []     # Liste aller gefundenen Dokumente
    }
    
    # Ordnerpfade aus der Konfiguration
    output_dir = app.config.get("paths", {}).get("output_dir", "")
    
    if not os.path.exists(output_dir):
        return data
        
    # Zeitraumfilter berechnen
    cutoff_date = calculate_cutoff_date(period)
    
    # Dateien im Ausgabeordner durchsuchen
    for filename in os.listdir(output_dir):
        if not filename.lower().endswith('.pdf'):
            continue
            
        file_path = os.path.join(output_dir, filename)
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size / (1024 * 1024)  # Größe in MB
        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
        
        # Zeitraumfilter anwenden
        if cutoff_date and file_mtime < cutoff_date:
            continue
            
        # Dokumentinformationen extrahieren
        doc_info = extract_document_info(filename)
        
        # Dokumenttyp zählen
        if doc_info["type"] in data["types"]:
            data["types"][doc_info["type"]] += 1
        else:
            data["types"][doc_info["type"]] = 1
        
        # Absender zählen
        if doc_info["sender"] in data["senders"]:
            data["senders"][doc_info["sender"]] += 1
        else:
            data["senders"][doc_info["sender"]] = 1
        
        # Größenkategorie bestimmen und zählen
        size_category = categorize_size(file_size)
        if size_category in data["sizes"]:
            data["sizes"][size_category] += 1
        else:
            data["sizes"][size_category] = 1
        
        # Datum für Zeitverlauf extrahieren und zählen
        date_key = file_mtime.strftime("%Y-%m-%d")
        if date_key in data["timeline"]:
            data["timeline"][date_key] += 1
        else:
            data["timeline"][date_key] = 1
        
        # Dokument zur Liste hinzufügen
        data["documents"].append({
            "filename": filename,
            "path": file_path,
            "size": file_size,
            "mtime": file_mtime,
            "type": doc_info["type"],
            "sender": doc_info["sender"]
        })
    
    return data

def calculate_cutoff_date(period):
    """
    Berechnet das Cutoff-Datum basierend auf dem ausgewählten Zeitraum.
    
    Args:
        period: Zeitraum für die Filterung ("Alle", "Heute", usw.)
        
    Returns:
        datetime: Cutoff-Datum oder None für "Alle"
    """
    if period == "Alle":
        return None
    elif period == "Heute":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "Diese Woche":
        cutoff_date = datetime.now() - timedelta(days=datetime.now().weekday())
        return cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "Dieser Monat":
        return datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "Dieses Jahr":
        return datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None

def extract_document_info(filename):
    """
    Extrahiert Informationen aus dem Dateinamen eines verarbeiteten Dokuments.
    
    Args:
        filename: Name der Dokumentdatei
        
    Returns:
        dict: Extrahierte Dokumentinformationen
    """
    # Standard-Informationen
    doc_info = {
        "type": "Unbekannt",
        "sender": "Unbekannt",
        "date": None,
        "subject": "Unbekannt"
    }
    
    # Format ist typischerweise YYYY-MM-DD_Typ_Absender_Betreff.pdf
    parts = filename.split("_")
    
    # Datum (wenn vorhanden)
    if len(parts) > 0:
        date_part = parts[0]
        if len(date_part) == 10 and date_part.count("-") == 2:
            doc_info["date"] = date_part
    
    # Typ (wenn vorhanden)
    if len(parts) > 1:
        doc_type = parts[1]
        if doc_type.lower().endswith('.pdf'):
            doc_type = doc_type[:-4]
        doc_info["type"] = doc_type
    
    # Absender (wenn vorhanden)
    if len(parts) > 2:
        doc_info["sender"] = parts[2]
    
    # Betreff (wenn vorhanden)
    if len(parts) > 3:
        subject_parts = parts[3:]
        subject = "_".join(subject_parts)
        if subject.lower().endswith('.pdf'):
            subject = subject[:-4]
        doc_info["subject"] = subject
    
    return doc_info

def categorize_size(file_size):
    """
    Kategorisiert eine Dateigröße in eine Größenkategorie.
    
    Args:
        file_size: Dateigröße in MB
        
    Returns:
        str: Größenkategorie
    """
    if file_size < 0.5:
        return "<0.5 MB"
    elif file_size < 1:
        return "0.5-1 MB"
    elif file_size < 5:
        return "1-5 MB"
    else:
        return ">5 MB"