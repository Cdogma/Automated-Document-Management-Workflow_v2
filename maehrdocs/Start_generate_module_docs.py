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
Die Struktur wird automatisch anhand der Dateihierarchie erstellt und in die Datei "MaehrDocs_Modulübersicht.md" geschrieben.

Verwendung:
    - Dieses Skript wird typischerweise im Root-Verzeichnis des Projekts ausgeführt.
    - Das Zielverzeichnis (standardmäßig `./maehrdocs`) kann bei Bedarf im Code angepasst werden.

Hinweis:
    - Fehlerhafte oder nicht-parsbare Python-Dateien werden übersprungen und im Ergebnis als Hinweistext vermerkt.
    - Nur `.py`-Dateien werden berücksichtigt. `__pycache__`-Ordner werden ignoriert.
"""

import os
import re
import ast
import importlib.util
from pathlib import Path

def get_docstring(node):
    """Extrahiert den Docstring aus einem AST-Knoten."""
    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
        return node.body[0].value.s.strip()
    return ""

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
    
    for node in ast.walk(tree):
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
            for class_node in ast.walk(node):
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

def generate_markdown(base_dir):
    """Generiert eine Markdown-Dokumentation der Module und deren Inhalte."""
    modules = {}
    
    # Nur Python-Dateien in unserem Zielordner und dessen Unterordnern durchsuchen
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_dir)
                module_path = rel_path.replace(os.path.sep, '.').replace('.py', '')
                
                if module_path == '__init__':
                    # Für __init__.py-Dateien setzen wir den Namen auf den Ordnernamen
                    module_path = os.path.basename(root)
                
                modules[module_path] = {
                    'file_path': file_path,
                    'analysis': analyze_python_file(file_path)
                }
    
    # Markdown generieren
    markdown = "# MaehrDocs Modulübersicht\n\n"
    markdown += "Diese Dokumentation wurde automatisch generiert und bietet einen Überblick über alle Module im MaehrDocs Projekt.\n\n"
    
    # Table of Contents
    markdown += "## Inhaltsverzeichnis\n\n"
    
    markdown += "### Module\n"
    # Erst die Hauptmodule
    for module_name in sorted(modules.keys()):
        if '.' not in module_name:
            module = modules[module_name]
            module_docstring = module['analysis']['module_docstring']
            summary = module_docstring.split('\n')[0] if module_docstring else "Keine Beschreibung verfügbar"
            markdown += f"- [{module_name}](#{module_name.lower().replace('.', '-')}) - {summary}\n"
    
    # Dann die Untermodule nach Namespace sortiert
    namespaces = {}
    for module_name in sorted(modules.keys()):
        if '.' in module_name:
            namespace = module_name.split('.')[0]
            if namespace not in namespaces:
                namespaces[namespace] = []
            namespaces[namespace].append(module_name)
    
    for namespace in sorted(namespaces.keys()):
        markdown += f"\n### {namespace} Module\n"
        for module_name in sorted(namespaces[namespace]):
            module = modules[module_name]
            module_docstring = module['analysis']['module_docstring']
            summary = module_docstring.split('\n')[0] if module_docstring else "Keine Beschreibung verfügbar"
            markdown += f"- [{module_name}](#{module_name.lower().replace('.', '-')}) - {summary}\n"
    
    # Detaillierte Modulbeschreibungen
    markdown += "\n## Module\n\n"
    
    # Erst die Hauptmodule
    for module_name in sorted(modules.keys()):
        if '.' not in module_name:
            module = modules[module_name]
            markdown += generate_module_markdown(module_name, module)
    
    # Dann die Untermodule nach Namespace sortiert
    for namespace in sorted(namespaces.keys()):
        markdown += f"\n## {namespace} Module\n\n"
        for module_name in sorted(namespaces[namespace]):
            module = modules[module_name]
            markdown += generate_module_markdown(module_name, module)
    
    return markdown

def generate_module_markdown(module_name, module):
    """Generiert den Markdown-Abschnitt für ein bestimmtes Modul."""
    markdown = f"### {module_name}\n\n"
    
    # Dateipfad
    rel_path = os.path.relpath(module['file_path'])
    markdown += f"**Dateipfad:** `{rel_path}`\n\n"
    
    # Moduldokumentationsstring
    module_docstring = module['analysis']['module_docstring']
    if module_docstring:
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
                    if method['name'] != '__init__':  # Private Methoden ausschließen
                        markdown += f"    - `{method['name']}()` - {method['summary']}\n"
        markdown += "\n"
    
    markdown += "---\n\n"
    return markdown

if __name__ == "__main__":
    # Pfad zum MaehrDocs-Paket
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maehrdocs")
    
    # Prüfen, ob das Verzeichnis existiert
    if not os.path.exists(base_dir):
        print(f"Das Verzeichnis {base_dir} wurde nicht gefunden.")
        # Versuche, das aktuelle Verzeichnis zu verwenden
        base_dir = "."
        print(f"Verwende stattdessen das aktuelle Verzeichnis: {os.path.abspath(base_dir)}")
    
    # Markdown generieren
    markdown = generate_markdown(base_dir)
    
    # In Datei schreiben
    output_file = "MaehrDocs_Modulübersicht.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Dokumentation wurde in {output_file} gespeichert.")