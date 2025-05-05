"""
────────────────────────────────────────────────────────────────────────────
check_env_html.py – HTML-Bericht zur Python-Umgebungsprüfung
────────────────────────────────────────────────────────────────────────────

🧾 Zweck:
Dieses Tool prüft, ob du dich in einer aktiven Python-virtuellen Umgebung (venv)
befindest und ob alle für dein Projekt wichtigen Pakete installiert sind.

👀 Besonderheit:
Statt nur die Konsole zu nutzen, erzeugt dieses Skript eine gut lesbare
HTML-Datei namens `env_status.html`. Diese zeigt dir visuell und übersichtlich:

- ob die virtuelle Umgebung aktiv ist
- welche Pakete vorhanden sind
- welche Pakete fehlen (inkl. pip-Install-Befehl)

💡 Vorteil:
Ideal zur Dokumentation, für Fehlersuche oder als Teil deiner Toolkette – z. B.
beim Projektstart, in Readmes oder zur Vorbereitung für Kollegen.

📦 Geprüfte Standardpakete:
- pydot
- yaml (PyYAML)
- tkinterdnd2
- openai
- pymupdf
- dotenv (python-dotenv)

🛠 Anleitung zur Nutzung:

1. Aktiviere deine venv (falls nicht automatisch):
   PowerShell:  .\venv\Scripts\Activate.ps1

2. Führe dieses Skript aus:
   python check_env_html.py

3. Das passiert automatisch:
   ✅ HTML-Datei wird erstellt
   ✅ requirements.txt wird aktualisiert
   ✅ HTML wird im Browser geöffnet
   ✅ Fenster mit Ampelstatus wird angezeigt

👨‍💻 Autor: René & Professor Schlau 🧙🏾‍♂️
📅 Stand: 2025-05-05
"""

import importlib.util
from datetime import datetime
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import webbrowser

wichtige_pakete = [
    "pydot",
    "yaml",
    "tkinterdnd2",
    "openai",
    "pymupdf",
    "dotenv"
]

def ist_venv_aktiv():
    return (
        hasattr(os.sys, 'base_prefix') and os.sys.base_prefix != os.sys.prefix
    ) or hasattr(os.sys, 'real_prefix')

def ist_paket_da(name):
    return importlib.util.find_spec(name) is not None

def zeige_statusfenster(venv_aktiv, fehlende_pakete):
    root = tk.Tk()
    root.withdraw()
    if venv_aktiv and not fehlende_pakete:
        messagebox.showinfo("🟢 Alles ok", "Alle Pakete sind vorhanden.\nVirtuelle Umgebung ist aktiv.")
    elif not venv_aktiv:
        messagebox.showerror("❌ Keine venv", "Du befindest dich NICHT in einer aktiven virtuellen Umgebung!")
    else:
        fehlende_str = "\n".join(fehlende_pakete)
        messagebox.showwarning("⚠️ Fehlende Pakete", f"Folgende Pakete fehlen:\n{fehlende_str}")

def erstelle_html_report(status_dict, log_datei="env_status.html"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = [
        "<html><head><meta charset='UTF-8'><title>Python-Umgebungsprüfung</title>",
        "<style>body{font-family:sans-serif;background:#f4f4f4;padding:2em;}h1{color:#444;}li{margin:0.5em 0;}",
        ".ok{color:green;}.fail{color:red;}</style></head><body>",
        f"<h1>🧪 Python-Umgebungsprüfung – {now}</h1>",
        f"<p><strong>Virtuelle Umgebung:</strong> {'<span class=\"ok\">aktiv</span>' if status_dict['venv'] else '<span class=\"fail\">nicht erkannt</span>'}</p>",
        "<ul>"
    ]

    for pkg, vorhanden in status_dict["pakete"].items():
        cls = "ok" if vorhanden else "fail"
        status = "✅ gefunden" if vorhanden else "❌ fehlt"
        html.append(f"<li class='{cls}'>{pkg}: {status}</li>")

    html.append("</ul>")
    if status_dict["fehlende"]:
        html.append("<h2>📦 Fehlende Pakete</h2>")
        html.append("<pre>pip install " + " ".join(status_dict["fehlende"]) + "</pre>")
    else:
        html.append("<p>🎉 Alle benötigten Pakete sind vorhanden.</p>")

    html.append("</body></html>")
    with open(log_datei, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"✅ HTML-Report gespeichert als: {log_datei}")
    webbrowser.open(log_datei)  # Automatisch im Browser öffnen

# Status prüfen
status = {
    "venv": ist_venv_aktiv(),
    "pakete": {},
    "fehlende": []
}

for paket in wichtige_pakete:
    vorhanden = ist_paket_da(paket)
    status["pakete"][paket] = vorhanden
    if not vorhanden:
        status["fehlende"].append(paket)

# HTML-Datei erzeugen und öffnen
erstelle_html_report(status)

# GUI-Ampelstatus anzeigen
zeige_statusfenster(status["venv"], status["fehlende"])

# requirements.txt erzeugen
try:
    with open("requirements.txt", "w", encoding="utf-8") as req:
        subprocess.run(["pip", "freeze"], stdout=req, check=True)
    print("📦 Datei 'requirements.txt' wurde erfolgreich erstellt.")
except Exception as e:
    print(f"⚠️ Fehler beim Schreiben von requirements.txt: {e}")
