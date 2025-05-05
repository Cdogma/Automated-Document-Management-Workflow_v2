"""
Berichterstellung und Lösungsvorschläge für den Import-Analysator

Dieses Modul ist verantwortlich für die Aufbereitung und Präsentation der
Analyseergebnisse in lesbaren Berichten und die Generierung von konkreten
Lösungsvorschlägen für identifizierte Probleme. Es stellt zwei Hauptfunktionen bereit:

1. generate_report - Erstellt einen umfassenden Analysebericht im Markdown-Format
   mit Übersichten, Statistiken und detaillierten Modulinformationen
   
2. suggest_solutions - Generiert maßgeschneiderte Lösungsvorschläge für erkannte
   zirkuläre Abhängigkeiten mit Codebeispielen und Best Practices

Die Berichte und Lösungsvorschläge werden als separate Markdown-Dateien gespeichert
und enthalten strukturierte, leicht verständliche Informationen für Entwickler.
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_report(analyzer, graph, output_file):
    """
    Erstellt einen detaillierten Bericht über die Importabhängigkeiten eines Projekts.
    
    Diese Funktion verarbeitet die Ergebnisse der Importanalyse und erstellt einen
    strukturierten Markdown-Bericht mit folgenden Hauptabschnitten:
    
    1. Übersicht - Zusammenfassung der Analyseergebnisse (Anzahl Module, Imports, Probleme)
    2. Zirkuläre Abhängigkeiten - Detaillierte Auflistung aller erkannten Zyklen
    3. Moduldetails - Informationen zu jedem Modul (Pfad, Imports, eingehende Abhängigkeiten)
    4. Statistiken - Quantitative Auswertungen (Top-Module nach Imports, häufig importierte Module)
    
    Die Berichte sind so gestaltet, dass sie sowohl für Menschen lesbar als auch
    für weitere automatisierte Verarbeitung geeignet sind (Markdown-Format).
    
    Args:
        analyzer (ImportAnalyzer): Die ImportAnalyzer-Instanz mit den Analyseergebnissen
        graph (DependencyGraph): Der Abhängigkeitsgraph zur Analyse von Beziehungen
        output_file (str): Pfad zur Ausgabedatei für den Bericht (Markdown)
    
    Returns:
        str: Absoluter Pfad zum erstellten Bericht
    """
    logger.info(f"Erstelle Bericht: {output_file}")
    
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Berichtkopf mit Metadaten
        f.write(f"# Import-Analyse Bericht - MaehrDocs\n\n")
        f.write(f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Analysiertes Verzeichnis: `{analyzer.project_dir}`\n\n")
        
        # Zusammenfassung der Ergebnisse
        f.write("## Zusammenfassung\n\n")
        f.write(f"- Anzahl Module: {len(analyzer.modules)}\n")
        f.write(f"- Anzahl Imports: {sum(len(imports) for imports in analyzer.imports.values())}\n")
        f.write(f"- Zirkuläre Importabhängigkeiten: {len(analyzer.circular_imports)}\n\n")
        
        # Zirkuläre Imports detailliert darstellen
        if analyzer.circular_imports:
            f.write("## Zirkuläre Importabhängigkeiten\n\n")
            f.write("Die folgenden zirkulären Abhängigkeiten wurden erkannt und sollten behoben werden:\n\n")
            
            for i, cycle in enumerate(analyzer.circular_imports, 1):
                path = cycle['path']
                f.write(f"### Zyklus {i}: {' -> '.join(path)}\n\n")
                
                # Detaillierte Informationen zu jedem Modul im Zyklus
                for module in path:
                    if module in analyzer.modules:
                        file_path = analyzer.modules[module]
                        rel_path = os.path.relpath(file_path, analyzer.project_dir)
                        f.write(f"- **{module}** (`{rel_path}`)\n")
                        
                        # Imports anzeigen, die Teil des Zyklus sind
                        if module in analyzer.imports:
                            cycle_imports = [imp for imp in analyzer.imports[module] if imp in path]
                            if cycle_imports:
                                f.write("  - Importiert: " + ", ".join(f"`{imp}`" for imp in cycle_imports) + "\n")
                
                f.write("\n")
        
        # Detaillierte Modulinformationen
        f.write("## Moduldetails\n\n")
        
        for module_name in sorted(analyzer.modules.keys()):
            f.write(f"### {module_name}\n\n")
            
            # Dateipfad
            file_path = analyzer.modules[module_name]
            rel_path = os.path.relpath(file_path, analyzer.project_dir)
            f.write(f"- **Datei:** `{rel_path}`\n")
            
            # Imports - unterscheiden zwischen internen (Projekt) und externen Imports
            if module_name in analyzer.imports and analyzer.imports[module_name]:
                f.write("- **Importiert:**\n")
                # Sortiere Imports für bessere Lesbarkeit
                for imp in sorted(analyzer.imports[module_name]):
                    # Markiere, wenn der Import zu einem anderen Modul im Projekt gehört
                    if imp in analyzer.modules:
                        f.write(f"  - `{imp}` (intern)\n")
                    else:
                        f.write(f"  - `{imp}` (extern)\n")
            else:
                f.write("- **Importiert:** Keine\n")
            
            # Module, die dieses Modul importieren (umgekehrte Abhängigkeiten)
            dependents = graph.get_dependents(module_name)
            if dependents:
                f.write("- **Importiert von:**\n")
                for dep in sorted(dependents):
                    f.write(f"  - `{dep}`\n")
            else:
                f.write("- **Importiert von:** Keinem\n")
            
            # Ist das Modul Teil von zirkulären Imports?
            in_cycles = [c for c in analyzer.circular_imports if module_name in c['path']]
            if in_cycles:
                f.write("- **In zirkulären Abhängigkeiten:**\n")
                for i, cycle in enumerate(in_cycles, 1):
                    cycle_str = ' -> '.join(cycle['path'])
                    f.write(f"  - Zyklus {i}: `{cycle_str}`\n")
                    
            f.write("\n")
        
        # Statistiken und Kennzahlen
        f.write("## Statistiken\n\n")
        
        # Module mit den meisten Imports (komplexeste Module)
        f.write("### Module mit den meisten Imports\n\n")
        modules_by_imports = sorted(
            [(m, len(imps)) for m, imps in analyzer.imports.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        f.write("| Modul | Anzahl Imports |\n")
        f.write("|-------|---------------|\n")
        for module, count in modules_by_imports[:10]:  # Top 10
            f.write(f"| `{module}` | {count} |\n")
        
        f.write("\n")
        
        # Am häufigsten importierte Module (zentrale Module)
        f.write("### Am häufigsten importierte Module\n\n")
        import_counts = {}
        for imports in analyzer.imports.values():
            for imp in imports:
                if imp in analyzer.modules:  # Nur interne Module
                    import_counts[imp] = import_counts.get(imp, 0) + 1
        
        most_imported = sorted(
            [(m, c) for m, c in import_counts.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        f.write("| Modul | Importiert von |\n")
        f.write("|-------|---------------|\n")
        for module, count in most_imported[:10]:  # Top 10
            f.write(f"| `{module}` | {count} |\n")
    
    logger.info(f"Bericht erstellt: {output_file}")
    return output_file

def suggest_solutions(analyzer, graph, output_dir):
    """
    Generiert maßgeschneiderte Lösungsvorschläge für zirkuläre Importabhängigkeiten.
    
    Diese Funktion analysiert die identifizierten zirkulären Abhängigkeiten und erstellt
    einen Bericht mit konkreten, aktionablen Lösungsvorschlägen. Für jeden Zyklus werden
    mehrere Lösungsstrategien vorgeschlagen, darunter:
    
    1. Extrahieren gemeinsamer Funktionalität in separate Module
    2. Verwenden von "Lazy Imports" (Verschieben von Imports in Funktionen)
    3. Implementierung von Dependency Injection
    4. Verwendung von TYPE_CHECKING für Typ-Annotationen
    5. Umstrukturierung der Modulhierarchie
    
    Jeder Lösungsvorschlag wird mit konkreten Codebeispielen und Erläuterungen versehen,
    um die Implementierung zu erleichtern.
    
    Args:
        analyzer (ImportAnalyzer): Die ImportAnalyzer-Instanz mit den Analyseergebnissen
        graph (DependencyGraph): Der Abhängigkeitsgraph zur Analyse von Beziehungen
        output_dir (str): Verzeichnis für die Ausgabedatei
    
    Returns:
        str: Pfad zum erstellten Lösungsvorschlagsbericht
    """
    output_file = os.path.join(output_dir, "import_solutions.md")
    logger.info(f"Erstelle Lösungsvorschläge: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Lösungsvorschläge für Importprobleme\n\n")
        f.write(f"Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Wenn keine Probleme gefunden wurden
        if not analyzer.circular_imports:
            f.write("## Keine zirkulären Importabhängigkeiten gefunden\n\n")
            f.write("Die Analyse hat keine zirkulären Importabhängigkeiten im Projekt identifiziert. ")
            f.write("Die aktuelle Modulstruktur ist in dieser Hinsicht optimal.\n\n")
            f.write("### Präventive Maßnahmen\n\n")
            f.write("Um auch in Zukunft zirkuläre Abhängigkeiten zu vermeiden, empfiehlt sich:\n\n")
            f.write("1. Regelmäßige Importanalysen durchführen\n")
            f.write("2. Klare Modulhierarchie definieren und dokumentieren\n")
            f.write("3. Gemeinsame Basismodule für häufig benötigte Funktionalität einrichten\n")
            
            return output_file
        
        # Einführung bei gefundenen Problemen
        f.write("## Zirkuläre Importabhängigkeiten\n\n")
        f.write("Die folgenden zirkulären Abhängigkeiten wurden identifiziert und benötigen Aufmerksamkeit. ")
        f.write("Diese Zyklen könnten bei bestimmten Import-Konstellationen zu Problemen führen, ")
        f.write("beispielsweise zu ImportError-Ausnahmen oder unerwarteten Verhaltensweisen.\n\n")
        
        # Für jeden Zyklus individuelle Lösungen vorschlagen
        for i, cycle in enumerate(analyzer.circular_imports, 1):
            path = cycle['path']
            f.write(f"### Zyklus {i}: {' -> '.join(path)}\n\n")
            
            # Analyse des spezifischen Zyklus
            f.write("#### Analyse\n\n")
            
            # Moduldetails anzeigen
            for module in path:
                if module in analyzer.modules:
                    file_path = analyzer.modules[module]
                    rel_path = os.path.relpath(file_path, analyzer.project_dir)
                    f.write(f"- **{module}** (`{rel_path}`)\n")
                    
                    # Imports anzeigen, die an diesem Zyklus beteiligt sind
                    if module in analyzer.imports:
                        cycle_imports = [imp for imp in analyzer.imports[module] if imp in path]
                        if cycle_imports:
                            f.write("  - Importiert aus diesem Zyklus: " + 
                                  ", ".join(f"`{imp}`" for imp in cycle_imports) + "\n")
            
            # Detaillierte Lösungsvorschläge
            f.write("\n#### Lösungsvorschläge\n\n")
            
            # Strategie 1: Gemeinsames Modul extrahieren
            f.write("**1. Gemeinsames Modul extrahieren:**\n")
            f.write("Identifizieren Sie gemeinsam genutzte Funktionalität zwischen diesen Modulen und extrahieren ")
            f.write("Sie diese in ein separates, neues Modul, das von beiden abhängigen Modulen importiert wird. ")
            f.write("Dies ist besonders effektiv, wenn die zirkuläre Abhängigkeit durch gegenseitige ")
            f.write("Nutzung ähnlicher Funktionen entsteht.\n\n")
            
            # Beispielcode mit dynamisch generiertem Modulnamen
            module_base = path[0].split('.')[-1] if '.' in path[0] else path[0]
            common_module = f"{'.'.join(path[0].split('.')[:-1])}.common_{module_base}" if '.' in path[0] else f"common_{module_base}"
            
            f.write("```python\n")
            f.write(f"# Neues Modul: {common_module}.py\n")
            f.write("# Gemeinsame Funktionalität hier implementieren\n")
            f.write("def shared_function():\n")
            f.write("    # Implementierung\n")
            f.write("    pass\n\n")
            f.write("class SharedClass:\n")
            f.write("    # Implementierung\n")
            f.write("    pass\n\n")
            f.write("# In den ursprünglichen Modulen:\n")
            f.write(f"from {common_module} import SharedClass, shared_function\n")
            f.write("```\n\n")
            
            # Strategie 2: Lazy Imports
            f.write("**2. Lazy Imports verwenden:**\n")
            f.write("Verschieben Sie die Imports in die Funktionen oder Methoden, die sie tatsächlich benötigen, ")
            f.write("anstatt sie auf Modulebene zu importieren. Dies vermeidet Probleme bei der Initialisierung ")
            f.write("und löst viele zirkuläre Abhängigkeiten elegante Weise.\n\n")
            
            f.write("```python\n")
            f.write("# Anstatt: from other_module import SomeClass\n\n")
            f.write("def some_function():\n")
            f.write("    # Lazy Import - wird erst bei Funktionsaufruf geladen\n")
            f.write("    from other_module import SomeClass\n")
            f.write("    \n")
            f.write("    # Rest der Funktion\n")
            f.write("    instance = SomeClass()\n")
            f.write("    return instance.process()\n")
            f.write("```\n\n")
            
            # Strategie 3: Dependency Injection
            f.write("**3. Dependency Injection:**\n")
            f.write("Übergeben Sie die benötigten Objekte als Parameter, anstatt die Module direkt zu importieren. ")
            f.write("Dies entkoppelt die Module und ermöglicht eine flexiblere Struktur. Dependency Injection ist ")
            f.write("besonders wertvoll bei komplexeren Anwendungen und vereinfacht auch das Testen.\n\n")
            
            f.write("```python\n")
            f.write("# Anstatt:\n")
            f.write("from other_module import SomeClass\n")
            f.write("def process_data():\n")
            f.write("    obj = SomeClass()\n")
            f.write("    return obj.process()\n\n")
            f.write("# Besser (mit Dependency Injection):\n")
            f.write("def process_data(processor):\n")
            f.write("    return processor.process()\n\n")
            f.write("# Aufruf:\n")
            f.write("from other_module import SomeClass\n")
            f.write("result = process_data(SomeClass())\n")
            f.write("```\n\n")
            
            # Strategie 4: Typ-Annotationen verschieben
            f.write("**4. Typ-Annotationen mit 'TYPE_CHECKING':**\n")
            f.write("Wenn die zirkulären Imports nur für Typ-Annotationen verwendet werden, ")
            f.write("nutzen Sie den `typing.TYPE_CHECKING`-Mechanismus. Dies ermöglicht die statische ")
            f.write("Typprüfung während der Entwicklung, ohne zirkuläre Abhängigkeiten zur Laufzeit.\n\n")
            
            f.write("```python\n")
            f.write("from typing import TYPE_CHECKING, Optional\n\n")
            f.write("if TYPE_CHECKING:\n")
            f.write("    from other_module import SomeClass  # Import nur für Typchecking\n\n")
            f.write("def function() -> 'SomeClass':  # String-Annotation verwenden\n")
            f.write("    # Zur Laufzeit importieren\n")
            f.write("    from other_module import SomeClass\n")
            f.write("    return SomeClass()\n\n")
            f.write("# Alternative mit Union und Optional:\n")
            f.write("def another_function() -> Optional['SomeClass']:\n")
            f.write("    # Implementierung\n")
            f.write("    pass\n")
            f.write("```\n\n")
            
            # Strategie 5: Modulstruktur überdenken
            f.write("**5. Modulstruktur überdenken:**\n")
            f.write("Möglicherweise deutet der Zyklus auf ein grundlegenderes Designproblem hin. ")
            f.write("Erwägen Sie eine Umstrukturierung der Modulhierarchie, um klare Abhängigkeitsrichtungen zu schaffen. ")
            f.write("Dies kann bedeuten, Module zusammenzuführen oder Funktionalität neu zu organisieren nach dem ")
            f.write("Prinzip der Verantwortungstrennung (Separation of Concerns).\n\n")
            
            f.write("Fragen zur Überprüfung:\n")
            f.write("- Sollten diese Module tatsächlich separate Einheiten sein?\n")
            f.write("- Gibt es eine natürliche Hierarchie zwischen ihnen?\n")
            f.write("- Könnten einige Funktionen besser in einem gemeinsamen übergeordneten Modul platziert werden?\n\n")
        
        # Allgemeine Best Practices
        f.write("## Allgemeine Empfehlungen\n\n")
        
        f.write("### 1. Konsistente Importkonventionen\n\n")
        f.write("Verwenden Sie einheitliche Import-Muster im gesamten Projekt:\n")
        f.write("- Absolute Imports für externe Module und projektweite Importe\n")
        f.write("- Relative Imports für Module innerhalb desselben Pakets\n")
        f.write("- Sortieren Sie Imports nach Konvention (z.B. Standardbibliothek → Drittanbieterbibliotheken → Projektmodule)\n\n")
        
        f.write("### 2. Klare Modulhierarchie\n\n")
        f.write("Etablieren Sie eine klare Hierarchie von Abhängigkeiten:\n")
        f.write("- Basismodule sollten keine höheren Module importieren\n")
        f.write("- Gemeinsame Funktionalität in eigenen Modulen organisieren\n")
        f.write("- Eindeutige Richtung des Datenflusses definieren\n\n")
        
        f.write("### 3. Modulgrößen optimieren\n\n")
        f.write("Finden Sie die richtige Balance für die Modulgranularität:\n")
        f.write("- Zu viele kleine Module können zu unnötiger Komplexität führen\n")
        f.write("- Zu große Module werden unübersichtlich und schwer zu warten\n")
        f.write("- Zusammengehörige Funktionalität sollte im gleichen Modul bleiben\n\n")
        
        f.write("### 4. Regelmäßige Überprüfung\n\n")
        f.write("Integrieren Sie die Importanalyse in Ihren Entwicklungsprozess:\n")
        f.write("- Führen Sie regelmäßig und nach größeren Refactorings Analysen durch\n")
        f.write("- Verwenden Sie CI/CD-Pipelines zur Erkennung neuer zirkulärer Abhängigkeiten\n")
        f.write("- Dokumentieren Sie die beabsichtigte Architektur und Modulstruktur\n")
    
    logger.info(f"Lösungsvorschläge erstellt: {output_file}")
    return output_file