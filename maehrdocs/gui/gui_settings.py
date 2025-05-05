# gui_settings.py
"""
Einstellungsmodul für MaehrDocs (Kompatibilitätsschicht)
Dieses Modul importiert die Funktionen aus den neuen aufgeteilten Modulen
für die Abwärtskompatibilität.
"""

# Importiere Funktionen aus dem speziellen Komponententab
from .gui_settings_components import (
    create_settings_section,
    create_settings_tab,
    collect_settings_from_widget,
    search_and_update_field
)

# Importiere Funktionen aus dem Dialogmodul
from .gui_settings_dialog import (
    open_settings,
    create_general_tab,
    create_openai_tab,
    create_document_tab,
    create_notifications_tab,
    save_settings,
    browse_folder
)

# Re-Exportiere alle Funktionen für Abwärtskompatibilität
__all__ = [
    'create_settings_section',
    'create_settings_tab',
    'collect_settings_from_widget',
    'search_and_update_field',
    'open_settings',
    'create_general_tab',
    'create_openai_tab',
    'create_document_tab',
    'create_notifications_tab',
    'save_settings',
    'browse_folder'
]