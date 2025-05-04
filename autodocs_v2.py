import os
import sys
import fitz  # PyMuPDF
import logging
import logging.handlers
import shutil
import json
import re
import hashlib
import yaml
import argparse
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from duplicate_detector import DuplicateDetector

# Lade API-Schlüssel aus der .env-Datei
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Basisverzeichnis definieren
BASE_DIR = r"C:\Users\renem\OneDrive\09_AutoDocs"
CONFIG_PATH = os.path.join(BASE_DIR, "autodocs_config.yaml")

def load_or_create_config(config_path=CONFIG_PATH):
    default_config = {
        "paths": {
            "input_dir": os.path.join(BASE_DIR, "01_InboxDocs"),
            "output_dir": os.path.join(BASE_DIR, "02_FinalDocs"),
            "trash_dir": os.path.join(BASE_DIR, "03_TrashDocs")
        },
        "openai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_retries": 3
        },
        "document_processing": {
            "max_file_size_mb": 20,
            "similarity_threshold": 0.85,
            "valid_doc_types": ["rechnung", "vertrag", "brief", "meldung", "bescheid", "dokument", "antrag"]
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "dokument_prozess.log",
            "max_log_size_mb": 5,
            "backup_count": 3
        }
    }
    
    # Wenn Konfigurationsdatei nicht existiert, erstelle sie
    if not os.path.exists(config_path):
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            print(f"Neue Konfigurationsdatei erstellt: {config_path}")
        except Exception as e:
            print(f"Fehler beim Erstellen der Konfigurationsdatei: {e}")
        return default_config
    
    # Bestehende Konfiguration laden
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Fehlende Konfigurationseinträge mit Standardwerten ergänzen
        def update_nested_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = update_nested_dict(d[k], v)
                elif k not in d:
                    d[k] = v
            return d
            
        config = update_nested_dict(config, default_config)
        return config
        
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}, Standard-Konfiguration wird verwendet")
        return default_config

def setup_logging(config):
    log_config = config["logging"]
    log_level = getattr(logging, log_config["log_level"], logging.INFO)
    log_file = os.path.join(BASE_DIR, log_config["log_file"])
    
    # Rotierendes Log-File
    max_bytes = log_config["max_log_size_mb"] * 1024 * 1024
    backup_count = log_config["backup_count"]
    
    handlers = [
        logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        ),
        logging.StreamHandler(sys.stdout)
    ]
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logging.info(f"Logging konfiguriert: Level={log_config['log_level']}, File={log_file}")

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "".join([page.get_text() for page in doc])
        if not text or len(text.strip()) < 10:
            logging.warning(f"PDF enthält zu wenig Text: {pdf_path}")
            return None
        doc.close()  # Wichtig: Ressourcen freigeben
        return text
    except fitz.FileDataError:
        logging.error(f"Datei ist keine gültige PDF: {pdf_path}")
        return None
    except fitz.EmptyFileError:
        logging.error(f"PDF-Datei ist leer: {pdf_path}")
        return None
    except PermissionError:
        logging.error(f"Keine Leseberechtigung für: {pdf_path}")
        return None
    except Exception as e:
        logging.error(f"Fehler beim Lesen der PDF {pdf_path}: {e}")
        return None

