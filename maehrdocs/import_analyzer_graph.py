"""
Graph-Funktionalität des Import-Analysators für MaehrDocs

Dieses Modul bietet eine Graph-basierte Darstellung von Modulabhängigkeiten
und Funktionen zur Analyse und Visualisierung dieser Abhängigkeitsstrukturen.
Es implementiert eine DependencyGraph-Klasse, die einen gerichteten Graphen
repräsentiert, sowie Hilfsfunktionen zum Aufbau und zur Visualisierung des Graphen.

Die Graph-Repräsentation ermöglicht:
- Einfache Navigation durch Abhängigkeitsbeziehungen
- Analyse der Modularchitektur
- Identifikation von stark vernetzten Komponenten
- Visualisierung des Abhängigkeitsnetzwerks
"""

import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class DependencyGraph:
    """
    Repräsentiert einen gerichteten Graphen von Modulabhängigkeiten.
    
    Diese Klasse implementiert einen spezialisierten gerichteten Graphen für
    Modulabhängigkeiten. Sie speichert sowohl ausgehende als auch eingehende
    Kanten für jeden Knoten, um effiziente Abfragen in beide Richtungen zu ermöglichen.
    
    Attribute:
        nodes (set): Menge aller Modulnamen (Knoten im Graphen)
        edges (dict): Dictionary von ausgehenden Kanten {from_module: [to_modules]}
        reverse_edges (dict): Dictionary von eingehenden Kanten {to_module: [from_modules]}
    """
    def __init__(self):
        """
        Initialisiert einen leeren Abhängigkeitsgraphen.
        
        Erstellt leere Datenstrukturen für Knoten und Kanten in beide Richtungen.
        """
        self.nodes = set()  # Menge aller Modulnamen
        self.edges = {}  # Ausgehende Kanten {from_module: [to_modules]}
        self.reverse_edges = {}  # Eingehende Kanten {to_module: [from_modules]}
    
    def add_node(self, module_name):
        """
        Fügt einen Knoten (Modul) zum Graphen hinzu.
        
        Wenn der Knoten bereits existiert, wird er nicht dupliziert.
        Für jeden neuen Knoten werden leere Listen für ausgehende und 
        eingehende Kanten initialisiert.
        
        Args:
            module_name (str): Name des hinzuzufügenden Moduls
        """
        if module_name not in self.nodes:
            self.nodes.add(module_name)
            self.edges[module_name] = []  # Liste der ausgehenden Kanten (importierte Module)
            self.reverse_edges[module_name] = []  # Liste der eingehenden Kanten (importierende Module)
    
    def add_edge(self, from_module, to_module):
        """
        Fügt eine gerichtete Kante (Abhängigkeit) zwischen zwei Modulen hinzu.
        
        Die Kante repräsentiert, dass from_module das to_module importiert.
        Wenn eine der Knoten noch nicht existiert, werden sie automatisch hinzugefügt.
        Doppelte Kanten werden vermieden.
        
        Args:
            from_module (str): Name des importierenden Moduls (Quellknoten)
            to_module (str): Name des importierten Moduls (Zielknoten)
        """
        # Sicherstellen, dass beide Knoten existieren
        self.add_node(from_module)
        self.add_node(to_module)
        
        # Kante hinzufügen, wenn sie noch nicht existiert
        if to_module not in self.edges[from_module]:
            self.edges[from_module].append(to_module)  # Ausgehende Kante
            self.reverse_edges[to_module].append(from_module)  # Eingehende Kante
    
    def get_dependencies(self, module_name):
        """
        Gibt alle direkten Abhängigkeiten (Imports) eines Moduls zurück.
        
        Args:
            module_name (str): Name des Moduls
        
        Returns:
            list: Liste von Modulnamen, die vom angegebenen Modul importiert werden
                 (leere Liste, wenn das Modul keine bekannten Abhängigkeiten hat)
        """
        return self.edges.get(module_name, [])
    
    def get_dependents(self, module_name):
        """
        Gibt alle Module zurück, die das angegebene Modul importieren (abhängige Module).
        
        Dies sind die umgekehrten Abhängigkeiten oder "Einflussbereich" eines Moduls.
        
        Args:
            module_name (str): Name des Moduls
        
        Returns:
            list: Liste von Modulnamen, die das angegebene Modul importieren
                 (leere Liste, wenn keine Module von diesem Modul abhängig sind)
        """
        return self.reverse_edges.get(module_name, [])
    
    def find_cycles(self):
        """
        Findet alle Zyklen (zirkuläre Abhängigkeiten) im Abhängigkeitsgraphen.
        
        Diese Methode verwendet einen modifizierten Tiefensuchalgorithmus (DFS) zur
        Erkennung von Zyklen in gerichteten Graphen. Für jeden Knoten wird eine
        neue DFS gestartet, um alle möglichen Zyklen zu finden.
        
        Returns:
            list: Liste von Zyklen, wobei jeder Zyklus eine Liste von Modulnamen ist,
                  die einen geschlossenen Pfad im Graphen bilden
        """
        cycles = []
        visited = {}  # {node: in_current_path}
        
        def dfs(node, path):
            """
            Hilfsfunktion für die Tiefensuche.
            
            Args:
                node (str): Aktueller Knoten
                path (list): Aktueller Pfad in der DFS
            """
            if node in visited:
                if visited[node]:  # Wenn der Knoten auf dem aktuellen Pfad ist
                    # Zyklus gefunden
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    cycles.append(cycle)
                return
            
            visited[node] = True  # Markiere als "auf aktuellem Pfad"
            path.append(node)
            
            for neighbor in self.edges.get(node, []):
                dfs(neighbor, path.copy())
            
            path.pop()
            visited[node] = False  # Markiere als "nicht mehr auf aktuellem Pfad"
        
        # Starte DFS von jedem Knoten aus
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        return cycles

