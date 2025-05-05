# MaehrDocs Modulübersicht

Diese Dokumentation wurde automatisch generiert und bietet einen Überblick über alle Module im MaehrDocs Projekt.

## Inhaltsverzeichnis

### Module

### maehrdocs Module
- [maehrdocs.__init__](#maehrdocs-__init__) - MaehrDocs - Automatisches Dokumentenmanagementsystem
- [maehrdocs.config](#maehrdocs-config) - Konfigurationsverwaltung für MaehrDocs
- [maehrdocs.document_processor](#maehrdocs-document_processor) - DocumentProcessor für MaehrDocs
- [maehrdocs.duplicate_detector](#maehrdocs-duplicate_detector) - Keine Beschreibung verfügbar
- [maehrdocs.file_operations](#maehrdocs-file_operations) - Dateioperationen für MaehrDocs
- [maehrdocs.filename_generator](#maehrdocs-filename_generator) - Dateinamengenerator für MaehrDocs
- [maehrdocs.gui.__init__](#maehrdocs-gui-__init__) - GUI-Paket für MaehrDocs
- [maehrdocs.gui.generate_module_docs](#maehrdocs-gui-generate_module_docs) - MaehrDocs Modul-Dokumentations-Generator
- [maehrdocs.gui.gui_actions](#maehrdocs-gui-gui_actions) - Event-Handler und Aktionen für MaehrDocs
- [maehrdocs.gui.gui_alerts](#maehrdocs-gui-gui_alerts) - Keine Beschreibung verfügbar
- [maehrdocs.gui.gui_animations](#maehrdocs-gui-gui_animations) - Keine Beschreibung verfügbar
- [maehrdocs.gui.gui_buttons](#maehrdocs-gui-gui_buttons) - Button-Komponenten für MaehrDocs GUI
- [maehrdocs.gui.gui_cards](#maehrdocs-gui-gui_cards) - Karten- und Container-Komponenten für MaehrDocs GUI
- [maehrdocs.gui.gui_command_executor](#maehrdocs-gui-gui_command_executor) - Befehlsausführung für MaehrDocs
- [maehrdocs.gui.gui_core](#maehrdocs-gui-gui_core) - Kernmodul der GUI-Anwendung für MaehrDocs
- [maehrdocs.gui.gui_dashboard](#maehrdocs-gui-gui_dashboard) - Dashboard-Funktionalität für MaehrDocs
- [maehrdocs.gui.gui_dialog](#maehrdocs-gui-gui_dialog) - Keine Beschreibung verfügbar
- [maehrdocs.gui.gui_document_actions](#maehrdocs-gui-gui_document_actions) - Dokumentenaktionen für MaehrDocs
- [maehrdocs.gui.gui_document_comparison](#maehrdocs-gui-gui_document_comparison) - Dokumentenvergleich für MaehrDocs
- [maehrdocs.gui.gui_document_loader](#maehrdocs-gui-gui_document_loader) - Dokumentenloader für MaehrDocs
- [maehrdocs.gui.gui_document_viewer](#maehrdocs-gui-gui_document_viewer) - Dokumentenansicht für MaehrDocs
- [maehrdocs.gui.gui_drop_handlers](#maehrdocs-gui-gui_drop_handlers) - Drag & Drop Handler für MaehrDocs
- [maehrdocs.gui.gui_form_fields](#maehrdocs-gui-gui_form_fields) - Spezifische Formularfelder für MaehrDocs GUI
- [maehrdocs.gui.gui_forms](#maehrdocs-gui-gui_forms) - Zentrale Formularkomponenten für MaehrDocs GUI
- [maehrdocs.gui.gui_help](#maehrdocs-gui-gui_help) - Hilfefunktionen für MaehrDocs
- [maehrdocs.gui.gui_layout](#maehrdocs-gui-gui_layout) - Layout-Komponenten für MaehrDocs GUI
- [maehrdocs.gui.gui_logger](#maehrdocs-gui-gui_logger) - Logging-Funktionalität für MaehrDocs GUI
- [maehrdocs.gui.gui_notification_handlers](#maehrdocs-gui-gui_notification_handlers) - Benachrichtigungshandler für MaehrDocs
- [maehrdocs.gui.gui_notifications](#maehrdocs-gui-gui_notifications) - Dieses Modul dient als zentrale Schnittstelle für alle Benachrichtigungen und Dialoge
- [maehrdocs.gui.gui_settings](#maehrdocs-gui-gui_settings) - Einstellungsmodul für MaehrDocs (Kompatibilitätsschicht)
- [maehrdocs.gui.gui_settings_components](#maehrdocs-gui-gui_settings_components) - Einstellungskomponenten für MaehrDocs GUI
- [maehrdocs.gui.gui_settings_dialog](#maehrdocs-gui-gui_settings_dialog) - Einstellungsdialog für MaehrDocs
- [maehrdocs.gui.gui_toast](#maehrdocs-gui-gui_toast) - Keine Beschreibung verfügbar
- [maehrdocs.gui.gui_utils](#maehrdocs-gui-gui_utils) - Hilfsfunktionen für MaehrDocs GUI
- [maehrdocs.main](#maehrdocs-main) - Haupteinstiegspunkt für MaehrDocs
- [maehrdocs.openai_integration](#maehrdocs-openai_integration) - OpenAI-Integration für MaehrDocs
- [maehrdocs.start_maehrdocs](#maehrdocs-start_maehrdocs) - Starter-Skript für MaehrDocs
- [maehrdocs.text_extractor](#maehrdocs-text_extractor) - Textextraktion aus PDF-Dokumenten für MaehrDocs

## Module


## maehrdocs Module

### maehrdocs.__init__

**Dateipfad:** `maehrdocs\__init__.py`

MaehrDocs - Automatisches Dokumentenmanagementsystem
Modularisierte Version mit verbesserter Struktur

Dieses Paket enthält alle Komponenten für das MaehrDocs System:
- Konfigurationsverwaltung
- Dokumentenverarbeitung
- Duplikaterkennung
- Grafische Benutzeroberfläche

---

### maehrdocs.config

**Dateipfad:** `maehrdocs\config.py`

Konfigurationsverwaltung für MaehrDocs
Enthält die ConfigManager-Klasse zum Laden und Speichern der Konfiguration

#### Funktionen

- `__init__()` - Initialisiert den ConfigManager
- `get_config()` - Gibt die aktuelle Konfiguration zurück
- `load_config()` - Lädt die Konfiguration aus der YAML-Datei
- `save_config()` - Speichert die Konfiguration in die YAML-Datei
- `create_default_config()` - Erstellt eine Standardkonfiguration
- `_ensure_directories_exist()` - Stellt sicher, dass die angegebenen Verzeichnisse existieren

#### Klassen

- `ConfigManager` - Verwaltet die Konfiguration des MaehrDocs-Systems
  - Methoden:
    - `get_config()` - Gibt die aktuelle Konfiguration zurück
    - `load_config()` - Lädt die Konfiguration aus der YAML-Datei
    - `save_config()` - Speichert die Konfiguration in die YAML-Datei
    - `create_default_config()` - Erstellt eine Standardkonfiguration
    - `_ensure_directories_exist()` - Stellt sicher, dass die angegebenen Verzeichnisse existieren

---

### maehrdocs.document_processor

**Dateipfad:** `maehrdocs\document_processor.py`

DocumentProcessor für MaehrDocs
Hauptklasse zur Verarbeitung von Dokumenten

#### Funktionen

- `__init__()` - Initialisiert den DocumentProcessor mit der Konfiguration
- `process_document()` - Verarbeitet ein einzelnes Dokument

#### Klassen

- `DocumentProcessor` - Hauptklasse zur Verarbeitung von Dokumenten
  - Methoden:
    - `process_document()` - Verarbeitet ein einzelnes Dokument

---

### maehrdocs.duplicate_detector

**Dateipfad:** `maehrdocs\duplicate_detector.py`

#### Funktionen

- `__init__()` - Keine Beschreibung verfügbar
- `calculate_similarity()` - Berechnet die Textähnlichkeit zwischen zwei Dokumenten
- `_tokenize()` - Text in Wörter aufteilen und bereinigen

#### Klassen

- `DuplicateDetector` - Keine Beschreibung verfügbar
  - Methoden:
    - `calculate_similarity()` - Berechnet die Textähnlichkeit zwischen zwei Dokumenten
    - `_tokenize()` - Text in Wörter aufteilen und bereinigen

---

### maehrdocs.file_operations

**Dateipfad:** `maehrdocs\file_operations.py`

Dateioperationen für MaehrDocs
Verwaltet alle Dateioperationen wie Verschieben, Kopieren und Löschen von Dateien

#### Funktionen

- `__init__()` - Initialisiert die Dateioperationen
- `_ensure_directories_exist()` - Stellt sicher, dass alle erforderlichen Verzeichnisse existieren
- `move_to_output()` - Verschiebt eine Datei in den Ausgabeordner mit neuem Namen
- `move_to_trash()` - Verschiebt eine Datei in den Papierkorb
- `get_input_files()` - Gibt eine Liste aller Dateien mit der angegebenen Endung im Eingangsordner zurück
- `get_output_files()` - Gibt eine Liste aller Dateien mit der angegebenen Endung im Ausgabeordner zurück
- `create_backup()` - Erstellt eine Sicherungskopie einer Datei

#### Klassen

- `FileOperations` - Klasse zur Verwaltung von Dateioperationen
  - Methoden:
    - `_ensure_directories_exist()` - Stellt sicher, dass alle erforderlichen Verzeichnisse existieren
    - `move_to_output()` - Verschiebt eine Datei in den Ausgabeordner mit neuem Namen
    - `move_to_trash()` - Verschiebt eine Datei in den Papierkorb
    - `get_input_files()` - Gibt eine Liste aller Dateien mit der angegebenen Endung im Eingangsordner zurück
    - `get_output_files()` - Gibt eine Liste aller Dateien mit der angegebenen Endung im Ausgabeordner zurück
    - `create_backup()` - Erstellt eine Sicherungskopie einer Datei

---

### maehrdocs.filename_generator

**Dateipfad:** `maehrdocs\filename_generator.py`

Dateinamengenerator für MaehrDocs
Generiert standardisierte Dateinamen basierend auf extrahierten Dokumentinformationen

#### Funktionen

- `__init__()` - Initialisiert den FilenameGenerator
- `generate_filename()` - Generiert einen standardisierten Dateinamen basierend auf den extrahierten Informationen
- `_format_date()` - Formatiert ein Datum im Format YYYY-MM-DD
- `_format_document_type()` - Formatiert den Dokumenttyp
- `_format_sender()` - Formatiert den Absender
- `_format_subject()` - Formatiert den Betreff

#### Klassen

- `FilenameGenerator` - Klasse zur Generierung standardisierter Dateinamen
  - Methoden:
    - `generate_filename()` - Generiert einen standardisierten Dateinamen basierend auf den extrahierten Informationen
    - `_format_date()` - Formatiert ein Datum im Format YYYY-MM-DD
    - `_format_document_type()` - Formatiert den Dokumenttyp
    - `_format_sender()` - Formatiert den Absender
    - `_format_subject()` - Formatiert den Betreff

---

### maehrdocs.gui.__init__

**Dateipfad:** `maehrdocs\gui\__init__.py`

GUI-Paket für MaehrDocs
Enthält alle GUI-bezogenen Komponenten und Funktionalitäten

---

### maehrdocs.gui.generate_module_docs

**Dateipfad:** `maehrdocs\gui\generate_module_docs.py`

MaehrDocs Modul-Dokumentations-Generator

Durchsucht alle Python-Dateien im MaehrDocs-Paket und erstellt eine Markdown-Dokumentation 
der Modulstruktur mit Funktionen und Klassen.

#### Funktionen

- `get_docstring()` - Extrahiert den Docstring aus einem AST-Knoten.
- `analyze_python_file()` - Analysiert eine Python-Datei und extrahiert Funktionen, Klassen und deren Docstrings.
- `generate_markdown()` - Generiert eine Markdown-Dokumentation der Module und deren Inhalte.
- `generate_module_markdown()` - Generiert den Markdown-Abschnitt für ein bestimmtes Modul.

---

### maehrdocs.gui.gui_actions

**Dateipfad:** `maehrdocs\gui\gui_actions.py`

Event-Handler und Aktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Benutzeraktionen und Ereignissen

---

### maehrdocs.gui.gui_alerts

**Dateipfad:** `maehrdocs\gui\gui_alerts.py`

#### Funktionen

- `show_success()` - Zeigt eine Erfolgs-Benachrichtigung an
- `show_info()` - Zeigt eine Info-Benachrichtigung an
- `show_warning()` - Zeigt eine Warnungs-Benachrichtigung an
- `show_error()` - Zeigt eine Fehler-Benachrichtigung an

---

### maehrdocs.gui.gui_animations

**Dateipfad:** `maehrdocs\gui\gui_animations.py`

#### Funktionen

- `animate_window()` - Animiert das Erscheinen eines Fensters mit Fade-In-Effekt
- `fade_in()` - Führt einen Fade-In-Effekt für ein Fenster durch
- `fade_out()` - Führt einen Fade-Out-Effekt für ein Fenster durch

---

### maehrdocs.gui.gui_buttons

**Dateipfad:** `maehrdocs\gui\gui_buttons.py`

Button-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen verschiedener Arten von Buttons

#### Funktionen

- `create_button()` - Erstellt einen styled Button
- `create_icon_button()` - Erstellt einen Button mit Icon
- `create_toggle_button()` - Erstellt einen Toggle-Button, der zwischen zwei Zuständen wechseln kann
- `_toggle_button_state()` - Hilfsfunktion zum Umschalten des Button-Zustands
- `_create_tooltip()` - Erstellt einen einfachen Tooltip für ein Widget
- `enter()` - Keine Beschreibung verfügbar
- `leave()` - Keine Beschreibung verfügbar

---

### maehrdocs.gui.gui_cards

**Dateipfad:** `maehrdocs\gui\gui_cards.py`

Karten- und Container-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen von Statuskarten und anderen Container-Elementen

#### Funktionen

- `create_status_card()` - Erstellt eine Statuskarte für einen Ordner
- `create_info_card()` - Erstellt eine Informationskarte
- `create_activity_card()` - Erstellt eine Aktivitätskarte mit einem Textfeld für Updates
- `create_section_frame()` - Erstellt einen Abschnittsrahmen mit optionalem Titel

---

### maehrdocs.gui.gui_command_executor

**Dateipfad:** `maehrdocs\gui\gui_command_executor.py`

Befehlsausführung für MaehrDocs
Enthält Funktionen zur Ausführung von Befehlen in separaten Threads

#### Funktionen

- `run_command_in_thread()` - Führt einen Befehl in einem separaten Thread aus
- `_run_command()` - Führt den eigentlichen Befehl aus und aktualisiert das Protokoll

---

### maehrdocs.gui.gui_core

**Dateipfad:** `maehrdocs\gui\gui_core.py`

Kernmodul der GUI-Anwendung für MaehrDocs
Enthält die Hauptklasse GuiApp, die alle anderen GUI-Komponenten koordiniert

#### Funktionen

- `__init__()` - Initialisiert die GUI mit Konfiguration und Dokumentenprozessor
- `setup_gui()` - Richtet die GUI ein und gibt das Root-Fenster zurück
- `open_folder()` - Öffnet den angegebenen Ordner im Datei-Explorer
- `browse_folder()` - Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld
- `log()` - Fügt eine Nachricht zum Protokollbereich hinzu

#### Klassen

- `GuiApp` - Hauptklasse für die MaehrDocs GUI-Anwendung
  - Methoden:
    - `setup_gui()` - Richtet die GUI ein und gibt das Root-Fenster zurück
    - `open_folder()` - Öffnet den angegebenen Ordner im Datei-Explorer
    - `browse_folder()` - Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld
    - `log()` - Fügt eine Nachricht zum Protokollbereich hinzu

---

### maehrdocs.gui.gui_dashboard

**Dateipfad:** `maehrdocs\gui\gui_dashboard.py`

Dashboard-Funktionalität für MaehrDocs
Erstellt das Dashboard mit Statuskarten und Aktivitätsanzeige

#### Funktionen

- `create_dashboard()` - Erstellt das Dashboard mit Statusanzeigen

---

### maehrdocs.gui.gui_dialog

**Dateipfad:** `maehrdocs\gui\gui_dialog.py`

#### Funktionen

- `show_confirm_dialog()` - Zeigt einen Bestätigungsdialog an
- `show_info_dialog()` - Zeigt einen Informationsdialog an
- `show_error_dialog()` - Zeigt einen Fehlerdialog an
- `show_warning_dialog()` - Zeigt einen Warnungsdialog an

---

### maehrdocs.gui.gui_document_actions

**Dateipfad:** `maehrdocs\gui\gui_document_actions.py`

Dokumentenaktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Dokumenten

#### Funktionen

- `process_documents()` - Verarbeitet alle Dokumente im Eingangsordner
- `simulate_processing()` - Führt eine Simulation (Dry-Run) durch
- `process_single_file()` - Verarbeitet eine einzelne vom Benutzer ausgewählte Datei
- `rebuild_config()` - Setzt die Konfiguration zurück

---

### maehrdocs.gui.gui_document_comparison

**Dateipfad:** `maehrdocs\gui\gui_document_comparison.py`

Dokumentenvergleich für MaehrDocs
Enthält Funktionen zum Vergleichen von PDF-Dokumenten

#### Funktionen

- `compare_documents()` - Öffnet ein Fenster zum visuellen Vergleich zweier Dokumente
- `create_document_panel()` - Erstellt ein Panel für die Anzeige eines Dokuments
- `load_and_compare_contents()` - Lädt den Inhalt der Dokumente und hebt Unterschiede hervor
- `highlight_differences()` - Hebt Unterschiede zwischen zwei Textfenstern hervor

---

### maehrdocs.gui.gui_document_loader

**Dateipfad:** `maehrdocs\gui\gui_document_loader.py`

Dokumentenloader für MaehrDocs
Enthält Funktionen zum Laden und Extrahieren von Dokumentinhalten

#### Funktionen

- `load_document_content()` - Lädt den Inhalt eines Dokuments in ein Text-Widget
- `get_document_metadata()` - Extrahiert Metadaten aus einem PDF-Dokument
- `extract_document_text()` - Extrahiert Text aus einem PDF-Dokument
- `get_document_preview()` - Lädt eine Vorschau des Dokumentinhalts in ein Text-Widget

---

### maehrdocs.gui.gui_document_viewer

**Dateipfad:** `maehrdocs\gui\gui_document_viewer.py`

Dokumentenansicht für MaehrDocs
Enthält grundlegende Funktionen zum Anzeigen von Dokumenten

#### Funktionen

- `open_document()` - Öffnet ein Dokument mit dem Standardprogramm
- `get_full_document_path()` - Bestimmt den vollständigen Pfad zu einem Dokument
- `show_document_info()` - Zeigt Informationen über ein Dokument an

---

### maehrdocs.gui.gui_drop_handlers

**Dateipfad:** `maehrdocs\gui\gui_drop_handlers.py`

Drag & Drop Handler für MaehrDocs
Enthält Funktionen zum Verarbeiten von Drag & Drop Ereignissen

#### Funktionen

- `handle_drop()` - Verarbeitet gedropte Dateien
- `copy_files_to_inbox()` - Kopiert Dateien in den Eingangsordner
- `copy_thread()` - Keine Beschreibung verfügbar

---

### maehrdocs.gui.gui_form_fields

**Dateipfad:** `maehrdocs\gui\gui_form_fields.py`

Spezifische Formularfelder für MaehrDocs GUI
Enthält die verschiedenen Formularfelder und deren Erstellung

#### Funktionen

- `create_text_field()` - Erstellt ein Textfeld
- `create_folder_field()` - Erstellt ein Feld für die Ordnerauswahl mit Durchsuchen-Button
- `create_dropdown_field()` - Erstellt ein Dropdown-Feld
- `create_spinbox_field()` - Erstellt ein Spinbox-Feld
- `create_scale_field()` - Erstellt ein Schieberegler-Feld
- `create_checkbox_field()` - Erstellt ein Checkbox-Feld

---

### maehrdocs.gui.gui_forms

**Dateipfad:** `maehrdocs\gui\gui_forms.py`

Zentrale Formularkomponenten für MaehrDocs GUI
Koordiniert die verschiedenen Formularelemente und -funktionen

#### Funktionen

- `create_form_field()` - Erstellt ein einzelnes Formularfeld basierend auf der Konfiguration
- `_get_config_value()` - Holt einen Wert aus der Konfiguration

---

### maehrdocs.gui.gui_help

**Dateipfad:** `maehrdocs\gui\gui_help.py`

Hilfefunktionen für MaehrDocs
Enthält Funktionen für die Anzeige von Hilfetexten und -informationen

#### Funktionen

- `show_help()` - Zeigt ein Hilfefenster an
- `get_overview_help()` - Liefert den Hilfetext für den Überblick
- `get_features_help()` - Liefert den Hilfetext für die Funktionen
- `get_tutorial_help()` - Liefert den Hilfetext für die Anleitung
- `get_troubleshooting_help()` - Liefert den Hilfetext für die Fehlerbehebung
- `change_tab()` - Keine Beschreibung verfügbar

---

### maehrdocs.gui.gui_layout

**Dateipfad:** `maehrdocs\gui\gui_layout.py`

Layout-Komponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen der Hauptlayout-Komponenten

#### Funktionen

- `create_header()` - Erstellt den Kopfbereich der GUI
- `create_control_panel()` - Erstellt das Steuerungspanel
- `create_log_panel()` - Erstellt den Protokollbereich
- `create_status_bar()` - Erstellt die Statusleiste am unteren Rand

---

### maehrdocs.gui.gui_logger

**Dateipfad:** `maehrdocs\gui\gui_logger.py`

Logging-Funktionalität für MaehrDocs GUI
Enthält Funktionen zum Protokollieren von Nachrichten

#### Funktionen

- `setup_logging()` - Richtet die Tags für das Logging ein
- `log_message()` - Fügt eine Nachricht zum Protokollbereich hinzu
- `update_activity_display()` - Aktualisiert die Aktivitätsanzeige mit der neuesten Nachricht
- `export_log()` - Exportiert das aktuelle Protokoll in eine Datei

---

### maehrdocs.gui.gui_notification_handlers

**Dateipfad:** `maehrdocs\gui\gui_notification_handlers.py`

Benachrichtigungshandler für MaehrDocs
Enthält Funktionen zur Verarbeitung von speziellen Benachrichtigungen

#### Funktionen

- `handle_duplicate_from_log()` - Verarbeitet Duplikatbenachrichtigungen aus der Protokollausgabe

---

### maehrdocs.gui.gui_notifications

**Dateipfad:** `maehrdocs\gui\gui_notifications.py`

Dieses Modul dient als zentrale Schnittstelle für alle Benachrichtigungen und Dialoge
in der MaehrDocs Anwendung. Es stellt verschiedene Funktionen zur Verfügung,
um Benachrichtigungen und Dialoge anzuzeigen.

Die eigentliche Implementierung dieser Funktionen wurde in separate Module ausgelagert:
- notifications.py: Benachrichtigungsfenster
- animations.py: Animationseffekte
- toast.py: Toast-Nachrichten
- dialog.py: Standard-Dialoge

#### Funktionen

- `show_success()` - Zeigt eine Erfolgs-Benachrichtigung an
- `show_info()` - Zeigt eine Info-Benachrichtigung an
- `show_warning()` - Zeigt eine Warnungs-Benachrichtigung an
- `show_error()` - Zeigt eine Fehler-Benachrichtigung an
- `show_success_toast()` - Zeigt einen Erfolgs-Toast an
- `confirm()` - Zeigt einen Bestätigungsdialog an und gibt das Ergebnis zurück
- `info()` - Zeigt einen Informationsdialog an
- `error()` - Zeigt einen Fehlerdialog an
- `warning()` - Zeigt einen Warnungsdialog an

---

### maehrdocs.gui.gui_settings

**Dateipfad:** `maehrdocs\gui\gui_settings.py`

Einstellungsmodul für MaehrDocs (Kompatibilitätsschicht)
Dieses Modul importiert die Funktionen aus den neuen aufgeteilten Modulen
für die Abwärtskompatibilität.

---

### maehrdocs.gui.gui_settings_components

**Dateipfad:** `maehrdocs\gui\gui_settings_components.py`

Einstellungskomponenten für MaehrDocs GUI
Enthält Funktionen zum Erstellen von Einstellungssektionen und -tabs

#### Funktionen

- `create_settings_section()` - Erstellt einen Abschnitt in den Einstellungen
- `create_settings_tab()` - Erstellt einen Tab in den Einstellungen
- `collect_settings_from_widget()` - Sammelt rekursiv alle Einstellungen aus Widgets
- `search_and_update_field()` - Durchsucht ein Widget nach einem Feld und aktualisiert dessen Wert

---

### maehrdocs.gui.gui_settings_dialog

**Dateipfad:** `maehrdocs\gui\gui_settings_dialog.py`

Einstellungsdialog für MaehrDocs
Erstellt ein Fenster zur Konfiguration der Anwendung

#### Funktionen

- `open_settings()` - Öffnet das Einstellungsfenster
- `create_general_tab()` - Erstellt den Tab für allgemeine Einstellungen
- `create_openai_tab()` - Erstellt den Tab für OpenAI-Einstellungen
- `create_document_tab()` - Erstellt den Tab für Dokumentverarbeitungseinstellungen
- `create_notifications_tab()` - Erstellt den Tab für Benachrichtigungseinstellungen
- `save_settings()` - Speichert die Einstellungen aus dem Einstellungsfenster
- `browse_folder()` - Öffnet einen Dialog zur Ordnerauswahl für ein Einstellungsfeld

---

### maehrdocs.gui.gui_toast

**Dateipfad:** `maehrdocs\gui\gui_toast.py`

#### Funktionen

- `show_toast()` - Zeigt einen Toast an und gibt das Fenster zurück
- `__init__()` - Erstellt eine neue Toast-Benachrichtigung
- `show()` - Zeigt den Toast an

#### Klassen

- `Toast` - Eine Toast-Benachrichtigung, die kurzzeitig am unteren Bildschirmrand erscheint
  - Methoden:
    - `show()` - Zeigt den Toast an

---

### maehrdocs.gui.gui_utils

**Dateipfad:** `maehrdocs\gui\gui_utils.py`

Hilfsfunktionen für MaehrDocs GUI
Enthält verschiedene Hilfsfunktionen für die GUI

#### Funktionen

- `update_dashboard()` - Aktualisiert die Anzeigen im Dashboard
- `open_folder_in_explorer()` - Öffnet den angegebenen Ordner im Datei-Explorer
- `setup_drag_drop()` - Richtet Drag & Drop-Funktionalität ein (erfordert tkinterdnd2)
- `clear_log()` - Löscht den Inhalt des Protokolls
- `check_for_new_documents()` - Prüft periodisch, ob neue Dokumente im Eingangsordner liegen
- `create_directory_structure()` - Erstellt die Verzeichnisstruktur für die Anwendung
- `get_file_count()` - Zählt die Anzahl der Dateien mit der angegebenen Endung im Verzeichnis
- `format_timestamp()` - Erstellt einen formatierten Zeitstempel
- `is_valid_path()` - Prüft, ob der angegebene Pfad gültig ist

---

### maehrdocs.main

**Dateipfad:** `maehrdocs\main.py`

Haupteinstiegspunkt für MaehrDocs
Enthält die Kommandozeilenargumente und die CLI-Logik

#### Funktionen

- `parse_arguments()` - Parst die Kommandozeilenargumente
- `setup_logging()` - Richtet das Logging basierend auf der Ausführlichkeitsstufe ein
- `main()` - Hauptfunktion des Programms

---

### maehrdocs.openai_integration

**Dateipfad:** `maehrdocs\openai_integration.py`

OpenAI-Integration für MaehrDocs
Verwaltet die Interaktion mit der OpenAI API

#### Funktionen

- `__init__()` - Initialisiert die OpenAI-Integration
- `analyze_document()` - Analysiert einen Dokumenttext mit der OpenAI API
- `_create_analysis_prompt()` - Erstellt den Prompt für die Dokumentanalyse
- `_call_openai_api()` - Ruft die OpenAI API auf
- `_parse_json_response()` - Parst die JSON-Antwort der API

#### Klassen

- `OpenAIIntegration` - Klasse zur Interaktion mit der OpenAI API
  - Methoden:
    - `analyze_document()` - Analysiert einen Dokumenttext mit der OpenAI API
    - `_create_analysis_prompt()` - Erstellt den Prompt für die Dokumentanalyse
    - `_call_openai_api()` - Ruft die OpenAI API auf
    - `_parse_json_response()` - Parst die JSON-Antwort der API

---

### maehrdocs.start_maehrdocs

**Dateipfad:** `maehrdocs\start_maehrdocs.py`

Starter-Skript für MaehrDocs
Startet die GUI der Anwendung

#### Funktionen

- `main()` - Hauptfunktion zum Starten der GUI

---

### maehrdocs.text_extractor

**Dateipfad:** `maehrdocs\text_extractor.py`

Textextraktion aus PDF-Dokumenten für MaehrDocs

#### Funktionen

- `__init__()` - Initialisiert den TextExtractor
- `extract_text_from_pdf()` - Extrahiert Text aus einer PDF-Datei
- `get_pdf_metadata()` - Extrahiert Metadaten aus einer PDF-Datei
- `is_valid_pdf()` - Prüft, ob eine Datei eine gültige PDF ist und die Größenbeschränkung einhält

#### Klassen

- `TextExtractor` - Klasse zur Extraktion von Text aus PDF-Dokumenten
  - Methoden:
    - `extract_text_from_pdf()` - Extrahiert Text aus einer PDF-Datei
    - `get_pdf_metadata()` - Extrahiert Metadaten aus einer PDF-Datei
    - `is_valid_pdf()` - Prüft, ob eine Datei eine gültige PDF ist und die Größenbeschränkung einhält

---

