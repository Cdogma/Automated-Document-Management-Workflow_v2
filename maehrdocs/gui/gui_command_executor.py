"""
Befehlsausführung für MaehrDocs
Enthält Funktionen zur Ausführung von Befehlen in separaten Threads
"""

import subprocess
import threading
from tkinter import messagebox
from datetime import datetime

def run_command_in_thread(app, command, env=None):
    """
    Führt einen Befehl in einem separaten Thread aus
    
    Args:
        app: Instanz der GuiApp
        command: Liste mit Befehlszeile und Argumenten
        env: Optionale Umgebungsvariablen für den Prozess
    """
    # Status aktualisieren
    app.status_label.config(text="Verarbeitung läuft...")
    
    # Log protokollieren
    app.log(f"Führe Befehl aus: {' '.join(command)}")
    
    # Thread starten
    thread = threading.Thread(target=_run_command, args=(app, command, env))
    thread.daemon = True
    thread.start()

def _run_command(app, command, env=None):
    """
    Führt den eigentlichen Befehl aus und aktualisiert das Protokoll
    
    Args:
        app: Instanz der GuiApp
        command: Liste mit Befehlszeile und Argumenten
        env: Optionale Umgebungsvariablen für den Prozess
    """
    try:
        # Prozess starten und Ausgabe erfassen
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env  # Umgebungsvariablen hinzufügen
        )
        
        # Ausgabe in Echtzeit verarbeiten
        for line in process.stdout:
            line = line.strip()
            
            # Auf spezielle Duplikatmarkierung prüfen
            if "DUPLIKAT_ERKANNT|" in line:
                # Duplikatinformationen extrahieren
                parts = line.split("|")
                if len(parts) >= 4:
                    original_file = parts[1]
                    duplicate_file = parts[2]
                    similarity = parts[3]
                    
                    # Blau formatierte Duplikatmeldung
                    duplikat_message = f"Duplikat erkannt: {duplicate_file} ist identisch mit {original_file} (Ähnlichkeit: {similarity})"
                    
                    # In das Log schreiben
                    app.log(duplikat_message, level="duplicate")
            else:
                # Normale Ausgabe
                app.log(line)
            
        # Auf Fehler prüfen
        for line in process.stderr:
            app.log(line.strip(), level="error")
            
        # Auf Prozessende warten
        process.wait()
        
        # Ergebnis anzeigen
        if process.returncode == 0:
            app.log("Verarbeitung erfolgreich abgeschlossen.", level="success")
            app.status_label.config(text="Bereit")
            
            # Dashboard aktualisieren - Verwende die Methode aus gui_utils
            from .gui_utils import update_dashboard
            app.root.after(1000, lambda: update_dashboard(app))
            
            # Benachrichtigung anzeigen wenn aktiviert
            if app.config.get("gui", {}).get("notify_on_completion", True):
                messagebox.showinfo(
                    "Verarbeitung abgeschlossen", 
                    "Die Dokumentenverarbeitung wurde erfolgreich abgeschlossen."
                )
        else:
            app.log(f"Verarbeitung mit Fehlercode {process.returncode} beendet.", level="error")
            app.status_label.config(text="Fehler aufgetreten")
            
    except Exception as e:
        app.log(f"Fehler bei der Ausführung: {str(e)}", level="error")
        app.status_label.config(text="Fehler aufgetreten")