# MaehrDocs - Automatisches Dokumentenmanagementsystem

Ein modernes, Python-basiertes System zur automatischen Verarbeitung und Verwaltung von PDF-Dokumenten mit KI-Unterstützung.

![MaehrDocs](https://via.placeholder.com/800x400?text=MaehrDocs)

## Funktionen

- **Automatische Verarbeitung**: PDFs werden aus dem Eingangsordner gelesen, analysiert und umbenannt
- **KI-Analyse**: Verwendet OpenAI, um Dokumenttyp, Absender, Datum und andere Informationen zu extrahieren
- **Einheitliche Umbenennung**: Alle Dokumente werden nach einem standardisierten Schema benannt
- **Duplikaterkennung**: Vermeidet doppelte Dokumente durch intelligente Textähnlichkeitsanalyse mit optimierter Verarbeitung für deutsche Texte
- **Moderne GUI**: Benutzerfreundliche Oberfläche mit Dark Mode und Dashboard
- **Drag & Drop**: Einfaches Hinzufügen von Dateien per Drag & Drop (optional, wenn tkinterdnd2 installiert ist)
- **Zentrales Messaging-System**: Vereinheitlichte Benachrichtigungen und Dialoge
- **Fehlerbehandlung**: Robust gegen Fehler mit zentralem Error-Handler
- **Modulare Struktur**: Verbesserte Wartbarkeit durch logische Komponentenaufteilung

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- OpenAI API-Schlüssel (in .env Datei)

### Pakete installieren

```bash
pip install pymupdf python-dotenv openai pyyaml pillow
```

Für Drag & Drop-Funktionalität (optional):

```bash
pip install tkinterdnd2
```

### Einrichtung

1. Klonen Sie das Repository oder laden Sie den Quellcode herunter
2. Erstellen Sie eine `.env` Datei mit Ihrem OpenAI API-Schlüssel:
   ```
   OPENAI_API_KEY=dein_api_key_hier
   ```
3. Führen Sie `python maehrdocs/main.py --rebuild-config` aus, um die Konfigurationsdatei zu erstellen
4. Passen Sie die Pfadeinstellungen in `autodocs_config.yaml` an Ihre Bedürfnisse an

## Verwendung

### Grafische Benutzeroberfläche

Die einfachste Methode ist die Verwendung der GUI:

```bash
python Start_MAEHRDOCS_GUI_Launcher.py
```

Oder alternativ:

```bash
python maehrdocs/START_maehrdocs.py
```

Unter Windows können Sie auch die `maehrdocs.bat` Datei doppelklicken.

### Kommandozeile

Für fortgeschrittene Benutzer steht auch eine Kommandozeilenschnittstelle zur Verfügung:

```bash
# Alle Dokumente im Eingangsordner verarbeiten
python maehrdocs/main.py

# Simulationsmodus (keine Änderungen)
python maehrdocs/main.py --dry-run

# Einzelne Datei verarbeiten
python maehrdocs/main.py --single-file "C:\Pfad\zu\deiner\datei.pdf"

# Erweiterte Protokollierung
python maehrdocs/main.py -v
python maehrdocs/main.py -vv  # Noch detaillierter

# Konfiguration zurücksetzen
python maehrdocs/main.py --rebuild-config

# Vorhandene Dateien überschreiben
python maehrdocs/main.py --force
```

## Projektstruktur

Das Projekt verwendet eine modulare Struktur mit getrennten Komponenten:

```
maehrdocs/
  ├── __init__.py                    # Paketdefinition und Exporte
  ├── config.py                      # Konfigurationsverwaltung (Singleton)
  ├── config_core.py                 # Kern-Konfigurationsmanagement
  ├── config_defaults.py             # Standardkonfigurationswerte
  ├── config_utils.py                # Hilfsfunktionen für Konfiguration
  ├── document_processor.py          # Dokumentenverarbeitung
  ├── duplicate_detector.py          # Optimierte Duplikaterkennung
  ├── error_handler.py               # Zentrale Fehlerbehandlung
  ├── file_operations.py             # Dateioperationen
  ├── filename_generator.py          # Generierung standardisierter Namen
  ├── import_analyzer.py             # Import-Analysator
  ├── import_analyzer_core.py        # Kernfunktionalität des Analysators
  ├── import_analyzer_graph.py       # Abhängigkeits-Graph-Funktionen
  ├── import_analyzer_parser.py      # Parser für Importanalyse
  ├── import_analyzer_report.py      # Berichterstellung für Importe
  ├── main.py                        # Kommandozeilenbasierter Einstiegspunkt
  ├── openai_integration.py          # Integration mit OpenAI API
  ├── text_extractor.py              # PDF-Textextraktion
  ├── START_maehrdocs.py             # Starter-Skript für GUI
  ├── Start_extract_code.py          # Code-Extraktionsskript
  ├── Start_generate_module_docs.py  # Dokumentationsgenerator
  ├── Start_Paketvergleich_venv.py   # venv-Paket-Vergleichstool
  ├── Start_upload_to_github.py      # GitHub-Upload-Tool
  └── gui/                           # GUI-Komponenten
      ├── __init__.py                # GUI-Modul-Exporte
      ├── gui_actions.py             # Event-Handler und Aktionen
      ├── gui_alerts.py              # Benachrichtigungskomponenten
      ├── gui_animations.py          # Animationseffekte
      ├── gui_buttons.py             # Button-Komponenten
      ├── gui_cards.py               # Karten- und Container-Komponenten
      ├── gui_command_executor.py    # Befehlsausführung
      ├── gui_core.py                # Hauptklasse für die GUI
      ├── gui_dashboard.py           # Dashboard-Funktionalität
      ├── gui_dialog.py              # Dialogkomponenten
      ├── gui_document_actions.py    # Dokumentenaktionen
      ├── gui_document_comparison.py # Dokumentenvergleich
      ├── gui_document_loader.py     # Dokumentenlader
      ├── gui_document_viewer.py     # Dokumentenansicht
      ├── gui_drop_handlers.py       # Drag & Drop-Handler
      ├── gui_form_fields.py         # Formularfeldkomponenten
      ├── gui_forms.py               # Zentrale Formularkomponenten
      ├── gui_help.py                # Hilfefunktionen
      ├── gui_layout.py              # Layout-Komponenten
      ├── gui_logger.py              # Logging-Funktionalität
      ├── gui_messaging.py           # Zentrales Messaging-System
      ├── gui_notification_handlers.py # Benachrichtigungshandler
      ├── gui_notifications.py       # Benachrichtigungssystem
      └── gui_settings.py            # Einstellungsdialog

# Einstiegspunkte in der Root-Ebene
Start_MAEHRDOCS_GUI_Launcher.py      # GUI-Launcher für MaehrDocs-Tools
Start_MAEHRDOCS_Launcher.py          # Tool-Launcher-Menü
```

## Konfiguration

Die Konfiguration erfolgt über die `autodocs_config.yaml` Datei. Wichtige Einstellungen:

### Pfade

```yaml
paths:
  input_dir: C:\Users\username\OneDrive\09_AutoDocs\01_InboxDocs
  output_dir: C:\Users\username\OneDrive\09_AutoDocs\02_FinalDocs
  trash_dir: C:\Users\username\OneDrive\09_AutoDocs\03_TrashDocs
```

### OpenAI-Einstellungen

```yaml
openai:
  model: gpt-3.5-turbo   # Alternativ: gpt-4o für höhere Präzision
  temperature: 0.3
  max_retries: 3
```

### Dokumentenverarbeitung

```yaml
document_processing:
  max_file_size_mb: 20
  similarity_threshold: 0.85   # Schwellenwert für Duplikaterkennung
  valid_doc_types:
    - rechnung
    - vertrag
    - brief
    - meldung
    - bescheid
    - dokument
    - antrag
```

### GUI-Einstellungen

```yaml
gui:
  show_duplicate_popup: true
  notify_on_completion: true
  enable_sounds: false
  notify_on_new_documents: true
```

## Tools und Utilities

MaehrDocs bietet verschiedene Hilfswerkzeuge:

- **Import-Analysator**: Erkennt und hilft, zirkuläre Importabhängigkeiten zu beheben
- **Modul-Dokumentationsgenerator**: Erstellt eine Übersicht aller Module und deren Funktionen
- **Code-Extraktor**: Extrahiert Code aus allen Python-Dateien des Projekts
- **Paketvergleich**: Vergleicht installierte Pakete mit Anforderungen
- **GitHub-Upload**: Schnelles Hochladen von Änderungen zu GitHub

## Besonderheiten der Architektur

- **Modularisierte Struktur**: Logische Aufteilung in kleinere, spezialisierte Module
- **Singleton-Konfigurationsmanager**: Konsistenter Zugriff auf Konfiguration
- **Zentrales Messaging-System**: Einheitliche Benachrichtigungen und Dialoge
- **Error-Handler-Klasse**: Verbesserte Fehlerbehandlung und -nachverfolgung
- **Fassade-Designmuster**: Bei GUI-Komponenten zur Vereinfachung der Schnittstellen

## Beiträge

Beiträge sind willkommen! Bitte öffnen Sie ein Issue oder einen Pull Request.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## Abhängigkeiten

### Erforderlich
- Python 3.8 oder höher
- PyMuPDF (fitz)
- python-dotenv
- openai
- pyyaml

### Optional
- tkinterdnd2 - Für Drag & Drop-Funktionalität (empfohlen für bessere Benutzererfahrung)
- pillow - Für verbesserte GUI-Elemente