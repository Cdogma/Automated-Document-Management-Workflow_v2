# dialog.py
import tkinter as tk
from tkinter import messagebox

def show_confirm_dialog(app, title, message):
    """
    Zeigt einen Bestätigungsdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
        
    Returns:
        bool: True wenn der Benutzer bestätigt hat, sonst False
    """
    return messagebox.askyesno(title, message)

def show_info_dialog(app, title, message):
    """
    Zeigt einen Informationsdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    messagebox.showinfo(title, message)
    
def show_error_dialog(app, title, message):
    """
    Zeigt einen Fehlerdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    messagebox.showerror(title, message)
    
def show_warning_dialog(app, title, message):
    """
    Zeigt einen Warnungsdialog an
    
    Args:
        app: Die Hauptanwendung
        title: Der Titel des Dialogs
        message: Die Nachricht des Dialogs
    """
    messagebox.showwarning(title, message)