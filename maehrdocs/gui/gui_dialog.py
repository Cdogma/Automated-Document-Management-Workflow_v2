"""
Dialog-Komponenten für MaehrDocs
Enthält standardisierte Dialogfunktionen für Benutzerinteraktionen wie
Bestätigungen, Informationen, Warnungen und Fehlermeldungen.

Diese Dialoge verwenden das native Messagebox-Modul von Tkinter und
sind im Stil der Anwendung gestaltet.
"""

import tkinter as tk
from tkinter import messagebox

def show_confirm_dialog(app, title, message):
    """
    Zeigt einen Bestätigungsdialog mit Ja/Nein-Optionen an.
    
    Dieser Dialog blockiert die Anwendung, bis der Benutzer eine Auswahl
    getroffen hat, und gibt das Ergebnis zurück.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        title (str): Der Titel des Dialogs
        message (str): Die Nachricht des Dialogs
        
    Returns:
        bool: True wenn der Benutzer "Ja" wählt, False wenn "Nein" gewählt wird
    """
    return messagebox.askyesno(title, message)

def show_info_dialog(app, title, message):
    """
    Zeigt einen Informationsdialog mit einer OK-Schaltfläche an.
    
    Verwendet für Mitteilungen und Hinweise, die der Benutzer lesen und
    bestätigen soll, ohne eine Entscheidung treffen zu müssen.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        title (str): Der Titel des Dialogs
        message (str): Die Nachricht des Dialogs
    """
    messagebox.showinfo(title, message)
    
def show_error_dialog(app, title, message):
    """
    Zeigt einen Fehlerdialog mit einem Fehlersymbol und einer OK-Schaltfläche an.
    
    Verwendet für Fehlermeldungen und kritische Probleme, die die Aufmerksamkeit
    des Benutzers erfordern.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        title (str): Der Titel des Dialogs
        message (str): Die Nachricht des Dialogs
    """
    messagebox.showerror(title, message)
    
def show_warning_dialog(app, title, message):
    """
    Zeigt einen Warnungsdialog mit einem Warnsymbol und einer OK-Schaltfläche an.
    
    Verwendet für Warnungen und potenzielle Probleme, die der Benutzer beachten
    sollte, aber nicht unbedingt ein Eingreifen erfordern.
    
    Args:
        app: Die Hauptanwendung (GuiApp-Instanz)
        title (str): Der Titel des Dialogs
        message (str): Die Nachricht des Dialogs
    """
    messagebox.showwarning(title, message)