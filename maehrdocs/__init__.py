"""
MaehrDocs - Automatisches Dokumentenmanagementsystem
Modularisierte Version mit verbesserter Struktur

Dieses Paket enthält alle Komponenten für das MaehrDocs System:
- Konfigurationsverwaltung
- Dokumentenverarbeitung
- Duplikaterkennung
- Grafische Benutzeroberfläche
"""

__version__ = '2.0.0'
__author__ = 'René Mähr'
__email__ = 'rene.maehr@web.de'

# Hauptklassen für einfachen Import
from .config import ConfigManager
from .document_processor import DocumentProcessor
from .duplicate_detector import DuplicateDetector

# Aliase für die GUI
from .gui import GuiApp

__all__ = [
    'ConfigManager',
    'DocumentProcessor',
    'DuplicateDetector',
    'GuiApp',
]