def analyze_document_with_openai(text, config):
    if not text or len(text.strip()) < 10:
        logging.warning("Zu wenig Text im Dokument für die Analyse")
        return {"error": "Zu wenig Text im Dokument"}

    prompt = f"""
Analysiere dieses Dokument und extrahiere die folgenden Informationen im JSON-Format:

1. dokumenttyp (z.B. rechnung, vertrag, brief)
2. datum (Rechnungs- oder Ausstellungsdatum im Format YYYY-MM-DD)
3. absender (Unternehmen oder Absender, klar gekürzt und vereinfacht)
4. betreff oder thema (optional)
5. schluesselwoerter (max. 5, optional)
Falls es sich um eine Rechnung handelt, zusätzlich:
6. rechnungsnummer
7. betrag (gesamt)

**Format:**
{{
  "dokumenttyp": "",
  "datum": "",
  "absender": "",
  "betreff": "",
  "schluesselwoerter": [],
  "rechnungsnummer": "",
  "betrag": ""
}}

**WICHTIG:**
- Verwende für "dokumenttyp" kurze Begriffe wie "rechnung", "vertrag", "brief", "meldung", "bescheid"
- Verwende für "absender" eine gekürzte Version (klein, _ statt Leerzeichen, ohne GmbH, AG etc.)
Analysiere nur den folgenden Dokumenttext (max. 4000 Zeichen):
{text[:4000]}
"""

    openai_config = config["openai"]
    max_retries = openai_config["max_retries"]
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model=openai_config["model"],
                messages=[
                    {"role": "system", "content": "Du bist ein Assistent für Dokumentenanalyse."},
                    {"role": "user", "content": prompt}
                ],
                temperature=openai_config["temperature"],
            )
            result = response.choices[0].message.content.strip()
            
            # JSON bereinigen
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
                
            # JSON parsen mit Fehlerbehandlung
            try:
                json_result = json.loads(result)
                return json_result
            except json.JSONDecodeError:
                logging.warning(f"Ungültiges JSON-Format bei Versuch {retry_count+1}: {result[:100]}...")
                retry_count += 1
                continue
                
        except Exception as e:
            logging.error(f"OpenAI API-Fehler bei Versuch {retry_count+1}: {e}")
            retry_count += 1
            if retry_count >= max_retries:
                return {"error": f"Analyse fehlgeschlagen nach {max_retries} Versuchen: {str(e)}"}
            # Kurze Pause vor erneutem Versuch
            import time
            time.sleep(1)
    
    return {"error": "Analyse fehlgeschlagen, ungültiges JSON-Format"}

def extract_scan_date(file_path):
    ts = os.path.getctime(file_path)
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

def is_well_named(filename):
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}_[a-z]+_[a-z0-9_]+\.pdf$', filename.lower()))

def is_duplicate(file_path, output_dir, config):
    """Erweiterte Duplikaterkennung mit Hashwert und zusätzlicher Inhaltsanalyse"""
    
    # Hash-basierte Erkennung (schnell)
    def file_hash(path):
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    current_hash = file_hash(file_path)
    
    # Erste Prüfung: Exakte Duplikate via Hash
    for f in os.listdir(output_dir):
        if not f.lower().endswith('.pdf'):
            continue
            
        compare_path = os.path.join(output_dir, f)
        if os.path.isfile(compare_path) and file_hash(compare_path) == current_hash:
            logging.info(f"Exaktes Duplikat gefunden (Hash-Übereinstimmung): {f}")
            return True
    
    # Wenn kein Hash-Duplikat, prüfe auf ähnliche Dokumente
    try:
        # Textvergleich für ähnliche Dokumente
        current_text = extract_text_from_pdf(file_path)
        
        if not current_text or len(current_text) < 100:
            logging.warning("Text zu kurz für zuverlässigen Ähnlichkeitsvergleich")
            return False
            
        # Prüfe jede PDF im Zielordner
        for f in os.listdir(output_dir):
            if not f.lower().endswith('.pdf'):
                continue
                
            compare_path = os.path.join(output_dir, f)
            compare_text = extract_text_from_pdf(compare_path)
            
            if not compare_text:
                continue
                
            # Ähnlichkeitsvergleich
            detector = DuplicateDetector()
            similarity = detector.calculate_similarity(current_text, compare_text)
            
            similarity_threshold = config["document_processing"]["similarity_threshold"]
            if similarity > similarity_threshold:
                logging.info(f"Ähnliches Dokument gefunden (Ähnlichkeit: {similarity:.2f}): {f}")
                return True
                
    except Exception as e:
        logging.error(f"Fehler beim Ähnlichkeitsvergleich: {e}")
        # Im Fehlerfall nicht als Duplikat erkennen
        return False
        
    return False

