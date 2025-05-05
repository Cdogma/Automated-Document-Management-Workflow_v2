r"""
────────────────────────────────────────────────────────────────────────────
Start_Paketvergleich_venv.py – Vergleich globaler Python-Pakete mit virtueller Umgebung
────────────────────────────────────────────────────────────────────────────

🧾 Beschreibung:
Dieses Tool hilft dir dabei, dein Python-Projekt auf eine saubere und isolierte
virtuelle Umgebung (venv) umzustellen. Es vergleicht, welche Pakete du früher
im globalen Python-Setup installiert hattest, und prüft, welche davon noch nicht
in deiner aktuellen venv enthalten sind.

So vermeidest du unnötige Altlasten und kannst gezielt nur die benötigten Pakete
in deine neue Umgebung übernehmen.

Es werden zwei Paketlisten verglichen:

1. `old_global_packages.txt`
   → Eine Liste aller Pakete, die du früher global installiert hattest.
   (erstellt mit `pip freeze > old_global_packages.txt`, **außerhalb der venv**)

2. `current_venv_packages.txt`
   → Eine Liste aller Pakete, die aktuell in deiner aktiven venv installiert sind.
   (erstellt mit `pip freeze > current_venv_packages.txt`, **innerhalb der venv**)

🎯 Ziel:
Das Skript zeigt dir, welche Pakete fehlen – und erstellt zusätzlich automatisch
ein Installationsskript (`install_missing_packages.bat`), mit dem du alle
fehlenden Pakete bequem nachinstallieren kannst.

💡 Vorteile:
- Du vermeidest Chaos im globalen Python-System
- Du erhältst volle Kontrolle über die venv
- Du kannst das Setup später reproduzieren

🛠 Anwendungsschritte:

1. Erstelle die beiden Paketlisten:
   - Global (außerhalb venv):  
     `pip freeze > old_global_packages.txt`
   - In venv (nach Aktivierung):  
     `pip freeze > current_venv_packages.txt`

2. Aktiviere deine venv:
   - PowerShell (Windows):  
     `.\venv\Scripts\Activate.ps1`

3. Starte dieses Skript:
   - `python Start_Paketvergleich_venv.py`

4. Ergebnis:
   - Die fehlenden Pakete werden in der Konsole angezeigt
   - Eine Datei `install_missing_packages.bat` wird erstellt

5. Installiere die Pakete bei Bedarf:
   - Durch Ausführen von `install_missing_packages.bat` (Doppelklick oder Konsole)

👨‍💻 Autor: René & Professor Schlau 🧙🏾‍♂️
📅 Datum: 2025-05-05
"""

def lade_paketliste(dateiname):
    encodings = ['utf-8', 'utf-16', 'latin-1']
    for encoding in encodings:
        try:
            with open(dateiname, 'r', encoding=encoding) as f:
                inhalt = {zeile.strip().split('==')[0].lower() for zeile in f if '==' in zeile}
                print(f"📥 Datei '{dateiname}' erfolgreich gelesen mit Encoding: {encoding}")
                return inhalt
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"❌ Datei nicht gefunden: {dateiname}")
            return set()
    print(f"❌ Konnte '{dateiname}' mit keiner unterstützten Kodierung lesen.")
    return set()

# Lade Paketlisten
global_pakete = lade_paketliste('old_global_packages.txt')
venv_pakete = lade_paketliste('current_venv_packages.txt')

# Fehlende Pakete berechnen
fehlende_pakete = global_pakete - venv_pakete

# Ausgabe und Erstellung der Batch-Datei
if fehlende_pakete:
    print("⚠️ Diese Pakete fehlen in deiner Virtual Environment:\n")
    with open('install_missing_packages.bat', 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("REM Installiert alle fehlenden Pakete in der aktiven venv\n\n")
        for paket in sorted(fehlende_pakete):
            print(f"  pip install {paket}")
            f.write(f"pip install {paket}\n")
    print("\n💾 Datei 'install_missing_packages.bat' wurde erfolgreich erstellt.")
else:
    print("✅ Deine venv enthält bereits alle zuvor genutzten Pakete.")

