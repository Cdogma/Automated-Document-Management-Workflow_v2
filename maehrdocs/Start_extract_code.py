#!/usr/bin/env python
"""
MaehrDocs Code Extractor

Dieses Skript durchsucht alle Python-Dateien im angegebenen Verzeichnis
und seiner Unterverzeichnisse und erstellt eine oder mehrere Textdateien
mit dem gesamten Code. Wenn die Ausgabedatei zu groß wird, wird der Code
automatisch auf mehrere Dateien aufgeteilt.

Die generierten Dateien enthalten einen Zeitstempel im Dateinamen und
sind auf ca. 4 MB begrenzt, um eine optimale Handhabung zu gewährleisten.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Maximale Größe für eine einzelne Ausgabedatei (in Bytes)
# 4 MB ist ein guter Wert für Textdateien
MAX_FILE_SIZE = 4 * 1024 * 1024  # 5 MB in Bytes

def estimate_file_size(content):
    """
    Schätzt die Größe eines Textinhalts in Bytes.
    
    Args:
        content: Der zu schätzende Textinhalt
        
    Returns:
        int: Geschätzte Größe in Bytes
    """
    return len(content.encode('utf-8'))

def create_output_file(base_name, timestamp, file_index=None):
    """
    Erstellt einen Dateinamen basierend auf dem Basisnamen, Zeitstempel und einem Index.
    
    Args:
        base_name: Der Basisname der Ausgabedatei
        timestamp: Der Zeitstempel für den Dateinamen (Format: YYYY-MM-DD_HH-MM)
        file_index: Der Index für die Datei (None für die erste Datei)
        
    Returns:
        str: Der vollständige Dateiname
    """
    name, ext = os.path.splitext(base_name)
    
    if file_index is None:
        return f"{name}_{timestamp}{ext}"
    
    return f"{name}_{timestamp}_Teil{file_index}{ext}"

def extract_code(base_dir, output_file_base):
    """
    Extrahiert den Code aus allen Python-Dateien im angegebenen Verzeichnis
    und seinen Unterverzeichnissen. Teilt die Ausgabe auf mehrere Dateien auf,
    wenn die maximale Dateigröße erreicht wird.
    
    Args:
        base_dir: Das Basisverzeichnis, in dem gesucht werden soll
        output_file_base: Der Basisname der Ausgabedatei
    
    Returns:
        list: Liste der erstellten Ausgabedateien
    """
    # Alle Python-Dateien im Verzeichnis und Unterverzeichnissen finden
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        # Ignoriere __pycache__ Verzeichnisse
        if "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                python_files.append((rel_path, file_path))
    
    # Sortiere die Dateien nach relativem Pfad
    python_files.sort()
    
    if not python_files:
        print(f"Keine Python-Dateien in {base_dir} gefunden!")
        return []
    
    # Timestamp für die Generierung und Dateinamen
    now = datetime.now()
    timestamp_display = now.strftime("%Y-%m-%d %H:%M:%S")
    timestamp_filename = now.strftime("%Y-%m-%d_%H-%M")
    
    # Header für jede Datei
    header = "# MaehrDocs Code Übersicht\n\n"
    header += f"# Generiert am {timestamp_display} durch {os.path.basename(__file__)}\n\n"
    
    # Initialisiere Variablen für Dateiaufteilung
    current_content = header
    current_size = estimate_file_size(current_content)
    file_index = None
    created_files = []
    
    # Verarbeitete Dateien zählen
    processed_files = 0
    total_files = len(python_files)
    
    # Jede Python-Datei verarbeiten
    for rel_path, file_path in python_files:
        processed_files += 1
        
        # Füge Dateiseparator hinzu
        file_separator = f"\n\n# {'='*80}\n"
        file_separator += f"# Datei: {rel_path}\n"
        file_separator += f"# {'='*80}\n\n"
        
        try:
            # Lese den Inhalt der Datei
            with open(file_path, "r", encoding="utf-8") as in_file:
                file_content = in_file.read()
            
            # Gesamtgröße des hinzuzufügenden Inhalts berechnen
            content_to_add = file_separator + file_content
            content_size = estimate_file_size(content_to_add)
            
            # Prüfen, ob die maximale Dateigröße überschritten würde
            if current_size + content_size > MAX_FILE_SIZE and current_content != header:
                # Speichere die aktuelle Datei
                output_name = create_output_file(output_file_base, timestamp_filename, file_index)
                with open(output_name, "w", encoding="utf-8") as out_file:
                    out_file.write(current_content)
                
                # Merke dir den Dateinamen
                created_files.append(output_name)
                print(f"Datei erstellt: {output_name} ({current_size/1024/1024:.2f} MB)")
                
                # Beginne eine neue Datei
                if file_index is None:
                    file_index = 2
                else:
                    file_index += 1
                
                # Neuer Header für die Fortsetzungsdatei
                continuation_header = header
                continuation_header += f"# Fortsetzung Teil {file_index} - Datei {processed_files} bis {total_files} von {total_files}\n\n"
                
                current_content = continuation_header
                current_size = estimate_file_size(current_content)
            
            # Füge den Inhalt zur aktuellen Datei hinzu
            current_content += content_to_add
            current_size = estimate_file_size(current_content)
            
        except Exception as e:
            error_message = f"# Fehler beim Lesen der Datei: {str(e)}\n"
            current_content += file_separator + error_message
            current_size = estimate_file_size(current_content)
    
    # Speichere die letzte Datei
    output_name = create_output_file(output_file_base, timestamp_filename, file_index)
    with open(output_name, "w", encoding="utf-8") as out_file:
        out_file.write(current_content)
    
    # Merke dir den Dateinamen
    created_files.append(output_name)
    print(f"Datei erstellt: {output_name} ({current_size/1024/1024:.2f} MB)")
    
    return created_files

if __name__ == "__main__":
    # Wenn kein Verzeichnis angegeben wurde, verwende das aktuelle Verzeichnis
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maehrdocs")
        
        # Wenn das Verzeichnis nicht existiert, verwende das aktuelle Verzeichnis
        if not os.path.exists(base_dir):
            base_dir = "."
    
    # Wenn keine Ausgabedatei angegeben wurde, verwende einen Standardnamen
    if len(sys.argv) > 2:
        output_file_base = sys.argv[2]
    else:
        output_file_base = "maehrdocs_code_overview.txt"
    
    # Aktuelle Zeit für die Ausgabe
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    print(f"Extrahiere Code aus: {os.path.abspath(base_dir)}")
    print(f"Schreibe Ausgabe in: {output_file_base} mit Zeitstempel {current_time}")
    
    created_files = extract_code(base_dir, output_file_base)
    
    if created_files:
        print(f"\nCode wurde in {len(created_files)} Datei(en) extrahiert:")
        for file in created_files:
            file_size = os.path.getsize(file) / 1024 / 1024  # Größe in MB
            print(f" - {file} ({file_size:.2f} MB)")
    else:
        print("Keine Dateien wurden erstellt.")