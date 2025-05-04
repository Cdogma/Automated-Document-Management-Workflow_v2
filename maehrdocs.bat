@echo off
title MaehrDocs - Intelligente Dokumentenverwaltung
echo =================================================== 
echo  MaehrDocs - Intelligente Dokumentenverwaltung
echo ===================================================
echo.
echo  Starte MaehrDocs GUI...
echo.

REM GUI starten (mit pythonw für ein verstecktes Konsolenfenster)
start pythonw start_maehrdocs.py

REM Erfolgsmeldung ausgeben
echo MaehrDocs wurde erfolgreich gestartet.
echo Sie können dieses Fenster jetzt schließen.
echo.

timeout /t 3 >nul
exit