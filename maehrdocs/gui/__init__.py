"""
GUI-Paket für MaehrDocs
Enthält alle GUI-bezogenen Komponenten und Funktionalitäten
"""

# Import der Hauptklasse
from .gui_core import GuiApp

# Import der Button-Komponenten
from .gui_buttons import (
    create_button, 
    create_icon_button, 
    create_toggle_button
)

# Import der Karten-Komponenten
from .gui_cards import (
    create_status_card, 
    create_info_card, 
    create_activity_card, 
    create_section_frame
)

# Import der Formular-Komponenten
from .gui_forms import (
    create_settings_section, 
    create_form_field
)

# Import der Dashboard-Funktionen
from .gui_dashboard import create_dashboard

# Import der Einstellungs-Funktionen
from .gui_settings import open_settings

# Import der Dokumentenansicht-Funktionen
from .gui_document_viewer import (
    compare_documents, 
    open_document
)

# Import der Event-Handler
from .gui_handlers import (
    process_documents, 
    simulate_processing, 
    process_single_file
)

# Exportiere die wichtigsten Klassen und Funktionen
__all__ = [
    'GuiApp',
    'create_button',
    'create_status_card',
    'create_dashboard',
    'open_settings',
    'compare_documents',
    'open_document',
    'process_documents'
]