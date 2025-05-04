# start_maehrdocs.py
from maehrdocs.config import ConfigManager
from maehrdocs.document_processor import DocumentProcessor
from maehrdocs.gui_manager import GuiManager

if __name__ == "__main__":
    # Initialisiere die Komponenten
    config_manager = ConfigManager()
    document_processor = DocumentProcessor(config_manager)
    gui_manager = GuiManager(config_manager, document_processor)
    
    # Starte die GUI
    root = gui_manager.setup_gui()
    root.mainloop()