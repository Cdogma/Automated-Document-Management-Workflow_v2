"""
START_MAEHRDOCS_GUI_Launcher.py – GUI-Launcher für MaehrDocs-Tools
────────────────────────────────────────────────────────────

🧾 Beschreibung:
Dieses Fenster-Tool bietet dir eine übersichtliche Bedienoberfläche, um die wichtigsten MaehrDocs-Tools direkt per Klick zu starten:
- Umgebung prüfen (Konsole)
- Umgebung prüfen (HTML)
- Projekt auf GitHub hochladen

Es ist modular aufgebaut, d. h. du kannst es später um neue Tools, Tabs oder ein Theme erweitern.

Autor: René & Professor Schlau 🧙🏾‍♂️
Stand: 2025-05-05
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def tool_starten(beschreibung, befehl):
    try:
        ausgabe.config(text=f"🚀 Starte: {beschreibung}...")
        subprocess.run(befehl, shell=True, check=True)
        ausgabe.config(text=f"✅ {beschreibung} erfolgreich beendet.")
    except subprocess.CalledProcessError:
        ausgabe.config(text=f"❌ Fehler beim Ausführen von: {beschreibung}")
        messagebox.showerror("Fehler", f"Das Tool '{beschreibung}' konnte nicht gestartet werden.")

# Hauptfenster
root = tk.Tk()
root.title("🧰 MaehrDocs Tool-Launcher")
root.geometry("460x260")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# Titel
tk.Label(root, text="Willkommen bei MaehrDocs", font=("Segoe UI", 16, "bold"), bg="#f0f0f0").pack(pady=10)

# Button-Bereich
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=10)

tk.Button(frame, text="🔍 Umgebung prüfen (Konsole)", width=35, command=lambda: tool_starten("check_env.py", "python maehrdocs/check_env.py")).pack(pady=5)
tk.Button(frame, text="🌐 Umgebung prüfen (HTML)", width=35, command=lambda: tool_starten("check_env_html.py", "python maehrdocs/check_env_html.py")).pack(pady=5)
tk.Button(frame, text="⬆️ Projekt zu GitHub hochladen", width=35, command=lambda: tool_starten("Upload zu GitHub", "python maehrdocs/START_upload_to_github.py")).pack(pady=5)

# Ausgabe unten
ausgabe = tk.Label(root, text="Bereit", bg="#f0f0f0", fg="#333", anchor="w")
ausgabe.pack(fill="x", padx=10, pady=(15, 5))

# Start
root.mainloop()
