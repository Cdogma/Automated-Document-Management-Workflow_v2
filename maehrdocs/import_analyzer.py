"""
Import-Analysator für MaehrDocs

Hauptmodul des Import-Analysators, das die Analyse von Importabhängigkeiten 
und die Erkennung von zirkulären Imports koordiniert.
"""

import os
import sys
import logging
from pathlib import Path

from .import_analyzer_core import ImportAnalyzer
from .import_analyzer_parser import parse_imports
from .import_analyzer_graph import build_dependency_graph
from .import_analyzer_report import generate_report, suggest_solutions

logger = logging.getLogger(__name__)

def analyze_project(project_dir=None, output_file=None, visualize=False):
    """
    Analysiert ein Python-Projekt auf Importabhängigkeiten und zirkuläre Imports.
    
    Args:
        project_dir (str): Verzeichnis des zu analysierenden Projekts. 
                         Wenn None, wird das aktuelle Verzeichnis verwendet.
        output_file (str): Dateipfad für den Bericht. Wenn None, wird ein 
                          Standardname verwendet.
        visualize (bool): Gibt an, ob eine Visualisierung des Abhängigkeitsgraphen 
                        erstellt werden soll.
    
    Returns:
        tuple: (ImportAnalyzer-Instanz, Berichtspfad)
    """
    # Standard-Projektverzeichnis ist das aktuelle Verzeichnis
    if project_dir is None:
        project_dir = os.getcwd()
    
    # Standard-Ausgabedatei
    if output_file is None:
        output_file = os.path.join(project_dir, "import_analysis_report.md")
    
    logger.info(f"Analysiere Projekt in: {project_dir}")
    
    # Importanalyse durchführen
    analyzer = ImportAnalyzer(project_dir)
    analyzer.scan_project()
    
    # Abhängigkeitsgraph erstellen
    graph = build_dependency_graph(analyzer.modules, analyzer.imports)
    
    # Bericht generieren
    report_path = generate_report(analyzer, graph, output_file)
    
    # Lösungsvorschläge
    if analyzer.circular_imports:
        suggest_solutions(analyzer, graph, os.path.dirname(report_path))
    
    # Visualisierung erstellen, wenn gewünscht
    if visualize:
        try:
            from .import_analyzer_graph import visualize_graph
            visualize_graph(graph, os.path.join(os.path.dirname(report_path), "dependencies.png"))
        except ImportError:
            logger.warning("Visualisierungsabhängigkeiten fehlen. Installiere graphviz und pydot für Visualisierungen.")
    
    return analyzer, report_path

def main():
    """
    Hauptfunktion, wenn das Modul als Skript ausgeführt wird.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="MaehrDocs Import-Analysator")
    parser.add_argument("-d", "--directory", help="Zu analysierendes Verzeichnis")
    parser.add_argument("-o", "--output", help="Ausgabedatei für den Bericht")
    parser.add_argument("-v", "--visualize", action="store_true", help="Erstellt eine Visualisierung")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    # Logging konfigurieren
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Analyse durchführen
    analyzer, report_path = analyze_project(args.directory, args.output, args.visualize)
    
    print(f"\nAnalyse abgeschlossen.")
    print(f"Gefundene Module: {len(analyzer.modules)}")
    print(f"Gefundene Imports: {len(analyzer.imports)}")
    print(f"Zirkuläre Imports: {len(analyzer.circular_imports)}")
    print(f"Bericht erstellt: {report_path}")

if __name__ == "__main__":
    main()