"""
check_python_apps.py – Python-Pakete prüfen und aktualisieren
────────────────────────────────────────────────────────────

🧾 Beschreibung:
Dieses Tool listet alle veralteten Python-Pakete im aktuellen Environment auf
und bietet optional die Möglichkeit, alle Pakete automatisch zu aktualisieren.

Funktionen:
- 📦 Anzeige veralteter Pakete mit Versionen
- 🔄 Automatisches Upgrade aller Pakete (nach Bestätigung)
- 🧠 Sicherer Ablauf mit Benutzerabfrage vor Updates
- 💻 Unterstützt virtuelle Umgebungen

Verwendung:
- Direkt im MaehrDocs-Launcher startbar
- Alternativ über Konsole: `python check_python_apps.py`

Autor: René & Professor Schlau 🧙🏾‍♂️
Stand: 2025-05-05
"""

import subprocess
import sys

def check_outdated_packages():
    print("📦 Veraltete Python-Pakete:\n")
    subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"])


def upgrade_all_packages():
    print("\n⚠️ Diese Aktion wird ALLE veralteten Pakete updaten.")
    confirm = input("Bist du sicher? [j/n]: ").strip().lower()
    if confirm != "j":
        print("❌ Update abgebrochen.")
        return

    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=freeze"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().splitlines()

    if not lines:
        print("✅ Alle Pakete sind aktuell.")
        return

    for line in lines:
        package = line.split("==")[0]
        print(f"⬆️ Aktualisiere {package} ...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package])
    print("✅ Alle verfügbaren Updates wurden abgeschlossen.")


if __name__ == "__main__":
    print("\n=== Python-Paketprüfung (MaehrDocs) ===\n")
    print("1. Veraltete Pakete anzeigen")
    print("2. Alle Pakete aktualisieren")
    print("0. Abbrechen")

    choice = input("\nBitte Auswahl eingeben (1/2/0): ").strip()

    if choice == "1":
        check_outdated_packages()
    elif choice == "2":
        upgrade_all_packages()
    else:
        print("❌ Abgebrochen.")
