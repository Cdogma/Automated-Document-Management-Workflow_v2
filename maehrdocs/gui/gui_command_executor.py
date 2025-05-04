"""
Befehlsausführung für MaehrDocs
Enthält Funktionen zur Ausführung von Befehlen in separaten Threads
"""

import subprocess
import threading
from tkinter import messagebox

def run_command_in_thread(app, command):
    """
    Führt einen Befehl in einem separaten Thread aus
    
    Args:
        app: Instanz der GuiApp
        command: Liste mit Befehlszeile und Argumenten
    """
    # Status aktualisieren
    app.status_label.config(text="Verarbeitung läuft...")
    
    # Log protokollieren
    app.log(f"Führe Befehl aus: {' '.join(command)}")
    
    # Thread starten
    thread = threading.Thread(target=_run_command, args=(app, command))
    thread.daemon = True
    thread.start()

def _run_command(app, command):
    """
    Führt den eigentlichen Befehl aus und aktualisiert das Protokoll
    
    Args:
        app: Instanz der GuiApp
        command: Liste mit Befehlszeile und Argumenten
    """
    try:
        # Prozess starten und Ausgabe erfassen
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Ausgabe in Echtzeit verarbeiten
        for line in process.stdout:
            app.log(line.strip())
            
            # Auf Duplikate prüfen
            if "DUPLICATE DETECTED" in line:
                from .gui_notification_handlers import handle_duplicate_from_log
                handle_duplicate_from_log(app, line)
            
        # Auf Fehler prüfen
        for line in process.stderr:
            app.log(line.strip(), level="error")
            
        # Auf Prozessende warten
        process.wait()
        
        # Ergebnis anzeigen
        if process.returncode == 0:
            app.log("Verarbeitung erfolgreich abgeschlossen.", level="success")
            app.status_label.config(text="Bereit")
            
            # Dashboard aktualisieren
            app.root.after(1000, app.update_dashboard)
            
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