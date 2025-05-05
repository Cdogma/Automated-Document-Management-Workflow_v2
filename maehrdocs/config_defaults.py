"""
Standard-Konfigurationswerte für MaehrDocs
Enthält Funktionen zur Erstellung der Standardkonfiguration 
und zur Verzeichnisverwaltung.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def create_default_config() -> Dict[str, Any]:
    """
    Erstellt eine Standardkonfiguration
    
    Returns:
        dict: Die Standardkonfiguration
    """
    home_dir = str(Path.home())
    base_dir = os.path.join(home_dir, "OneDrive", "09_AutoDocs")
    
    # Stellen Sie sicher, dass die Standardordner existieren
    ensure_directories_exist([
        os.path.join(base_dir, "01_InboxDocs"),
        os.path.join(base_dir, "02_FinalDocs"),
        os.path.join(base_dir, "03_TrashDocs")
    ])
    
    # Standardkonfiguration
    return {
        "paths": {
            "input_dir": os.path.join(base_dir, "01_InboxDocs"),
            "output_dir": os.path.join(base_dir, "02_FinalDocs"),
            "trash_dir": os.path.join(base_dir, "03_TrashDocs")
        },
        "openai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "max_retries": 3
        },
        "document_processing": {
            "max_file_size_mb": 20,
            "similarity_threshold": 0.85,
            "valid_doc_types": [
                "rechnung",
                "vertrag",
                "brief",
                "meldung",
                "bescheid",
                "dokument",
                "antrag"
            ]
        },
        "gui": {
            "show_duplicate_popup": True,
            "notify_on_completion": True,
            "enable_sounds": False,
            "notify_on_new_documents": True
        }
    }

def ensure_directories_exist(directory_list: List[str]) -> None:
    """
    Stellt sicher, dass die angegebenen Verzeichnisse existieren
    
    Args:
        directory_list: Liste der zu prüfenden Verzeichnisse
    """
    for directory in directory_list:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Verzeichnis erstellt: {directory}")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen von Verzeichnis {directory}: {str(e)}")