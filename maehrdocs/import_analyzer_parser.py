"""
Parser-Funktionalität des Import-Analysators für MaehrDocs

Dieses Modul ist verantwortlich für das Parsen von Python-Dateien und das Extrahieren 
von Import-Anweisungen. Es verwendet primär das AST-Modul (Abstract Syntax Tree) für 
präzise Codeanalyse und bietet Fallback-Mechanismen mit regulären Ausdrücken für Dateien 
mit Syntaxfehlern.

Hauptfunktionalitäten:
- Extrahieren aller Import-Anweisungen aus Python-Quellcode
- Behandlung verschiedener Import-Typen (import, from-import)
- Extraktion von Modulnamen aus Dateipfaden
- Erkennung relativer Imports
"""

import os
import re
import ast
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def parse_imports(content):
    """
    Parst Python-Code und extrahiert alle Importanweisungen.
    
    Diese Funktion verwendet primär den Python-AST-Parser für eine präzise 
    syntaktische Analyse des Codes. Für Dateien mit Syntaxfehlern, die durch 
    den AST-Parser nicht verarbeitet werden können, wird ein Fallback mit 
    regulären Ausdrücken bereitgestellt.
    
    Unterstützte Import-Formate:
    - Einfache Imports: import module1, module2
    - Qualifizierte Imports: import module.submodule
    - From-Imports: from module import object
    - Absolute From-Imports: from module.submodule import object
    
    Args:
        content (str): Python-Quellcode als String
        
    Returns:
        list: Deduplizierte Liste von importierten Modulnamen
              (ohne die importierten Objekte, nur die Modulnamen)
    """
    imported_modules = []
    
    try:
        # Code mit dem AST-Parser analysieren
        tree = ast.parse(content)
        
        # Alle Import-Anweisungen im AST finden
        for node in ast.walk(tree):
            # Import-Anweisung (z.B. "import os", "import os, sys")
            if isinstance(node, ast.Import):
                for name in node.names:
                    imported_modules.append(name.name)
            
            # From-Import-Anweisung (z.B. "from os import path")
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:  # Absoluter Import (from module import x)
                    if node.module:
                        imported_modules.append(node.module)
                # Hinweis: Relative Imports (z.B. from .module import x) werden hier bewusst
                # ausgelassen, da sie keine externen Modulabhängigkeiten darstellen
                        
    except SyntaxError:
        # Fallback: Wenn der Code Syntaxfehler enthält, verwende reguläre Ausdrücke
        logger.warning("AST-Parsing fehlgeschlagen, verwende Regex-Fallback")
        imported_modules.extend(_parse_imports_with_regex(content))
        
    except Exception as e:
        logger.error(f"Fehler beim Parsen: {str(e)}")
    
    return list(set(imported_modules))  # Duplikate entfernen

def _parse_imports_with_regex(content):
    """
    Fallback-Methode zum Extrahieren von Imports mit regulären Ausdrücken.
    
    Diese Methode wird verwendet, wenn die AST-Analyse aufgrund von Syntaxfehlern 
    im Code fehlschlägt. Sie ist weniger genau als die AST-basierte Analyse, 
    kann aber auch bei fehlerhaftem Code grundlegende Import-Informationen extrahieren.
    
    Die Methode verwendet zwei Hauptmuster:
    1. Für direkte Imports: 'import modulname[, modulname2, ...]'
    2. Für from-Imports: 'from modulname import ...'
    
    Einschränkungen:
    - Erkennt keine Kommentare oder Strings, die Import-Schlüsselwörter enthalten
    - Kann bei komplexeren Import-Strukturen ungenau sein
    - Identifiziert keine bedingten Imports (z.B. in if-Blöcken)
    
    Args:
        content (str): Python-Quellcode
        
    Returns:
        list: Liste von importierten Modulnamen (möglicherweise mit Duplikaten)
    """
    imported_modules = []
    
    # Reguläre Ausdrücke für Import-Anweisungen
    # Import-Muster: 'import module' oder 'import module1, module2'
    import_pattern = r'^\s*import\s+([\w\.]+)(?:\s*,\s*([\w\.]+))*'
    # From-Import-Muster: 'from module import ...'
    from_pattern = r'^\s*from\s+([\w\.]+)\s+import'
    
    # Alle Zeilen durchgehen
    for line in content.split('\n'):
        # Import-Anweisungen finden
        import_match = re.match(import_pattern, line)
        if import_match:
            for group in import_match.groups():
                if group:  # Ignoriere None-Werte
                    imported_modules.append(group)
        
        # From-Import-Anweisungen finden
        from_match = re.match(from_pattern, line)
        if from_match and from_match.group(1):
            imported_modules.append(from_match.group(1))
    
    return imported_modules

def extract_module_name(file_path, project_dir):
    """
    Extrahiert den vollqualifizierten Modulnamen aus einem Dateipfad.
    
    Konvertiert einen Dateipfad in einen Python-Modulnamen entsprechend 
    der Python-Importkonventionen. Berücksichtigt dabei:
    - Relativen Pfad vom Projektverzeichnis
    - OS-spezifische Pfadtrennzeichen → Python-Punktnotation
    - Spezialbehandlung von __init__.py-Dateien als Verzeichnismodule
    
    Beispiele:
    - project_dir/module/file.py → module.file
    - project_dir/package/module/file.py → package.module.file
    - project_dir/package/__init__.py → package
    
    Args:
        file_path (str): Absoluter Pfad zur Python-Datei
        project_dir (str): Absoluter Pfad zum Basisverzeichnis des Projekts
        
    Returns:
        str: Der ermittelte Python-Modulname
    """
    # Relativen Pfad vom Projektverzeichnis aus erstellen
    rel_path = os.path.relpath(file_path, project_dir)
    
    # Dateiendung entfernen
    module_path = os.path.splitext(rel_path)[0]
    
    # Pfadtrenner durch Punkte ersetzen (OS-unabhängig)
    module_name = module_path.replace(os.path.sep, '.')
    
    # __init__.py-Dateien werden als Verzeichnismodul behandelt
    if module_name.endswith('.__init__'):
        module_name = module_name[:-9]  # .__init__ entfernen
        
    return module_name

def is_relative_import(import_statement):
    """
    Überprüft, ob ein Import-Statement ein relativer Import ist.
    
    Relative Imports beginnen mit einem oder mehreren Punkten und beziehen sich
    auf Module relativ zum aktuellen Modul, z.B.:
    - from . import module (Import aus demselben Paket)
    - from .. import module (Import aus dem übergeordneten Paket)
    - from .module import object (Import aus einem Modul im selben Paket)
    
    Args:
        import_statement (str): Die zu prüfende Import-Anweisung als String
        
    Returns:
        bool: True, wenn es sich um einen relativen Import handelt (beginnt mit '.'),
              False für absolute Imports
    """
    return import_statement.startswith('.')