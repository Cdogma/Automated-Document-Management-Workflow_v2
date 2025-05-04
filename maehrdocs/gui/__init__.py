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

# Import der Event-Handler (jetzt aus gui_actions statt gui_handlers)
from .gui_actions import (
    process_documents, 
    simulate_processing, 
    process_single_file
)

# Spezifische Module aus der neuen Aufteilung
from .gui_document_actions import rebuild_config
from .gui_drop_handlers import handle_drop, copy_files_to_inbox
from .gui_command_executor import run_command_in_thread
from .gui_notification_handlers import handle_duplicate_from_log

# Exportiere die wichtigsten Klassen und Funktionen
__all__ = [
    'GuiApp',
    'create_button',
    'create_status_card',
    'create_dashboard',
    'open_settings',
    'compare_documents',
    'open_document',
    'process_documents',
    'rebuild_config',
    'handle_drop',
    'run_command_in_thread',
    'handle_duplicate_from_log'
]