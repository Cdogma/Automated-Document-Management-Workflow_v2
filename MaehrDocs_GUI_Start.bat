@echo off
title 🧰 MaehrDocs GUI-Launcher
cd /d "%~dp0"
call venv\Scripts\activate.bat
python START_MAEHRDOCS_GUI_Launcher.py
pause
