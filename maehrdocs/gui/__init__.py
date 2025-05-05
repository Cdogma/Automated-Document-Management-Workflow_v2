
"""
GUI-Paket für MaehrDocs

Dieses Modul bündelt sämtliche grafischen Komponenten und Funktionen der Benutzeroberfläche für MaehrDocs. 
Es stellt eine modulare, erweiterbare und benutzerfreundliche GUI bereit, die sowohl für die visuelle Darstellung 
als auch für die Interaktion mit dem Dokumentenmanagement-System zuständig ist.

Die enthaltenen Komponenten decken folgende Bereiche ab:
- Aufbau und Start der Haupt-GUI-Anwendung (GuiApp)
- Wiederverwendbare UI-Elemente wie Buttons, Karten, Formulare und Einstellungssektionen
- Anzeige- und Vergleichsfunktionen für Dokumente
- Dashboard zur Darstellung von Statusinformationen und Aktivitäten
- Aktionen zur Dokumentenverarbeitung (z. B. Analyse, Umbenennung, Verschiebung)
- Drag & Drop-Unterstützung und asynchrone Befehlsausführung
- Integration von Benachrichtigungen und Duplikatserkennung

Dieses Paket dient als zentrales Interface zwischen dem Benutzer und der Automatisierungslogik 
von MaehrDocs. Es unterstützt eine konsistente UX und erlaubt durch die klare Modulstruktur 
eine einfache Erweiterung oder Anpassung der Oberfläche.
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
from .gui_forms import create_form_field
from .gui_settings_components import create_settings_section

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