"""
Berichtsgeneratoren für MaehrDocs
Enthält spezialisierte Funktionen zur Erstellung verschiedener Berichtsformate
für die Dokumentation von Duplikaten und anderen Systemereignissen.

Unterstützte Formate:
- Text: Einfache Textberichte für die Konsole oder einfache Logs
- HTML: Formatierte, interaktive Berichte für die Ansicht im Browser
- JSON: Maschinenlesbare Berichte für die Weiterverarbeitung
"""

import os
import logging
import datetime
import json

def generate_text_report(report_file, duplicate_file, original_file, config, logger=None):
    """
    Generiert einen einfachen Textbericht über ein erkanntes Duplikat.
    
    Args:
        report_file (str): Pfad zur zu erstellenden Berichtsdatei
        duplicate_file (str): Pfad zur Duplikatdatei
        original_file (str): Pfad zur Originaldatei
        config (dict): Die Anwendungskonfiguration
        logger: Logger-Instanz für die Protokollierung
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
        
    try:
        # Grundlegende Informationen sammeln
        dup_filename = os.path.basename(duplicate_file)
        orig_filename = os.path.basename(original_file)
        
        # Dateigrößen ermitteln
        dup_size = os.path.getsize(duplicate_file)
        orig_size = os.path.getsize(original_file)
        
        # Änderungsdaten ermitteln
        dup_modified = datetime.datetime.fromtimestamp(os.path.getmtime(duplicate_file))
        orig_modified = datetime.datetime.fromtimestamp(os.path.getmtime(original_file))
        
        # Bericht schreiben
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== MaehrDocs Duplikatbericht ===\n")
            f.write(f"Erstellt am: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("== Duplikat-Datei ==\n")
            f.write(f"Dateiname: {dup_filename}\n")
            f.write(f"Pfad: {duplicate_file}\n")
            f.write(f"Größe: {dup_size / 1024:.2f} KB\n")
            f.write(f"Zuletzt geändert: {dup_modified.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("== Original-Datei ==\n")
            f.write(f"Dateiname: {orig_filename}\n")
            f.write(f"Pfad: {original_file}\n")
            f.write(f"Größe: {orig_size / 1024:.2f} KB\n")
            f.write(f"Zuletzt geändert: {orig_modified.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("== Vergleich ==\n")
            f.write(f"Größenunterschied: {abs(dup_size - orig_size) / 1024:.2f} KB\n")
            f.write(f"Zeitunterschied: {abs((orig_modified - dup_modified).total_seconds() / 3600):.2f} Stunden\n\n")
            
            f.write("== Maßnahmen ==\n")
            f.write(f"Die Duplikatdatei wurde in den Papierkorb verschoben.\n")
            f.write(f"Für detaillierten Textvergleich bitte den Inhalt beider Dateien manuell vergleichen.\n")
        
        logger.info(f"Textbericht erstellt: {report_file}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des Textberichts: {str(e)}")

def generate_html_report(report_file, duplicate_file, original_file, config, logger=None):
    """
    Generiert einen HTML-Bericht über ein erkanntes Duplikat.
    
    Args:
        report_file (str): Pfad zur zu erstellenden Berichtsdatei
        duplicate_file (str): Pfad zur Duplikatdatei
        original_file (str): Pfad zur Originaldatei
        config (dict): Die Anwendungskonfiguration
        logger: Logger-Instanz für die Protokollierung
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
        
    try:
        # Grundlegende Informationen sammeln
        dup_filename = os.path.basename(duplicate_file)
        orig_filename = os.path.basename(original_file)
        
        # Dateigrößen ermitteln
        dup_size = os.path.getsize(duplicate_file)
        orig_size = os.path.getsize(original_file)
        
        # Änderungsdaten ermitteln
        dup_modified = datetime.datetime.fromtimestamp(os.path.getmtime(duplicate_file))
        orig_modified = datetime.datetime.fromtimestamp(os.path.getmtime(original_file))
        
        # HTML-Bericht erstellen
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaehrDocs Duplikatbericht</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
        }
        .container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .file-info {
            flex: 1;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin: 0 10px;
        }
        .comparison {
            background-color: #e9f7ef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .actions {
            background-color: #eaf2f8;
            padding: 15px;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>MaehrDocs Duplikatbericht</h1>
    <p>Erstellt am: """)
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            f.write("""</p>
            
    <div class="container">
        <div class="file-info">
            <h2>Duplikat-Datei</h2>
            <table>
                <tr>
                    <th>Dateiname</th>
                    <td>""")
            f.write(dup_filename)
            f.write("""</td>
                </tr>
                <tr>
                    <th>Pfad</th>
                    <td>""")
            f.write(duplicate_file)
            f.write("""</td>
                </tr>
                <tr>
                    <th>Größe</th>
                    <td>""")
            f.write(f"{dup_size / 1024:.2f} KB")
            f.write("""</td>
                </tr>
                <tr>
                    <th>Zuletzt geändert</th>
                    <td>""")
            f.write(dup_modified.strftime('%Y-%m-%d %H:%M:%S'))
            f.write("""</td>
                </tr>
            </table>
        </div>
        
        <div class="file-info">
            <h2>Original-Datei</h2>
            <table>
                <tr>
                    <th>Dateiname</th>
                    <td>""")
            f.write(orig_filename)
            f.write("""</td>
                </tr>
                <tr>
                    <th>Pfad</th>
                    <td>""")
            f.write(original_file)
            f.write("""</td>
                </tr>
                <tr>
                    <th>Größe</th>
                    <td>""")
            f.write(f"{orig_size / 1024:.2f} KB")
            f.write("""</td>
                </tr>
                <tr>
                    <th>Zuletzt geändert</th>
                    <td>""")
            f.write(orig_modified.strftime('%Y-%m-%d %H:%M:%S'))
            f.write("""</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="comparison">
        <h2>Vergleich</h2>
        <table>
            <tr>
                <th>Größenunterschied</th>
                <td>""")
            f.write(f"{abs(dup_size - orig_size) / 1024:.2f} KB")
            f.write("""</td>
            </tr>
            <tr>
                <th>Zeitunterschied</th>
                <td>""")
            f.write(f"{abs((orig_modified - dup_modified).total_seconds() / 3600):.2f} Stunden")
            f.write("""</td>
            </tr>
        </table>
    </div>
    
    <div class="actions">
        <h2>Maßnahmen</h2>
        <p>Die Duplikatdatei wurde in den Papierkorb verschoben.</p>
        <p>Für detaillierten Textvergleich bitte den Inhalt beider Dateien manuell vergleichen.</p>
    </div>
</body>
</html>""")
        
        logger.info(f"HTML-Bericht erstellt: {report_file}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des HTML-Berichts: {str(e)}")

def generate_json_report(report_file, duplicate_file, original_file, config, logger=None):
    """
    Generiert einen JSON-Bericht über ein erkanntes Duplikat.
    
    Args:
        report_file (str): Pfad zur zu erstellenden Berichtsdatei
        duplicate_file (str): Pfad zur Duplikatdatei
        original_file (str): Pfad zur Originaldatei
        config (dict): Die Anwendungskonfiguration
        logger: Logger-Instanz für die Protokollierung
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
        
    try:
        # Grundlegende Informationen sammeln
        dup_filename = os.path.basename(duplicate_file)
        orig_filename = os.path.basename(original_file)
        
        # Dateigrößen ermitteln
        dup_size = os.path.getsize(duplicate_file)
        orig_size = os.path.getsize(original_file)
        
        # Änderungsdaten ermitteln
        dup_modified = datetime.datetime.fromtimestamp(os.path.getmtime(duplicate_file))
        orig_modified = datetime.datetime.fromtimestamp(os.path.getmtime(original_file))
        
        # JSON-Struktur erstellen
        report_data = {
            "report_type": "duplicate_detection",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duplicate_file": {
                "filename": dup_filename,
                "path": duplicate_file,
                "size_bytes": dup_size,
                "size_kb": round(dup_size / 1024, 2),
                "last_modified": dup_modified.strftime("%Y-%m-%d %H:%M:%S")
            },
            "original_file": {
                "filename": orig_filename,
                "path": original_file,
                "size_bytes": orig_size,
                "size_kb": round(orig_size / 1024, 2),
                "last_modified": orig_modified.strftime("%Y-%m-%d %H:%M:%S")
            },
            "comparison": {
                "size_difference_bytes": abs(dup_size - orig_size),
                "size_difference_kb": round(abs(dup_size - orig_size) / 1024, 2),
                "time_difference_seconds": abs((orig_modified - dup_modified).total_seconds()),
                "time_difference_hours": round(abs((orig_modified - dup_modified).total_seconds() / 3600), 2)
            },
            "actions": {
                "duplicate_moved_to_trash": True,
                "report_generated": True
            }
        }
        
        # In JSON-Datei schreiben
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"JSON-Bericht erstellt: {report_file}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des JSON-Berichts: {str(e)}")