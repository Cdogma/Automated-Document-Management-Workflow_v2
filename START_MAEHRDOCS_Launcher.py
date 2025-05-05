"""
START.py – Tool-Launcher-Menü für MaehrDocs
────────────────────────────────────────────────────────────
✨ Komfortabler Einstiegspunkt für alle Tools des Projekts:
- Umgebung prüfen (Konsole oder HTML)
- Projekt über GitHub hochladen

🧙‍♂️ Professor Schlau-Tipp:
Das Menu ist modular aufgebaut und kann später um weitere Funktionen erweitert werden – z. B. Dokumentenscanner, PDF-Uploader usw.

Autor: René & Professor Schlau
Stand: 2025-05-05
"""

import subprocess
import os
import sys

def run_tool(command, beschreibung):
    print(f"\n🚀 Starte: {beschreibung}...\n")
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError:
        print(f"❌ Fehler beim Ausführen von: {beschreibung}\n")

def main_menu():
    while True:
        print("""
═════════════════════════════════════════════
🧰 MAEHRDOCS TOOL-STARTMENÜ
═════════════════════════════════════════════
[1] Umgebung prüfen (Konsole + Log)
[2] Umgebung prüfen (HTML + Browser)
[3] Projekt zu GitHub hochladen
[Q] Beenden
        """)

        wahl = input("Bitte Auswahl eingeben: ").strip().lower()

        if wahl == "1":
            run_tool("python maehrdocs/check_env.py", "check_env (Konsole)")
        elif wahl == "2":
            run_tool("python maehrdocs/check_env_html.py", "check_env_html (Browser)")
        elif wahl == "3":
            run_tool("python maehrdocs/START_upload_to_github.py", "GitHub Upload")
        elif wahl == "q":
            print("\n👋 Bis bald, Meister Mähr!")
            sys.exit(0)
        else:
            print("❗ Ungültige Eingabe. Bitte 1, 2, 3 oder Q wählen.")

if __name__ == "__main__":
    main_menu()
