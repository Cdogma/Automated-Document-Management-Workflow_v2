"""
Kernfunktionalität des Import-Analysators für MaehrDocs

Dieses Modul bildet das Herzstück des Import-Analysators und enthält die Hauptklasse 
ImportAnalyzer. Diese Klasse ist verantwortlich für das Scannen eines Python-Projekts, 
die Verarbeitung der einzelnen Python-Dateien, die Extraktion der Importabhängigkeiten 
und die Erkennung von zirkulären Importabhängigkeiten, die zu Laufzeitproblemen führen 
können.

Der Analyseprozess erfolgt in mehreren Stufen:
1. Rekursives Scannen des Projektverzeichnisses nach Python-Dateien
2. Extraktion der Modulnamen und Import-Anweisungen aus jeder Datei
3. Aufbau eines Abhängigkeitsnetzwerks zwischen den Modulen
4. Durchführung einer Tiefensuche zur Erkennung zirkulärer Abhängigkeiten
"""

import os
import logging
from pathlib import Path

from .import_analyzer_parser import parse_imports, extract_module_name

logger = logging.getLogger(__name__)

class ImportAnalyzer:
    """
    Hauptklasse für die Analyse von Importabhängigkeiten in Python-Projekten.
    
    Diese Klasse koordiniert den gesamten Analyseprozess, von der Erkennung 
    der Python-Dateien über die Extraktion der Imports bis zur Identifikation 
    von zirkulären Importabhängigkeiten.
    
    Attribute:
        project_dir (str): Absoluter Pfad zum Projektverzeichnis
        modules (dict): Zuordnung von Modulnamen zu ihren Dateipfaden {module_name: file_path}
        imports (dict): Zuordnung von Modulen zu ihren importierten Modulen {module_name: [imported_modules]}
        circular_imports (list): Liste identifizierter zirkulärer Importpfade
    """
    
    def __init__(self, project_dir):
        """
        Initialisiert den Import-Analyzer für ein spezifisches Projektverzeichnis.
        
        Args:
            project_dir (str): Verzeichnis des zu analysierenden Projekts (absoluter Pfad)
        """
        self.project_dir = os.path.abspath(project_dir)
        self.modules = {}  # {module_name: file_path}
        self.imports = {}  # {module_name: [imported_modules]}
        self.circular_imports = []  # Liste von zirkulären Importpfaden
    
    def scan_project(self):
        """
        Durchsucht das Projektverzeichnis nach Python-Dateien und analysiert deren Imports.
        
        Dieser Prozess umfasst:
        1. Rekursives Durchsuchen aller Verzeichnisse (außer __pycache__ und versteckten Ordnern)
        2. Verarbeiten jeder gefundenen Python-Datei (.py)
        3. Erkennung zirkulärer Importabhängigkeiten über eine Tiefensuche
        
        Die Ergebnisse werden in den Objektattributen modules, imports und circular_imports gespeichert.
        """
        logger.info(f"Scanne Projektverzeichnis: {self.project_dir}")
        
        # Python-Dateien im Projekt finden
        for root, dirs, files in os.walk(self.project_dir):
            # __pycache__ und andere versteckte Verzeichnisse überspringen
            dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)
        
        # Zirkuläre Imports erkennen
        self._detect_circular_imports()
        
        logger.info(f"Scan abgeschlossen. Gefunden: {len(self.modules)} Module, {len(self.circular_imports)} zirkuläre Imports.")
    
    def _process_file(self, file_path):
        """
        Verarbeitet eine einzelne Python-Datei und extrahiert Modulname und Imports.
        
        Diese Methode:
        1. Extrahiert den Modulnamen aus dem Dateipfad
        2. Liest und analysiert den Dateiinhalt, um alle Import-Anweisungen zu finden
        3. Speichert die Ergebnisse in den Objektattributen
        
        Args:
            file_path (str): Absoluter Pfad zur Python-Datei
        """
        rel_path = os.path.relpath(file_path, self.project_dir)
        logger.debug(f"Verarbeite Datei: {rel_path}")
        
        try:
            # Modulname aus Dateipfad extrahieren (z.B. 'package.module')
            module_name = extract_module_name(file_path, self.project_dir)
            
            # Datei parsen, um Imports zu extrahieren
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                import_statements = parse_imports(content)
            
            # Modulname und Imports speichern
            self.modules[module_name] = file_path
            self.imports[module_name] = import_statements
            
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten von {rel_path}: {str(e)}")
    
    def _detect_circular_imports(self):
        """
        Erkennt zirkuläre Importabhängigkeiten im Projekt.
        
        Diese Methode startet eine Tiefensuche (DFS) von jedem Modul aus,
        um zirkuläre Pfade im Abhängigkeitsgraphen zu finden. Jeder gefundene
        Zyklus wird in der circular_imports-Liste gespeichert.
        """
        logger.info("Suche nach zirkulären Imports...")
        
        # Für jedes Modul eine Tiefensuche starten
        for module_name in self.modules:
            # DFS starten, um zirkuläre Pfade zu finden
            visited = {}  # {module: path_to_module}
            self._dfs_for_cycles(module_name, visited, [])
    
    def _dfs_for_cycles(self, current, visited, path):
        """
        Führt eine Tiefensuche (DFS) durch, um zirkuläre Importpfade zu erkennen.
        
        Diese Methode implementiert einen angepassten DFS-Algorithmus zur Erkennung
        von Zyklen in einem gerichteten Graphen. Der Algorithmus funktioniert wie folgt:
        
        1. Wenn der aktuelle Knoten bereits im Pfad ist, wurde ein Zyklus gefunden
        2. Andernfalls wird der aktuelle Knoten zum Pfad hinzugefügt
        3. Für jeden Import des aktuellen Moduls wird die DFS rekursiv fortgesetzt
        4. Bei Rückkehr wird der aktuelle Knoten aus dem Pfad entfernt (Backtracking)
        
        Gefundene Zyklen werden nur einmal gespeichert, auch wenn sie mehrfach entdeckt werden.
        
        Args:
            current (str): Name des aktuellen Moduls
            visited (dict): Dictionary der bereits besuchten Module
            path (list): Aktueller Pfad in der DFS (Liste von Modulnamen)
        """
        # Wenn wir dieses Modul schon besucht haben, haben wir einen Kreis gefunden
        if current in visited:
            # Kreis extrahieren, beginnend vom ersten Vorkommen des aktuellen Moduls im Pfad
            cycle_path = path[path.index(current):]
            cycle_path.append(current)  # Kreis schließen, indem wir das aktuelle Modul anhängen
            
            # Generiere einen eindeutigen Schlüssel für diesen Zyklus
            cycle_key = '->'.join(cycle_path)
            
            # Nur eindeutige Kreise speichern
            if cycle_key not in [c['key'] for c in self.circular_imports]:
                self.circular_imports.append({
                    'key': cycle_key,  # Eindeutiger Identifikationsstring
                    'path': cycle_path.copy()  # Kopie des Pfads (Liste von Modulnamen)
                })
            return
        
        # Dieses Modul als besucht markieren
        visited[current] = True
        path.append(current)
        
        # Alle importierten Module durchgehen
        if current in self.imports:
            for imported_module in self.imports[current]:
                # Nur Module im Projekt verfolgen (externe Module ignorieren)
                if imported_module in self.modules:
                    # Wichtig: visited und path müssen kopiert werden, um Seiteneffekte zu vermeiden
                    self._dfs_for_cycles(imported_module, visited.copy(), path.copy())
        
        # Backtracking - Modul aus Pfad und besuchten Modulen entfernen
        path.pop()
        del visited[current]
    
    def get_module_details(self, module_name):
        """
        Gibt detaillierte Informationen zu einem bestimmten Modul zurück.
        
        Diese Methode sammelt umfassende Informationen über ein Modul:
        - Modulname und Dateipfad
        - Liste der von diesem Modul importierten Module
        - Liste der Module, die dieses Modul importieren (umgekehrte Abhängigkeiten)
        
        Args:
            module_name (str): Name des Moduls
            
        Returns:
            dict: Dictionary mit Moduldetails oder None, wenn das Modul nicht gefunden wurde
        """
        if module_name not in self.modules:
            return None
        
        # Module finden, die das angegebene Modul importieren
        imported_by = []
        for mod, imports in self.imports.items():
            if module_name in imports:
                imported_by.append(mod)
        
        return {
            'name': module_name,
            'file_path': self.modules[module_name],
            'imports': self.imports.get(module_name, []),
            'imported_by': imported_by
        }