def generate_filename(doc_info, fallback_date, config):
    if "error" in doc_info:
        return f"unbekannt_{fallback_date}.pdf"  # Dateiendung direkt hinzufügen

    date_part = fallback_date
    if doc_info.get("datum"):
        try:
            # Striktere Datumsvalidierung
            date_str = doc_info["datum"]
            # Prüfen auf korrektes Format
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                raise ValueError("Falsches Datumsformat")
                
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Prüfen auf plausibles Datum (nicht in der Zukunft, nicht zu alt)
            if date_obj > datetime.now():
                logging.warning(f"Zukunftsdatum erkannt: {date_str}, nutze Scan-Datum")
                date_part = fallback_date
            elif date_obj.year < 2000:
                logging.warning(f"Sehr altes Datum erkannt: {date_str}, prüfe Plausibilität")
                # Optional: Bestätigung einholen oder Fallback nutzen
                date_part = fallback_date
            else:
                date_part = date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            logging.info(f"⚠️ Kein gültiges Datum im Dokument gefunden – Fallback auf Scan-Datum: {e}")
            date_part = fallback_date
    else:
        logging.info("📌 Kein Datum von GPT – nutze Scan-Datum als Fallback.")

    # Dokumenttyp validieren und standardisieren
    valid_doc_types = config["document_processing"]["valid_doc_types"]
    doc_type = doc_info.get("dokumenttyp", "dokument").lower()
    doc_type = doc_type if doc_type in valid_doc_types else "dokument"
    
    # Absender bereinigen
    sender = doc_info.get("absender", "unbekannt").replace(" ", "_").lower()
    sender = re.sub(r'[^a-z0-9_]', '', sender)[:30]  # Begrenzung auf 30 Zeichen
    
    if not sender or sender == "":
        sender = "unbekannt"

    filename = f"{date_part}_{doc_type}_{sender}.pdf"
    return filename

