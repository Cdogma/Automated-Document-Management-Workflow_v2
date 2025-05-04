"""
Hilfefunktionen für MaehrDocs
Enthält Funktionen für die Anzeige von Hilfetexten und -informationen
"""

import tkinter as tk
from tkinter import scrolledtext

from .gui_buttons import create_button

def show_help(app):
    """
    Zeigt ein Hilfefenster an
    
    Args:
        app: Instanz der GuiApp
    """
    help_window = tk.Toplevel(app.root)
    help_window.title("MaehrDocs - Hilfe")
    help_window.geometry("800x600")
    help_window.configure(bg=app.colors["background_dark"])
    
    help_frame = tk.Frame(
        help_window, 
        bg=app.colors["background_medium"], 
        padx=20, 
        pady=20
    )
    help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Überschrift
    header = tk.Label(
        help_frame, 
        text="Hilfe und Dokumentation", 
        font=app.fonts["header"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    header.pack(anchor=tk.W, pady=(0, 20))
    
    # Tabs für verschiedene Hilfethemen
    tab_frame = tk.Frame(help_frame, bg=app.colors["background_medium"])
    tab_frame.pack(fill=tk.X, pady=10)
    
    tabs = {
        "Überblick": get_overview_help,
        "Funktionen": get_features_help,
        "Anleitung": get_tutorial_help,
        "Fehlerbehebung": get_troubleshooting_help
    }
    
    # Aktiver Tab
    active_tab = tk.StringVar(value="Überblick")
    
    # Hilfetext
    help_text = scrolledtext.ScrolledText(
        help_frame, 
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"],
        padx=15,
        pady=15
    )
    help_text.pack(fill=tk.BOTH, expand=True)
    
    # Tab-Buttons erstellen
    for tab_name in tabs:
        tab_btn = create_button(
            app,
            tab_frame, 
            tab_name, 
            lambda name=tab_name: change_tab(name),
            bg=app.colors["primary"] if tab_name == active_tab.get() else app.colors["background_dark"]
        )
        tab_btn.pack(side=tk.LEFT, padx=5)
    
    # Funktion zum Wechseln der Tabs
    def change_tab(tab_name):
        active_tab.set(tab_name)
        
        # Tabs aktualisieren
        for i, child in enumerate(tab_frame.winfo_children()):
            if isinstance(child, tk.Button):
                tab_text = list(tabs.keys())[i]
                if tab_text == tab_name:
                    child.config(bg=app.colors["primary"])
                else:
                    child.config(bg=app.colors["background_dark"])
        
        # Hilfetext aktualisieren
        help_text.config(state=tk.NORMAL)
        help_text.delete(1.0, tk.END)
        
        # Hilfetextfunktion abrufen und ausführen
        help_function = tabs[tab_name]
        help_content = help_function()
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    # Initial den Text für den aktiven Tab anzeigen
    initial_content = get_overview_help()
    help_text.insert(tk.END, initial_content)
    help_text.config(state=tk.DISABLED)
    
    # Button zum Schließen
    close_btn = create_button(
        app,
        help_frame, 
        "Schließen", 
        help_window.destroy
    )
    close_btn.pack(anchor=tk.E, pady=10)
    
    return help_window

def get_overview_help():
    """
    Liefert den Hilfetext für den Überblick
    
    Returns:
        str: Hilfetext
    """
    return """
# MaehrDocs - Benutzerhandbuch

## Überblick

MaehrDocs ist ein intelligentes Dokumentenmanagementsystem, das mit Hilfe von KI PDF-Dokumente automatisch analysiert, 
kategorisiert und umbenennt. Die Anwendung wurde entwickelt, um den Prozess der Dokumentenverwaltung zu vereinfachen
und zu automatisieren.

## Hauptfunktionen

1. **Automatische Verarbeitung** - PDFs werden aus dem Eingangsordner gelesen, analysiert und umbenannt
2. **KI-Analyse** - Verwendet OpenAI, um Dokumenttyp, Absender, Datum und andere Informationen zu extrahieren
3. **Duplikaterkennung** - Vermeidet doppelte Dokumente durch intelligente Ähnlichkeitserkennung
4. **Übersichtliches Dashboard** - Zeigt den Status aller Ordner und die letzten Aktivitäten an

## Ordnerstruktur

Die Anwendung verwendet standardmäßig die folgende Ordnerstruktur:

- Eingangsordner: Hier werden die zu verarbeitenden PDF-Dokumente abgelegt
- Ausgabeordner: Hier werden die verarbeiteten Dokumente mit neuem Namen gespeichert
- Problemordner: Hier werden Dokumente gespeichert, die nicht verarbeitet werden konnten oder als Duplikate erkannt wurden
"""

def get_features_help():
    """
    Liefert den Hilfetext für die Funktionen
    
    Returns:
        str: Hilfetext
    """
    return """
# Funktionen

## Dashboard

Das Dashboard bietet einen Überblick über den aktuellen Status Ihrer Dokumente:

- **Eingang**: Zeigt die Anzahl der Dokumente im Eingangsordner an
- **Verarbeitet**: Zeigt die Anzahl der bereits verarbeiteten Dokumente an
- **Probleme**: Zeigt die Anzahl der Dokumente im Problemordner an

## Dokumentenverarbeitung

Die Anwendung bietet verschiedene Methoden zur Verarbeitung von Dokumenten:

- **Alle verarbeiten**: Verarbeitet alle Dokumente im Eingangsordner
- **Simulation**: Führt eine Testverarbeitung durch, ohne Änderungen vorzunehmen
- **Einzelne Datei verarbeiten**: Ermöglicht die Verarbeitung einer einzelnen Datei

## Duplikaterkennung

Das System erkennt Duplikate durch:

- Berechnung des Datei-Hashs
- Textähnlichkeitsanalyse mit anpassbarem Schwellenwert
- Vergleich von Metadaten

Bei erkannten Duplikaten erscheint ein Hinweis im Protokoll und ein Popup-Dialog mit Details.

## Protokoll

Das Protokoll zeigt alle Aktionen und Ereignisse der Anwendung an:

- Erfolgreiche Verarbeitungen
- Fehler und Warnungen
- Erkannte Duplikate
"""

def get_tutorial_help():
    """
    Liefert den Hilfetext für die Anleitung
    
    Returns:
        str: Hilfetext
    """
    return """
# Anleitung

## Schnellstart

1. Legen Sie PDF-Dokumente im Eingangsordner ab
2. Klicken Sie auf "Alle Dokumente verarbeiten"
3. Die verarbeiteten Dokumente finden Sie im Ausgabeordner

## Detaillierte Anleitung

### Neue Dokumente verarbeiten

Klicken Sie auf "Alle Dokumente verarbeiten", um alle PDFs im Eingangsordner zu verarbeiten. 
Alternativ können Sie "Simulation (Dry-Run)" wählen, um die Verarbeitung zu testen, ohne Änderungen vorzunehmen.

### Einzelne Datei verarbeiten

Klicken Sie auf "Einzelne Datei verarbeiten" und wählen Sie eine PDF-Datei aus, um nur diese zu verarbeiten.

### Konfiguration anpassen

Klicken Sie auf "Einstellungen", um die Konfiguration anzupassen, z.B.:
- Verzeichnispfade
- OpenAI-Modell und Parameter
- Schwellenwert für Duplikaterkennung
- Gültige Dokumenttypen

### Drag & Drop

Sie können Dateien auch direkt per Drag & Drop in die Anwendung ziehen, um sie zu verarbeiten.
Beachten Sie, dass diese Funktion die Installation von tkinterdnd2 erfordert.
"""

def get_troubleshooting_help():
    """
    Liefert den Hilfetext für die Fehlerbehebung
    
    Returns:
        str: Hilfetext
    """
    return """
# Fehlerbehebung

## Häufige Probleme

### Fehler bei der Textextraktion

**Problem**: Die Anwendung kann keinen Text aus einer PDF extrahieren.

**Lösung**: 
- Prüfen Sie, ob die PDF beschädigt oder passwortgeschützt ist
- Stellen Sie sicher, dass die PDF Textinhalt hat (keine gescannte Bilder ohne OCR)
- Versuchen Sie, die PDF mit einem anderen Programm zu öffnen und zu speichern

### OpenAI-API-Fehler

**Problem**: Die Anwendung kann keine Verbindung zur OpenAI-API herstellen.

**Lösung**:
- Überprüfen Sie Ihre Internetverbindung
- Stellen Sie sicher, dass der API-Schlüssel in der .env-Datei korrekt ist
- Prüfen Sie, ob Ihr API-Schlüssel noch gültig ist
- Erhöhen Sie die Anzahl der Wiederholungsversuche in den Einstellungen

### Dokument wird nicht erkannt

**Problem**: Die Anwendung kann den Dokumenttyp nicht korrekt erkennen.

**Lösung**:
- Passen Sie die gültigen Dokumenttypen in den Einstellungen an
- Stellen Sie sicher, dass der Dokumenttyp im Text eindeutig erkennbar ist
- Probieren Sie ein anderes OpenAI-Modell (z.B. GPT-4o statt GPT-3.5-Turbo)

## Tipps & Tricks

- Verwenden Sie Drag & Drop, um Dateien direkt in die Anwendung zu ziehen
- Halten Sie Ihren Eingangsordner aufgeräumt für bessere Übersicht
- Überprüfen Sie regelmäßig den Problemordner auf nicht verarbeitete Dokumente
- Nutzen Sie die Simulationsfunktion, um die Verarbeitung zu testen, bevor Sie Änderungen vornehmen

Bei weiteren Fragen wenden Sie sich an support@maehrdocs.de
"""