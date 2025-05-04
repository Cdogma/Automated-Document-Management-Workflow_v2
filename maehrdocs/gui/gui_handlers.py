"""
Event-Handler und Aktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Benutzeraktionen und Ereignissen
"""

import os
import time
import subprocess
import threading
from tkinter import filedialog, messagebox
import shutil
from datetime import datetime
from .gui_document_viewer import show_duplicate_alert

def process_documents(app):
    """
    Verarbeitet alle Dokumente im Eingangsordner
    
    Args:
        app: Instanz der GuiApp
    """
    run_command_in_thread(app, ["python", "autodocs_v2.py"])

def simulate_processing(app):
    """
    Führt eine Simulation (Dry-Run) durch
    
    Args:
        app: Instanz der GuiApp
    """
    run_command_in_thread(app, ["python", "autodocs_v2.py", "--dry-run"])

def process_single_file(app):
    """
    Verarbeitet eine einzelne vom Benutzer ausgewählte Datei
    
    Args:
        app: Instanz der GuiApp
    """
    file_path = filedialog.askopenfilename(
        title="PDF-Datei auswählen",
        filetypes=[("PDF-Dateien", "*.pdf")]
    )
    
    if file_path:
        run_command_in_thread(app, ["python", "autodocs_v2.py", "--single-file", file_path])

def rebuild_config(app):
    """
    Setzt die Konfiguration zurück
    
    Args:
        app: Instanz der GuiApp
    """
    if messagebox.askyesno(
        "Konfiguration zurücksetzen", 
        "Möchten Sie die Konfiguration wirklich zurücksetzen? "
        "Alle benutzerdefinierten Einstellungen gehen verloren."
    ):
        run_command_in_thread(app, ["python", "autodocs_v2.py", "--rebuild-config"])