def process_documents(dry_run=False, force_overwrite=False, config=None):
    success_count = 0
    error_count = 0
    skipped_count = 0
    duplicate_count = 0
    
    input_dir = config["paths"]["input_dir"]
    output_dir = config["paths"]["output_dir"]
    trash_dir = config["paths"]["trash_dir"]
    
    # Alle PDF-Dateien sammeln (mit Ausnahme versteckter Dateien)
    pdf_files = [f for f in os.listdir(input_dir) 
                if f.lower().endswith('.pdf') and not f.startswith('.')]
    
    if not pdf_files:
        logging.info("Keine PDF-Dateien im Eingabeordner gefunden.")
        return

    total_count = len(pdf_files)
    logging.info(f"Gefunden: {total_count} PDF-Dateien zur Verarbeitung")
    
    # Erstelle eine Zusammenfassung für die Protokollierung am Ende
    results_summary = []

    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(input_dir, pdf_file)
        logging.info(f"[{i}/{total_count}] Verarbeite: {pdf_file}")
        result_info = {"original": pdf_file, "status": "error", "details": ""}

        try:
            # Dateigröße prüfen
            file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
            max_file_size = config["document_processing"]["max_file_size_mb"]
            if file_size > max_file_size:
                logging.warning(f"Datei zu groß ({file_size:.2f} MB): {pdf_file}")
                result_info["status"] = "skipped"
                result_info["details"] = f"Datei zu groß: {file_size:.2f} MB"
                skipped_count += 1
                results_summary.append(result_info)
                continue

            if is_well_named(pdf_file):
                logging.info(f"Schon gut benannt: {pdf_file} → Übersprungen")
                result_info["status"] = "skipped"
                result_info["details"] = "Bereits korrekt benannt"
                skipped_count += 1
                results_summary.append(result_info)
                continue

            # PDF-Text extrahieren
            pdf_text = extract_text_from_pdf(pdf_path)
            if not pdf_text:
                logging.warning(f"Kein Text extrahierbar: {pdf_file} → Wird in Trash verschoben")
                if not dry_run:
                    shutil.move(pdf_path, os.path.join(trash_dir, pdf_file))
                result_info["status"] = "error"
                result_info["details"] = "Textextraktion fehlgeschlagen"
                error_count += 1
                results_summary.append(result_info)
                continue
            
            # Dokument mit OpenAI analysieren
            doc_info = analyze_document_with_openai(pdf_text, config)
            
            if "error" in doc_info:
                logging.warning(f"Analyse fehlgeschlagen: {doc_info['error']}")
                result_info["details"] = f"Analyse fehlgeschlagen: {doc_info['error']}"
            
            doc_info["original_filename"] = pdf_file
            
            # Scan-Datum ermitteln und neuen Dateinamen generieren
            scan_date = extract_scan_date(pdf_path)
            new_filename = generate_filename(doc_info, fallback_date=scan_date, config=config)
            output_path = os.path.join(output_dir, new_filename)
            
            # Auf Duplikate prüfen
            if is_duplicate(pdf_path, output_dir, config):
                logging.info(f"Duplikat erkannt, wird nicht verschoben: {pdf_file}")
                result_info["status"] = "duplicate"
                result_info["details"] = f"Duplikat von bestehendem Dokument"
                if not dry_run:
                    os.remove(pdf_path)
                duplicate_count += 1
                results_summary.append(result_info)
                continue
            
            # Konflikte bei Dateinamen behandeln
            if os.path.exists(output_path) and not force_overwrite:
                name_ohne_pdf = new_filename[:-4]
                timestamp = datetime.now().strftime('%H%M%S')
                new_filename = f"{name_ohne_pdf}_{timestamp}.pdf"
                output_path = os.path.join(output_dir, new_filename)
                logging.info(f"Dateikonflikt gelöst durch Zeitstempel: {new_filename}")
            
            # Datei kopieren und Original löschen
            if not dry_run:
                shutil.copy2(pdf_path, output_path)
                os.remove(pdf_path)
                logging.info(f"✅ {pdf_file} → {new_filename}")
            else:
                logging.info(f"[SIMULATION] Würde umbenennen: {pdf_file} → {new_filename}")
            
            result_info["status"] = "success"
            result_info["details"] = f"Umbenannt zu: {new_filename}"
            result_info["new_filename"] = new_filename
            success_count += 1
            
        except Exception as e:
            logging.error(f"❌ Fehler bei {pdf_file}: {e}")
            result_info["details"] = f"Unerwarteter Fehler: {str(e)}"
            try:
                if not dry_run:
                    shutil.move(pdf_path, os.path.join(trash_dir, pdf_file))
                    logging.info(f"Datei in Trash verschoben: {pdf_file}")
            except Exception as move_error:
                logging.error(f"Fehler beim Verschieben in Trash: {move_error}")
            
            error_count += 1
        
        results_summary.append(result_info)

    # Speichere Verarbeitungsbericht
    try:
        report_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(BASE_DIR, f"verarbeitungsbericht_{report_time}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "statistik": {
                    "gesamt": total_count,
                    "erfolgreich": success_count,
                    "übersprungen": skipped_count,
                    "duplikate": duplicate_count,
                    "fehler": error_count
                },
                "details": results_summary
            }, f, indent=2, ensure_ascii=False)
        logging.info(f"Verarbeitungsbericht erstellt: {report_path}")
    except Exception as e:
        logging.error(f"Fehler beim Erstellen des Verarbeitungsberichts: {e}")

    # Statistik ausgeben
    logging.info(f"""
=== Zusammenfassung ===
Gesamt verarbeitet: {total_count}
✅ Erfolgreich: {success_count}
⏭️ Übersprungen: {skipped_count}
🔄 Duplikate: {duplicate_count}
❌ Fehler: {error_count}
====================
    """)

def parse_arguments():
    parser = argparse.ArgumentParser(description='AutoDocs - Automatische Dokumentenverarbeitung')
    
    parser.add_argument('--config', type=str, help='Pfad zur alternativen Konfigurationsdatei')
    parser.add_argument('--verbose', '-v', action='count', default=0, 
                        help='Erhöht Detaillierungsgrad der Ausgabe (mehrfach möglich: -v, -vv, -vvv)')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Simulationsmodus: Keine Dateien werden verschoben')
    parser.add_argument('--single-file', type=str, 
                        help='Verarbeitet nur die angegebene Datei')
    parser.add_argument('--rebuild-config', action='store_true',
                        help='Erstellt die Konfigurationsdatei neu mit Standardwerten')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Überschreibt vorhandene Dateien ohne Nachfrage')
    
    return parser.parse_args()

