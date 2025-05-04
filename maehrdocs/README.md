# MaehrDocs - Automatisches Dokumentenmanagementsystem

Ein Python-basiertes System zur automatischen Verarbeitung und Verwaltung von PDF-Dokumenten mit Hilfe von KI.

![MaehrDocs](https://via.placeholder.com/800x400?text=MaehrDocs)

## Funktionen

- **Automatische Verarbeitung**: PDFs werden aus dem Eingangsordner gelesen, analysiert und umbenannt
- **KI-Analyse**: Verwendet OpenAI, um Dokumenttyp, Absender, Datum und andere Informationen zu extrahieren
- **Einheitliche Umbenennung**: Alle Dokumente werden nach einem standardisierten Schema benannt
- **Duplikaterkennung**: Vermeidet doppelte Dokumente durch intelligente Textähnlichkeitsanalyse
- **Moderne GUI**: Benutzerfreundliche Oberfläche mit Dark Mode und Dashboard
- **Drag & Drop**: Einfaches Hinzufügen von Dateien per Drag & Drop (optional, wenn tkinterdnd2 installiert ist)

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
3. Führen Sie `python main.py --rebuild-config` aus, um die Konfigurationsdatei zu erstellen
4. Passen Sie die Pfadeinstellungen in `autodocs_config.yaml` an Ihre Bedürfnisse an

## Verwendung

### Grafische Benutzeroberfläche

Die einfachste Methode ist die Verwendung der GUI:

```bash
python start_maehrdocs.py
```

Oder unter Windows einfach die `maehrdocs.bat` Datei doppelklicken.

### Kommandozeile

Für fortgeschrittene Benutzer steht auch eine Kommandozeilenschnittstelle zur Verfügung:

```bash
# Alle Dokumente im Eingangsordner verarbeiten
python main.py

# Simulationsmodus (keine Änderungen)
python main.py --dry-run

# Einzelne Datei verarbeiten
python main.py --single-file "C:\Pfad\zu\deiner\datei.pdf"

# Erweiterte Protokollierung
python main.py -v
python main.py -vv  # Noch detaillierter

# Konfiguration zurücksetzen
python main.py --rebuild-config

# Vorhandene Dateien überschreiben
python main.py --force
```

## Projektstruktur

Das Projekt verwendet eine modulare Struktur:

```
maehrdocs/
  ├── __init__.py         # Paketdefinition und Exporte
  ├── config.py           # Konfigurationsverwaltung
  ├── document_processor.py  # Dokumentenverarbeitung
  ├── duplicate_detector.py  # Duplikaterkennung
  └── gui/                # GUI-Komponenten
      ├── __init__.py
      ├── gui_core.py     # Hauptklasse für die GUI
      ├── gui_components.py  # Wiederverwendbare UI-Komponenten
      ├── gui_dashboard.py   # Dashboard-Funktionalität
      ├── gui_settings.py    # Einstellungsdialog
      ├── gui_document_viewer.py  # Dokumentenansicht
      └── gui_handlers.py   # Event-Handler
main.py                   # Kommandozeilenbasierter Einstiegspunkt
start_maehrdocs.py        # Vereinfachter Start der GUI
maehrdocs.bat             # Windows-Batchdatei zum einfachen Starten
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
    # weitere Dokumenttypen...
```

## Beiträge

Beiträge sind willkommen! Bitte öffnen Sie ein Issue oder einen Pull Request.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.