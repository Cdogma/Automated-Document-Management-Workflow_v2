# MaehrDocs - Intelligente Dokumentenverwaltung

Ein Python-basiertes System zur automatischen Verarbeitung und Verwaltung von PDF-Dokumenten mit Hilfe von KI.

## Funktionen

- Automatische Analyse von PDF-Dokumenten mit OpenAI
- Extrahierung relevanter Informationen wie Absender, Datum, Dokumenttyp
- Einheitliche Umbenennung nach standardisiertem Schema
- Erkennung von Duplikaten mittels Textähnlichkeitsanalyse
- Moderne, benutzerfreundliche GUI mit Dark Mode
- Drag & Drop Funktionalität (optional, wenn tkinterdnd2 installiert ist)

## Struktur

Das Projekt ist modular aufgebaut:

- `maehrdocs/` - Hauptpaket mit allen Modulen
  - `config.py` - Verwaltung der Konfiguration
  - `document_processor.py` - Dokumentverarbeitung
  - `duplicate_detector.py` - Duplikaterkennung
  - `gui_manager.py` - GUI-Verwaltung
- `main.py` - Kommandozeilenbasierter Einstiegspunkt
- `start_maehrdocs.py` - Vereinfachter Start der GUI
- `maehrdocs.bat` - Windows-Batchdatei zum einfachen Starten

## Installation

Benötigte Pakete:

```bash
pip install pymupdf python-dotenv openai pyyaml pillow