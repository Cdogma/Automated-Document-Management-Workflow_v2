#!/usr/bin/env python
"""
MaehrDocs Code Extractor

Dieses Skript durchsucht alle Python-Dateien im angegebenen Verzeichnis
und seiner Unterverzeichnisse und erstellt eine Textdatei mit dem gesamten Code.
"""

import os
import sys
from pathlib import Path

def extract_code(base_dir, output_file):
    """
    Extrahiert den Code aus allen Python-Dateien im angegebenen Verzeichnis
    und seinen Unterverzeichnissen.
    
    Args:
        base_dir: Das Basisverzeichnis, in dem gesucht werden soll
        output_file: Der Name der Ausgabedatei
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
    
    # Öffne die Ausgabedatei
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write("# MaehrDocs Code Übersicht\n\n")
        out_file.write(f"# Generiert am {os.path.basename(__file__)}\n\n")
        
        # Für jede Python-Datei
        for rel_path, file_path in python_files:
            out_file.write(f"\n\n# {'='*80}\n")
            out_file.write(f"# Datei: {rel_path}\n")
            out_file.write(f"# {'='*80}\n\n")
            
            # Lese den Inhalt und schreibe ihn in die Ausgabedatei
            try:
                with open(file_path, "r", encoding="utf-8") as in_file:
                    content = in_file.read()
                    out_file.write(content)
            except Exception as e:
                out_file.write(f"# Fehler beim Lesen der Datei: {str(e)}\n")
    
    print(f"Code aus {len(python_files)} Python-Dateien wurde in '{output_file}' extrahiert.")

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
        output_file = sys.argv[2]
    else:
        output_file = "maehrdocs_code_overview.txt"
    
    print(f"Extrahiere Code aus: {os.path.abspath(base_dir)}")
    print(f"Schreibe Ausgabe in: {output_file}")
    
    extract_code(base_dir, output_file)