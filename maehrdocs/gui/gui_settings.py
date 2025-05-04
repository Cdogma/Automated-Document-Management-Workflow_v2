# gui_settings.py
"""
Einstellungsmodul für MaehrDocs (Kompatibilitätsschicht)
Dieses Modul importiert die Funktionen aus den neuen aufgeteilten Modulen
für die Abwärtskompatibilität.
"""

# Importiere alle Funktionen aus den neuen Modulen
from .gui_settings_components import (
    create_settings_section,
    create_settings_tab,
    collect_settings_from_widget,
    search_and_update_field
)

from .gui_settings_dialog import (
    open_settings,
    save_settings,
    browse_folder
)