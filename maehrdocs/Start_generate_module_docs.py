#!/usr/bin/env python
"""
MaehrDocs Modul-Dokumentations-Generator

Dieses Skript durchsucht rekursiv alle Python-Dateien im MaehrDocs-Paketverzeichnis und generiert 
eine strukturierte Markdown-Dokumentation. Die Dokumentation enthält für jedes Modul:

- Den relativen Dateipfad
- Den Modul-Docstring (sofern vorhanden)
- Eine Liste aller Funktionen mit Kurzbeschreibung
- Eine Übersicht aller Klassen inklusive Methoden und zugehöriger Docstrings

Die Ausgabe eignet sich ideal zur internen Projektdokumentation, Codepflege oder als öffentliches Entwickler-Referenzdokument. 
Die Struktur wird automatisch anhand der Dateihierarchie erstellt und in separate Markdown-Dateien aufgeteilt, wenn eine
maximale Dateigröße erreicht wird.

Verwendung:
    - Dieses Skript wird typischerweise im Root-Verzeichnis des Projekts ausgeführt.
    - Das Zielverzeichnis (standardmäßig `./maehrdocs`) kann bei Bedarf im Code angepasst werden.

Hinweis:
    - Fehlerhafte oder nicht-parsbare Python-Dateien werden übersprungen und im Ergebnis als Hinweistext vermerkt.
    - Nur `.py`-Dateien werden berücksichtigt. `__pycache__`-Ordner werden ignoriert.
    - Große Dokumentationen werden automatisch auf mehrere Dateien aufgeteilt.
"""

import os
import re
import ast
import importlib.util
from pathlib import Path
from datetime import datetime

# Maximale Größe für eine einzelne Dokumentationsdatei (in Bytes)
# 2 MB ist ein guter Wert, der problemlos hochgeladen werden kann
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB in Bytes

def get_docstring(node):
    """Extrahiert den Docstring aus einem AST-Knoten."""
    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
        return node.body[0].value.s.strip()
    return ""

def estimate_markdown_size(markdown_content):
    """
    Schätzt die Größe eines Markdown-Inhalts in Bytes.
    
    Args:
        markdown_content: Der zu schätzende Markdown-Inhalt
        
    Returns:
        int: Geschätzte Größe in Bytes
    """
    return len(markdown_content.encode('utf-8'))

