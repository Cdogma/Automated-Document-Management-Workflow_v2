"""
Event-Handler und Aktionen für MaehrDocs
Enthält Funktionen zur Verarbeitung von Benutzeraktionen und Ereignissen
"""

# Re-Exporte aus den spezialisierten Modulen für Abwärtskompatibilität

# Dokumentenaktionen
from .gui_document_actions import (
    process_documents,
    simulate_processing,
    process_single_file,
    rebuild_config
)

# Drag & Drop Handler
from .gui_drop_handlers import (
    handle_drop,
    copy_files_to_inbox
)

# Befehlsausführung
from .gui_command_executor import (
    run_command_in_thread,
    _run_command
)

# Benachrichtigungshandler
from .gui_notification_handlers import (
    handle_duplicate_from_log
)