#!/usr/bin/env python
"""
Test-Skript für die Statistik-Komponente
Prüft, ob die neue Komponente korrekt eingebunden werden kann.
"""

import os
import sys
import tkinter as tk

# Füge das Projektverzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Initialisiere Logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_test():
    """
    Führt den Test für die Statistik-Komponente durch.
    """
    try:
        logger.info("Teste Import der Statistik-Komponente...")
        # Versuche, die Module direkt zu importieren (ohne maehrdocs Präfix)
        from gui_statistics import create_statistics_panel
        from gui_statistics_data import collect_data
        from gui_statistics_charts import create_chart_figure
        
        logger.info("✅ Erfolg: Alle Module konnten importiert werden.")
        
        # Teste matplotlib
        logger.info("Teste matplotlib...")
        import matplotlib
        logger.info(f"✅ Erfolg: Matplotlib Version {matplotlib.__version__} gefunden.")
        
        # Erstelle ein einfaches Test-GUI
        logger.info("Erstelle Test-GUI...")
        root = tk.Tk()
        root.title("Statistik-Komponenten-Test")
        root.geometry("800x600")
        
        # Mock app-Objekt erstellen
        class MockApp:
            def __init__(self):
                self.colors = {
                    "background_dark": "#0D1117",
                    "background_medium": "#161B22",
                    "card_background": "#1F2937",
                    "primary": "#3B82F6",
                    "accent": "#60A5FA",
                    "text_primary": "#F9FAFB",
                    "text_secondary": "#9CA3AF",
                    "success": "#10B981",
                    "warning": "#FBBF24",
                    "error": "#EF4444"
                }
                self.fonts = {
                    "header": ("Segoe UI", 16, "bold"),
                    "subheader": ("Segoe UI", 14, "bold"),
                    "normal": ("Segoe UI", 12),
                    "small": ("Segoe UI", 10),
                    "code": ("Consolas", 11)
                }
                self.config = {
                    "paths": {
                        "output_dir": os.path.join(current_dir, "test_output"),
                        "input_dir": os.path.join(current_dir, "test_input"),
                        "trash_dir": os.path.join(current_dir, "test_trash")
                    }
                }
                # Stelle sicher, dass die Testverzeichnisse existieren
                for directory in self.config["paths"].values():
                    if not os.path.exists(directory):
                        os.makedirs(directory)
        
        mock_app = MockApp()
        
        # Erstelle einen Hauptframe
        main_frame = tk.Frame(root, bg=mock_app.colors["background_medium"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Versuche, das Statistik-Panel zu erstellen
        try:
            stats_panel = create_statistics_panel(mock_app, main_frame)
            logger.info("✅ Erfolg: Statistik-Panel wurde erstellt.")
            
            # Zeige den Test-GUI
            logger.info("Test-GUI wird angezeigt...")
            root.mainloop()
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Erstellen des Statistik-Panels: {str(e)}")
            return False
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import-Fehler: {str(e)}")
        logger.error("Ein oder mehrere Module konnten nicht importiert werden.")
        logger.error("Bitte überprüfen Sie, ob alle Dateien korrekt erstellt wurden.")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== MaehrDocs Statistik-Komponenten-Test ===\n")
    
    success = run_test()
    
    if success:
        print("\n✅ Test erfolgreich abgeschlossen!")
        print("Die Statistik-Komponente wurde korrekt eingebunden.")
        print("Sie können die Anwendung jetzt mit dem normalen Starter starten.")
    else:
        print("\n❌ Test fehlgeschlagen!")
        print("Bitte überprüfen Sie die Fehlermeldungen und korrigieren Sie den Code.")