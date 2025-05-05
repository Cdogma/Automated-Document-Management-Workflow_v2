"""
────────────────────────────────────────────────────────────────────────────
check_env.py – Prüfung der Python-Umgebung auf wichtige Abhängigkeiten
────────────────────────────────────────────────────────────────────────────

🧾 Beschreibung:
Dieses Tool prüft, ob du dich in einer aktiven venv befindest und ob alle wichtigen
Pakete wie pydot, openai, pymupdf usw. korrekt installiert sind.

📁 Es erstellt automatisch:
- eine Logdatei namens `env_status.log` mit dem Prüfprotokoll
- eine aktuelle `requirements.txt` für Backup oder Weitergabe
- ein GUI-Fenster (Ampel) mit Statusmeldung (grün/gelb/rot)

👨‍💻 Autor: René & Professor Schlau 🧙🏾‍♂️
📅 Stand: 2025-05-05
"""

import sys
import importlib.util
from datetime import datetime
import subprocess
import tkinter as tk
from tkinter import messagebox

# 🧩 Pakete, die für dein Projekt wichtig sind
wichtige_pakete = [
    "pydot",
    "yaml",         # entspricht pyyaml
    "tkinterdnd2",
    "openai",
    "pymupdf",
    "dotenv"        # entspricht python-dotenv
]

# Prüft, ob venv aktiv ist
def ist_venv_aktiv():
    return (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ) or hasattr(sys, 'real_prefix')

# Prüft, ob ein Paket installiert ist
def ist_paket_da(name):
    return importlib.util.find_spec(name) is not None

# Schreibt eine Logdatei
def schreibe_log(dateiname, inhalt):
    with open(dateiname, "w", encoding="utf-8") as f:
        f.write("\n".join(inhalt))

# Zeigt GUI-Ampelfenster mit Status
def zeige_statusfenster(venv_aktiv, fehlende_pakete):
    root = tk.Tk()
    root.withdraw()  # kein Hauptfenster
    if venv_aktiv and not fehlende_pakete:
        messagebox.showinfo("🟢 Alles ok", "Alle Pakete sind vorhanden.\nVirtuelle Umgebung ist aktiv.")
    elif not venv_aktiv:
        messagebox.showerror("❌ Keine venv", "Du befindest dich NICHT in einer aktiven virtuellen Umgebung!")
    else:
        fehlende_str = "\n".join(fehlende_pakete)
        messagebox.showwarning("⚠️ Fehlende Pakete", f"Folgende Pakete fehlen:\n{fehlende_str}")

# Hauptfunktion zur Prüfung
def prüfe_umgebung():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fehlende = []
    log = [f"📅 Prüfzeitpunkt: {timestamp}", ""]

    # Venv prüfen
    venv_aktiv = ist_venv_aktiv()
    if venv_aktiv:
        print("✅ Virtuelle Umgebung ist aktiv.")
        log.append("✅ Virtuelle Umgebung ist aktiv.")
    else:
        print("❌ Keine virtuelle Umgebung erkannt!")
        log.append("❌ Keine virtuelle Umgebung erkannt!")

    # Pakete prüfen
    for paket in wichtige_pakete:
        vorhanden = ist_paket_da(paket)
        status = f"✅ Paket gefunden: {paket}" if vorhanden else f"❌ Paket fehlt: {paket}"
        print(status)
        log.append(status)
        if not vorhanden:
            fehlende.append(paket)

    # Hinweis für fehlende Pakete
    if fehlende:
        install_cmd = "pip install " + " ".join(fehlende)
        print(f"\n💡 Du kannst fehlende Pakete installieren mit:\n{install_cmd}")
        log.append(f"\n💡 Du kannst fehlende Pakete installieren mit:\n{install_cmd}")
    else:
        print("\n🎉 Alle wichtigen Pakete sind vorhanden!")
        log.append("\n🎉 Alle wichtigen Pakete sind vorhanden!")

    print("\n🟢 Prüfung abgeschlossen.")
    log.append("\n🟢 Prüfung abgeschlossen.\n")

    # Log schreiben
    schreibe_log("env_status.log", log)

    # GUI-Fenster anzeigen
    zeige_statusfenster(venv_aktiv, fehlende)

    # requirements.txt erzeugen
    try:
        with open("requirements.txt", "w", encoding="utf-8") as req:
            subprocess.run(["pip", "freeze"], stdout=req, check=True)
        print("📦 Datei 'requirements.txt' wurde erfolgreich erstellt.")
    except Exception as e:
        print(f"⚠️ Fehler beim Schreiben von requirements.txt: {e}")

# Skript ausführen
if __name__ == "__main__":
    print("🧪 Umgebung prüfen...\n")
    prüfe_umgebung()