def handle_drop(app, event):
    """
    Verarbeitet gedropte Dateien
    
    Args:
        app: Instanz der GuiApp
        event: Drop-Event mit Dateiinformationen
    """
    # Prüfen, ob Drag & Drop aktiviert ist
    if not hasattr(event, 'data'):
        app.log("Drag & Drop ist nicht verfügbar.", level="warning")
        return
        
    # Liste der gedropten Dateien
    files = event.data
    
    # Windows-Pfade verarbeiten
    if os.name == 'nt':
        files = files.replace('{', '').replace('}', '')
        file_list = files.split()
    else:
        file_list = files.split()
    
    # PDF-Filter
    pdf_files = [f for f in file_list if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        messagebox.showinfo("Keine PDFs", "Es wurden keine PDF-Dateien zum Verarbeiten gefunden.")
        return
        
    # Bestätigung
    if len(pdf_files) == 1:
        answer = messagebox.askyesno(
            "Datei verarbeiten", 
            f"Möchten Sie die Datei '{os.path.basename(pdf_files[0])}' verarbeiten?"
        )
        if answer:
            run_command_in_thread(app, ["python", "autodocs_v2.py", "--single-file", pdf_files[0]])
    else:
        # Bei mehreren Dateien fragen, ob man sie in den Eingangsordner kopieren möchte
        answer = messagebox.askyesno(
            "Dateien verarbeiten", 
            f"Möchten Sie {len(pdf_files)} PDF-Dateien in den Eingangsordner kopieren?"
        )
        if answer:
            copy_files_to_inbox(app, pdf_files)

def copy_files_to_inbox(app, file_list):
    """
    Kopiert Dateien in den Eingangsordner
    
    Args:
        app: Instanz der GuiApp
        file_list: Liste der zu kopierenden Dateipfade
    """
    from tkinter import ttk
    
    inbox_dir = app.config["paths"]["input_dir"]
    
    # Fortschrittsfenster erstellen
    progress_window = tk.Toplevel(app.root)
    progress_window.title("Dateien werden kopiert...")
    progress_window.geometry("400x200")
    progress_window.configure(bg=app.colors["background_dark"])
    progress_window.grab_set()  # Modal machen
    
    progress_frame = tk.Frame(
        progress_window, 
        bg=app.colors["background_medium"], 
        padx=20, 
        pady=20
    )
    progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Beschreibung
    label = tk.Label(
        progress_frame, 
        text=f"Kopiere {len(file_list)} Dateien in den Eingangsordner...", 
        font=app.fonts["normal"],
        fg=app.colors["text_primary"],
        bg=app.colors["background_medium"]
    )
    label.pack(pady=10)
    
    # Fortschrittsbalken
    progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
    progress.pack(pady=10)
    
    # Dateiname
    file_label = tk.Label(
        progress_frame, 
        text="", 
        font=app.fonts["small"],
        fg=app.colors["text_secondary"],
        bg=app.colors["background_medium"]
    )
    file_label.pack(pady=5)
    
    # In einem Thread kopieren
    def copy_thread():
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(file_list):
            try:
                # UI aktualisieren
                progress['value'] = (i / len(file_list)) * 100
                file_name = os.path.basename(file_path)
                file_label.config(text=f"Kopiere: {file_name}")
                
                # Datei kopieren
                dest_path = os.path.join(inbox_dir, file_name)
                shutil.copy2(file_path, dest_path)
                
                # Log
                app.log(f"Datei kopiert: {file_name}")
                success_count += 1
                
            except Exception as e:
                app.log(f"Fehler beim Kopieren von {os.path.basename(file_path)}: {str(e)}", level="error")
                error_count += 1
                
            # Kurze Pause für die UI
            time.sleep(0.1)
        
        # Fertig
        progress['value'] = 100
        file_label.config(text="Kopiervorgang abgeschlossen")
        
        # Abschlussmeldung
        if error_count == 0:
            messagebox.showinfo(
                "Kopiervorgang abgeschlossen", 
                f"Alle {success_count} Dateien wurden erfolgreich in den Eingangsordner kopiert."
            )
        else:
            messagebox.showwarning(
                "Kopiervorgang mit Fehlern abgeschlossen", 
                f"{success_count} Dateien erfolgreich kopiert, {error_count} Fehler aufgetreten."
            )
        
        # Fenster schließen
        progress_window.destroy()
        
        # Dashboard aktualisieren
        app.update_dashboard()
        
        # Fragen, ob die Dateien verarbeitet werden sollen
        if success_count > 0 and messagebox.askyesno(
            "Dateien verarbeiten", 
            f"Möchten Sie die {success_count} kopierten Dateien jetzt verarbeiten?"
        ):
            process_documents(app)
    
    # Thread starten
    thread = threading.Thread(target=copy_thread)
    thread.daemon = True
    thread.start()

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

def handle_duplicate_from_log(app, log_line):
    """
    Verarbeitet Duplikatbenachrichtigungen aus der Protokollausgabe
    
    Args:
        app: Instanz der GuiApp
        log_line: Log-Zeile mit Duplikatinformationen
    """
    try:
        # Aus dem Log-Text die relevanten Informationen extrahieren
        # Format könnte sein: "DUPLICATE DETECTED: [Original: file1.pdf] [Duplicate: file2.pdf] [Similarity: 0.92]"
        if "[Original:" in log_line and "[Duplicate:" in log_line and "[Similarity:" in log_line:
            # Original-Datei extrahieren
            original_start = log_line.find("[Original:") + 10
            original_end = log_line.find("]", original_start)
            original_file = log_line[original_start:original_end].strip()
            
            # Duplikat-Datei extrahieren
            duplicate_start = log_line.find("[Duplicate:") + 11
            duplicate_end = log_line.find("]", duplicate_start)
            duplicate_file = log_line[duplicate_start:duplicate_end].strip()
            
            # Ähnlichkeitswert extrahieren
            similarity_start = log_line.find("[Similarity:") + 12
            similarity_end = log_line.find("]", similarity_start)
            similarity_str = log_line[similarity_start:similarity_end].strip()
            similarity_score = float(similarity_str)
            
            # Popup anzeigen, wenn aktiviert
            if app.config.get("gui", {}).get("show_duplicate_popup", True):
                show_duplicate_alert(app, original_file, duplicate_file, similarity_score)
    except Exception as e:
        app.log(f"Fehler bei der Verarbeitung der Duplikatbenachrichtigung: {str(e)}", level="error")