def build_dependency_graph(modules, imports):
    """
    Erstellt einen Abhängigkeitsgraphen aus Modulen und ihren Imports.
    
    Diese Funktion konvertiert die rohen Analysedaten (Module und ihre Imports)
    in eine strukturierte Graph-Repräsentation für weitergehende Analysen.
    
    Args:
        modules (dict): Zuordnung von Modulnamen zu Dateipfaden {module_name: file_path}
        imports (dict): Zuordnung von Modulen zu ihren Imports {module_name: [imported_modules]}
    
    Returns:
        DependencyGraph: Ein vollständig aufgebauter Abhängigkeitsgraph
    """
    graph = DependencyGraph()
    
    # Alle Module als Knoten hinzufügen
    for module_name in modules:
        graph.add_node(module_name)
    
    # Importabhängigkeiten als Kanten hinzufügen
    for module_name, imported_modules in imports.items():
        for imported_module in imported_modules:
            # Nur Kanten zu bekannten Modulen (im Projekt) hinzufügen
            # Externe Module (z.B. aus der Standardbibliothek) werden ignoriert
            if imported_module in modules:
                graph.add_edge(module_name, imported_module)
    
    return graph

def visualize_graph(graph, output_file):
    """
    Erstellt eine visuelle Darstellung des Abhängigkeitsgraphen.
    
    Diese Funktion erzeugt eine grafische Darstellung des Abhängigkeitsgraphen
    mithilfe der Bibliotheken pydot und graphviz. Die Visualisierung wird in der
    angegebenen Datei gespeichert (PNG, PDF, SVG, etc.).
    
    Visualisierungseigenschaften:
    - Module werden als Knoten dargestellt (Rechtecke, hellblau)
    - Abhängigkeiten werden als gerichtete Pfeile dargestellt
    - Das Layout ist von links nach rechts orientiert
    
    Args:
        graph (DependencyGraph): Der zu visualisierende Abhängigkeitsgraph
        output_file (str): Pfad zur Ausgabedatei (Format wird aus Dateiendung abgeleitet)
    
    Returns:
        bool: True bei Erfolg, False bei Fehler
    """
    try:
        import pydot
        
        # Neuen Graphen mit horizontalem Layout erstellen
        dot_graph = pydot.Dot(graph_type='digraph', rankdir='LR')
        
        # Knoten hinzufügen
        for node in graph.nodes:
            dot_node = pydot.Node(node, shape='box', style='filled', 
                                 fillcolor='lightblue')
            dot_graph.add_node(dot_node)
        
        # Kanten hinzufügen
        for from_node, to_nodes in graph.edges.items():
            for to_node in to_nodes:
                edge = pydot.Edge(from_node, to_node)
                dot_graph.add_edge(edge)
        
        # Graph in Datei schreiben (Format wird aus der Dateiendung abgeleitet)
        output_format = output_file.split('.')[-1]
        dot_graph.write(output_file, format=output_format)
        logger.info(f"Abhängigkeitsgraph gespeichert unter: {output_file}")
        
        return True
    except ImportError:
        logger.error("Visualisierung erfordert die Pakete 'pydot' und 'graphviz'.")
        logger.info("Installieren Sie diese mit: pip install pydot graphviz")
        return False
    except Exception as e:
        logger.error(f"Fehler bei der Graphvisualisierung: {str(e)}")
        return False