"""
Datensammlung für die Statistikvisualisierung in MaehrDocs
Enthält Funktionen zum Sammeln und Aufbereiten von Dokumentendaten
für die statistische Auswertung mit Caching-Mechanismus für bessere Performance.
"""

import os
import logging
import time
from datetime import datetime, timedelta
from functools import lru_cache

# Cache für die gesammelten Daten
# Format: {Zeitraum: (Zeitstempel, Daten)}
_data_cache = {}
# Maximale Cache-Lebensdauer in Sekunden (5 Minuten)
_CACHE_TTL = 300

def collect_data(app, period="Alle"):
    """
    Sammelt Dokumentendaten für die statistische Analyse mit Caching.
    
    Durchsucht die Dokumentenordner, filtert nach dem ausgewählten Zeitraum
    und sammelt relevante Metadaten zur Visualisierung. Verwendet einen Cache,
    um wiederholte Abfragen für denselben Zeitraum zu beschleunigen.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        period: Zeitraum für die Filterung ("Alle", "Heute", usw.)
        
    Returns:
        dict: Gesammelte Dokumentendaten für die Analyse
    """
    logger = logging.getLogger(__name__)
    
    # Cache-Prüfung
    current_time = time.time()
    if period in _data_cache:
        cache_time, cached_data = _data_cache[period]
        # Cache verwenden, wenn er noch nicht abgelaufen ist
        if current_time - cache_time < _CACHE_TTL:
            logger.debug(f"Verwende Cache-Daten für Zeitraum: {period}")
            return cached_data
    
    logger.debug(f"Sammle neue Daten für Zeitraum: {period}")
    
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
    
    try:
        # Optimierung: Vorfilterung der Dateiliste
        start_time = time.time()
        pdf_files = [f for f in os.listdir(output_dir) if f.lower().endswith('.pdf')]
        
        # Mit Generator arbeiten für bessere Speichereffizienz
        for filename in pdf_files:
            file_path = os.path.join(output_dir, filename)
            
            try:
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
                
                # Dokument zur Liste hinzufügen - nur bei Bedarf die vollständigen Daten
                if len(data["documents"]) < 1000:  # Begrenzung für Speichereffizienz
                    data["documents"].append({
                        "filename": filename,
                        "path": file_path,
                        "size": file_size,
                        "mtime": file_mtime,
                        "type": doc_info["type"],
                        "sender": doc_info["sender"]
                    })
            except Exception as e:
                logger.warning(f"Fehler bei Verarbeitung von {filename}: {str(e)}")
                continue
                
        # Verarbeitungszeit messen
        processing_time = time.time() - start_time
        logger.debug(f"Datensammlung für {len(pdf_files)} Dateien: {processing_time:.2f} Sekunden")
        
        # Daten im Cache speichern
        _data_cache[period] = (current_time, data)
        
        return data
        
    except Exception as e:
        logger.error(f"Fehler bei der Datensammlung: {str(e)}")
        return data

# Caching für die Cutoff-Daten-Berechnung
@lru_cache(maxsize=32)
def calculate_cutoff_date(period):
    """
    Berechnet das Cutoff-Datum basierend auf dem ausgewählten Zeitraum.
    Diese Funktion wird gecacht, da die Berechnung für jeden Zeitraum gleich bleibt.
    
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

def clear_cache():
    """
    Löscht den Datencache vollständig.
    Nützlich nach Dokumentenverarbeitung oder anderen Änderungen, die den Cache invalidieren.
    """
    global _data_cache
    _data_cache.clear()
    logging.getLogger(__name__).debug("Statistik-Datencache geleert")