def process_single_file(file_path, config, dry_run=False, force_overwrite=False):
    if not os.path.exists(file_path):
        logging.error(f"Datei nicht gefunden: {file_path}")
        return False
        
    if not file_path.lower().endswith('.pdf'):
        logging.error(f"Keine PDF-Datei: {file_path}")
        return False
        
    output_dir = config["paths"]["output_dir"]
    trash_dir = config["paths"]["trash_dir"]
    
    try:
        pdf_file = os.path.basename(file_path)
        logging.info(f"Verarbeite Einzeldatei: {pdf_file}")
        
        # PDF-Text extrahieren
        pdf_text = extract_text_from_pdf(file_path)
        if not pdf_text:
            logging.warning(f"Kein Text extrahierbar: {pdf_file}")
            return False
        
        # Dokument mit OpenAI analysieren
        doc_info = analyze_document_with_openai(pdf_text, config)
        
        if "error" in doc_info:
            logging.warning(f"Analyse fehlgeschlagen: {doc_info['error']}")
            return False
        
        doc_info["original_filename"] = pdf_file
        
        # Scan-Datum ermitteln und neuen Dateinamen generieren
        scan_date = extract_scan_date(file_path)
        new_filename = generate_filename(doc_info, fallback_date=scan_date, config=config)
        output_path = os.path.join(output_dir, new_filename)
        
        # Auf Duplikate prüfen
        if is_duplicate(file_path, output_dir, config):
            logging.info(f"Duplikat erkannt, wird nicht verschoben: {pdf_file}")
            return False
        
        # Konflikte bei Dateinamen behandeln
        if os.path.exists(output_path) and not force_overwrite:
            name_ohne_pdf = new_filename[:-4]
            timestamp = datetime.now().strftime('%H%M%S')
            new_filename = f"{name_ohne_pdf}_{timestamp}.pdf"
            output_path = os.path.join(output_dir, new_filename)
            logging.info(f"Dateikonflikt gelöst durch Zeitstempel: {new_filename}")
        
        # Datei kopieren und Original löschen
        if not dry_run:
            shutil.copy2(file_path, output_path)
            os.remove(file_path)
            logging.info(f"✅ {pdf_file} → {new_filename}")
        else:
            logging.info(f"[SIMULATION] Würde umbenennen: {pdf_file} → {new_filename}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Fehler bei {file_path}: {e}")
        return False

if __name__ == "__main__":
    # Kommandozeilenargumente parsen
    args = parse_arguments()
    
    # Konfiguration laden oder neu erstellen
    if args.rebuild_config and os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
        print(f"Bestehende Konfigurationsdatei gelöscht: {CONFIG_PATH}")
        
    config_path = args.config if args.config else CONFIG_PATH
    config = load_or_create_config(config_path)
    
    # Verbose-Level anpassen
    if args.verbose > 0:
        log_levels = {
            0: logging.INFO,
            1: logging.INFO,  # -v: INFO mit mehr Details
            2: logging.DEBUG,  # -vv: DEBUG
            3: logging.DEBUG   # -vvv: DEBUG mit maximalen Details
        }
        config["logging"]["log_level"] = logging.getLevelName(log_levels.get(min(args.verbose, 3)))
        print(f"Loglevel geändert auf: {config['logging']['log_level']}")
    
    # Logging einrichten
    setup_logging(config)
    
    # Weitere Kommandozeilenparameter verarbeiten
    if args.dry_run:
        logging.info("SIMULATIONSMODUS: Keine Dateien werden verschoben")
    
    # Pfade aus Konfiguration übernehmen
    INPUT_DIR = config["paths"]["input_dir"]
    OUTPUT_DIR = config["paths"]["output_dir"]
    TRASH_DIR = config["paths"]["trash_dir"]
    
    # Ordner sicherstellen
    for folder in [INPUT_DIR, OUTPUT_DIR, TRASH_DIR]:
        os.makedirs(folder, exist_ok=True)
    
    logging.info("=== Start Dokumentenverarbeitung ===")
    
    if args.single_file:
        # Einzelne Datei verarbeiten
        success = process_single_file(args.single_file, config, 
                                     dry_run=args.dry_run, 
                                     force_overwrite=args.force)
        if success:
            logging.info("Einzeldateiverarbeitung erfolgreich abgeschlossen.")
        else:
            logging.warning("Einzeldateiverarbeitung nicht erfolgreich.")
    else:
        # Normaler Prozess für alle Dateien
        process_documents(dry_run=args.dry_run, force_overwrite=args.force, config=config)
        
    logging.info("=== Ende ===")