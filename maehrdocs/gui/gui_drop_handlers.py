"""
Drag & Drop Handler für MaehrDocs
Enthält Funktionen zum Verarbeiten von Drag & Drop Ereignissen
"""

import os
import time
import shutil
import threading
import tkinter as tk
from tkinter import messagebox

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
            from .gui_command_executor import run_command_in_thread
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
            from .gui_document_actions import process_documents
            process_documents(app)
    
    # Thread starten
    thread = threading.Thread(target=copy_thread)
    thread.daemon = True
    thread.start()