def analyze_python_file(file_path):
    """Analysiert eine Python-Datei und extrahiert Funktionen, Klassen und deren Docstrings."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            content = file.read()
            tree = ast.parse(content)
        except Exception as e:
            return {
                'module_docstring': f"Fehler beim Parsen: {str(e)}",
                'functions': [],
                'classes': []
            }
    
    module_docstring = get_docstring(tree)
    
    functions = []
    classes = []
    
    # Top-Level-Definitionen finden
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_docstring = get_docstring(node)
            # Einfache Zusammenfassung aus dem Docstring extrahieren
            summary = func_docstring.split('\n')[0] if func_docstring else "Keine Beschreibung verfügbar"
            functions.append({
                'name': node.name,
                'docstring': func_docstring,
                'summary': summary
            })
        elif isinstance(node, ast.ClassDef):
            class_docstring = get_docstring(node)
            summary = class_docstring.split('\n')[0] if class_docstring else "Keine Beschreibung verfügbar"
            
            methods = []
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_docstring = get_docstring(class_node)
                    method_summary = method_docstring.split('\n')[0] if method_docstring else "Keine Beschreibung verfügbar"
                    methods.append({
                        'name': class_node.name,
                        'docstring': method_docstring,
                        'summary': method_summary
                    })
            
            classes.append({
                'name': node.name,
                'docstring': class_docstring,
                'summary': summary,
                'methods': methods
            })
    
    return {
        'module_docstring': module_docstring,
        'functions': functions,
        'classes': classes
    }

def generate_module_markdown(module_name, module):
    """Generiert den Markdown-Abschnitt für ein bestimmtes Modul."""
    markdown = f"### {module_name}\n\n"
    
    # Dateipfad
    rel_path = os.path.relpath(module['file_path'])
    markdown += f"**Dateipfad:** `{rel_path}`\n\n"
    
    # Moduldokumentationsstring
    module_docstring = module['analysis']['module_docstring']
    if module_docstring:
        # Begrenze die Länge des Docstrings
        if len(module_docstring) > 500:
            module_docstring = module_docstring[:497] + "..."
        markdown += f"{module_docstring}\n\n"
    
    # Funktionen
    functions = module['analysis']['functions']
    if functions:
        markdown += "#### Funktionen\n\n"
        for func in functions:
            markdown += f"- `{func['name']}()` - {func['summary']}\n"
        markdown += "\n"
    
    # Klassen
    classes = module['analysis']['classes']
    if classes:
        markdown += "#### Klassen\n\n"
        for cls in classes:
            markdown += f"- `{cls['name']}` - {cls['summary']}\n"
            
            # Methoden
            methods = cls['methods']
            if methods:
                markdown += "  - Methoden:\n"
                for method in methods:
                    if not method['name'].startswith('_'):  # Private Methoden ausschließen
                        markdown += f"    - `{method['name']}()` - {method['summary']}\n"
        markdown += "\n"
    
    markdown += "---\n\n"
    return markdown

def create_markdown_file(content, file_index=None):
    """
    Erstellt eine Markdown-Datei mit dem angegebenen Inhalt.
    
    Args:
        content: Der Markdown-Inhalt
        file_index: Der Index für die Datei (None für die erste Datei)
        
    Returns:
        str: Der Pfad zur erstellten Datei
    """
    if file_index is None:
        output_file = "MaehrDocs_Modulübersicht.md"
    else:
        output_file = f"MaehrDocs_Modulübersicht_Teil{file_index}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file

def generate_markdown(base_dir, max_files=50):
    """
    Generiert eine Markdown-Dokumentation der Module und deren Inhalte.
    Die Dokumentation wird auf mehrere Dateien aufgeteilt, wenn sie zu groß wird.
    
    Args:
        base_dir: Das Basisverzeichnis
        max_files: Maximale Anzahl an Dateien zur Verarbeitung
    """
    modules = {}
    file_count = 0
    
    # Nur Python-Dateien in unserem Zielordner und dessen Unterordnern durchsuchen
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                module_path = rel_path.replace(os.path.sep, '.').replace('.py', '')
                
                # Überprüfe Dateigröße - überspringe sehr große Dateien
                if os.path.getsize(file_path) > 100000:  # 100 KB
                    print(f"Überspringe große Datei: {file_path}")
                    continue
                
                if module_path == '__init__':
                    # Für __init__.py-Dateien setzen wir den Namen auf den Ordnernamen
                    module_path = os.path.basename(root)
                
                modules[module_path] = {
                    'file_path': file_path,
                    'analysis': analyze_python_file(file_path)
                }
                
                file_count += 1
                if file_count >= max_files:
                    print(f"Maximale Anzahl an Dateien ({max_files}) erreicht.")
                    break
        
        if file_count >= max_files:
            break
    
    # Markdown-Header generieren
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"# MaehrDocs Modulübersicht\n\n"
    header += f"Diese Dokumentation wurde automatisch am {timestamp} generiert und bietet einen Überblick über {file_count} Module im MaehrDocs Projekt.\n\n"
    
    # Inhaltsverzeichnis generieren
    toc = "## Inhaltsverzeichnis\n\n"
    
    # Hauptmodule im Inhaltsverzeichnis
    toc += "### Module\n"
    for module_name in sorted(modules.keys()):
        if '.' not in module_name:
            module = modules[module_name]
            module_docstring = module['analysis']['module_docstring']
            summary = module_docstring.split('\n')[0] if module_docstring else "Keine Beschreibung verfügbar"
            toc += f"- [{module_name}](#{module_name.lower().replace('.', '-')}) - {summary}\n"
    
    # Untermodule im Inhaltsverzeichnis
    namespaces = {}
    for module_name in sorted(modules.keys()):
        if '.' in module_name:
            namespace = module_name.split('.')[0]
            if namespace not in namespaces:
                namespaces[namespace] = []
            namespaces[namespace].append(module_name)
    
    for namespace in sorted(namespaces.keys()):
        toc += f"\n### {namespace} Module\n"
        for module_name in sorted(namespaces[namespace]):
            module = modules[module_name]
            module_docstring = module['analysis']['module_docstring']
            summary = module_docstring.split('\n')[0] if module_docstring else "Keine Beschreibung verfügbar"
            toc += f"- [{module_name}](#{module_name.lower().replace('.', '-')}) - {summary}\n"
    
    # Markdown-Inhalte generieren und auf Dateien aufteilen
    current_content = header + toc + "\n## Module\n\n"
    current_size = estimate_markdown_size(current_content)
    created_files = []
    file_index = None
    
    # Erst die Hauptmodule
    for module_name in sorted(modules.keys()):
        if '.' not in module_name:
            module_markdown = generate_module_markdown(module_name, modules[module_name])
            module_size = estimate_markdown_size(module_markdown)
            
            # Wenn die aktuelle Datei mit diesem Modul zu groß würde, erstelle eine neue Datei
            if current_size + module_size > MAX_FILE_SIZE and current_content != header + toc + "\n## Module\n\n":
                # Speichere die aktuelle Datei
                output_file = create_markdown_file(current_content, file_index)
                created_files.append(output_file)
                print(f"Datei erstellt: {output_file} ({current_size/1024/1024:.2f} MB)")
                
                # Erstelle eine neue Datei mit Header und setze den Index
                if file_index is None:
                    file_index = 2
                else:
                    file_index += 1
                current_content = header + f"\n## Module (Fortsetzung Teil {file_index})\n\n"
                current_size = estimate_markdown_size(current_content)
            
            # Modul zur aktuellen Datei hinzufügen
            current_content += module_markdown
            current_size = estimate_markdown_size(current_content)
    
    # Dann die Untermodule nach Namespace sortiert
    for namespace in sorted(namespaces.keys()):
        namespace_header = f"\n## {namespace} Module\n\n"
        namespace_size = estimate_markdown_size(namespace_header)
        
        # Wenn die aktuelle Datei mit diesem Namespace-Header zu groß würde, erstelle eine neue Datei
        if current_size + namespace_size > MAX_FILE_SIZE:
            output_file = create_markdown_file(current_content, file_index)
            created_files.append(output_file)
            print(f"Datei erstellt: {output_file} ({current_size/1024/1024:.2f} MB)")
            
            # Erstelle eine neue Datei mit Header und setze den Index
            if file_index is None:
                file_index = 2
            else:
                file_index += 1
            current_content = header + f"\n## {namespace} Module (Teil {file_index})\n\n"
            current_size = estimate_markdown_size(current_content)
        else:
            current_content += namespace_header
            current_size = estimate_markdown_size(current_content)
        
        # Untermodule dieses Namespace hinzufügen
        for module_name in sorted(namespaces[namespace]):
            module_markdown = generate_module_markdown(module_name, modules[module_name])
            module_size = estimate_markdown_size(module_markdown)
            
            # Wenn die aktuelle Datei mit diesem Modul zu groß würde, erstelle eine neue Datei
            if current_size + module_size > MAX_FILE_SIZE:
                output_file = create_markdown_file(current_content, file_index)
                created_files.append(output_file)
                print(f"Datei erstellt: {output_file} ({current_size/1024/1024:.2f} MB)")
                
                # Erstelle eine neue Datei mit Header und setze den Index
                if file_index is None:
                    file_index = 2
                else:
                    file_index += 1
                current_content = header + f"\n## {namespace} Module (Fortsetzung Teil {file_index})\n\n"
                current_size = estimate_markdown_size(current_content)
            
            # Modul zur aktuellen Datei hinzufügen
            current_content += module_markdown
            current_size = estimate_markdown_size(current_content)
    
    # Speichere die letzte Datei
    output_file = create_markdown_file(current_content, file_index)
    created_files.append(output_file)
    print(f"Datei erstellt: {output_file} ({current_size/1024/1024:.2f} MB)")
    
    return created_files

if __name__ == "__main__":
    # Pfad zum MaehrDocs-Paket
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maehrdocs")
    
    # Prüfen, ob das Verzeichnis existiert
    if not os.path.exists(base_dir):
        print(f"Das Verzeichnis {base_dir} wurde nicht gefunden.")
        # Versuche, das aktuelle Verzeichnis zu verwenden
        base_dir = "."
        print(f"Verwende stattdessen das aktuelle Verzeichnis: {os.path.abspath(base_dir)}")
    
    # Markdown generieren mit Begrenzung auf max. 50 Dateien
    created_files = generate_markdown(base_dir, max_files=50)
    
    print(f"Dokumentation wurde in {len(created_files)} Datei(en) gespeichert:")
    for file in created_files:
        file_size = os.path.getsize(file) / 1024 / 1024  # Größe in MB
        print(f" - {file} ({file_size:.2f} MB)")