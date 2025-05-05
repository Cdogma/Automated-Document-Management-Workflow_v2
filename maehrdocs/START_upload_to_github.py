"""
upload_to_github.py – Schneller Git-Upload für deine Prüfskripte & Reports
────────────────────────────────────────────────────────────────────────────
Fügt alle Änderungen in deinem Projektverzeichnis zum Git-Repo hinzu,
committet sie automatisch mit einem Zeitstempel und pusht sie zu GitHub.

Voraussetzung: 
- Dein Projekt ist bereits ein `git init` Repository
- Du hast `origin` zu GitHub verbunden (z. B. via SSH oder https)
"""

import subprocess
from datetime import datetime

commit_message = f"🧾 Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Änderungen erfolgreich zu GitHub hochgeladen.")
except subprocess.CalledProcessError as e:
    print(f"❌ Fehler bei Git-Upload: {e}")
