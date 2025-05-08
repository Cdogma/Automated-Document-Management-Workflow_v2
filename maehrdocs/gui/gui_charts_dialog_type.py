"""
Typ-Detail-Dialog für Charts in MaehrDocs
Enthält Funktionen zum Anzeigen von Details für ausgewählte Dokumenttypen.
"""

import tkinter as tk
import logging

def fill_type_detail(frame, data, app):
    """
    Füllt den Detail-Dialog für einen Dokumenttyp mit Inhalten.
    
    Args:
        frame: Das übergeordnete Frame
        data: Die anzuzeigenden Daten
        app: Die GuiApp-Instanz
    """
    try:
        type_name = data.get("type", "Unbekannt")
        count = data.get("count", 0)
        
        # Basisdaten anzeigen
        info_frame = tk.Frame(frame, bg=app.colors["card_background"])
        info_frame.pack(fill=tk.X, pady=10)
        
        # Typ-Icon (symbolisch)
        icon_label = tk.Label(
            info_frame,
            text="📄",  # Dokumentsymbol
            font=("Segoe UI", 36),
            bg=app.colors["card_background"],
            fg=app.colors["primary"]
        )
        icon_label.pack(side=tk.LEFT, padx=20)
        
        # Textinformationen
        text_frame = tk.Frame(info_frame, bg=app.colors["card_background"])
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Typ-Name
        tk.Label(
            text_frame,
            text=type_name,
            font=app.fonts["subheader"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Anzahl
        tk.Label(
            text_frame,
            text=f"Dokumente: {count}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"]
        ).pack(anchor=tk.W)
        
        # Beschreibung anzeigen
        if count > 0:
            beschreibung = get_type_description(type_name)
            
            # Beschreibungsrahmen
            desc_frame = tk.Frame(frame, bg=app.colors["background_medium"], padx=10, pady=10)
            desc_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                desc_frame,
                text="Beschreibung:",
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"]
            ).pack(anchor=tk.W)
            
            tk.Label(
                desc_frame,
                text=beschreibung,
                font=app.fonts["normal"],
                bg=app.colors["background_medium"],
                fg=app.colors["text_primary"],
                wraplength=460,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=5)
            
            # Tipps
            _show_type_tips(frame, type_name, app)
        else:
            # Keine Dokumente vorhanden
            tk.Label(
                frame,
                text="Keine Dokumente von diesem Typ vorhanden.",
                font=app.fonts["normal"],
                bg=app.colors["card_background"],
                fg=app.colors["warning"]
            ).pack(pady=20)
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Füllen des Typ-Detail-Dialogs: {str(e)}")
        
        # Fehleranzeige
        tk.Label(
            frame,
            text=f"Fehler beim Laden der Details: {str(e)}",
            font=app.fonts["normal"],
            bg=app.colors["card_background"],
            fg=app.colors["error"]
        ).pack(pady=20)

def get_type_description(type_name):
    """
    Gibt eine Beschreibung für einen Dokumenttyp zurück.
    
    Args:
        type_name: Name des Dokumenttyps
        
    Returns:
        str: Beschreibung des Dokumenttyps
    """
    # Standardbeschreibungen für gängige Dokumenttypen
    descriptions = {
        "Rechnung": "Eine Rechnung ist ein kaufmännisches Dokument, das die Forderung eines Verkäufers gegenüber dem Käufer über den Kaufpreis aus einem Kaufvertrag dokumentiert.",
        "Vertrag": "Ein Vertrag ist eine rechtlich bindende Vereinbarung zwischen zwei oder mehr Parteien.",
        "Brief": "Ein Brief ist ein schriftliches Dokument, das als Kommunikationsmittel zwischen Sender und Empfänger dient.",
        "Bescheid": "Ein Bescheid ist ein Verwaltungsakt einer Behörde, der rechtliche Wirkung entfaltet.",
        "Dokument": "Ein allgemeines Dokument, das Informationen in strukturierter Form enthält.",
        "Antrag": "Ein Antrag ist ein schriftliches Gesuch an eine Behörde oder Organisation.",
        "Meldung": "Eine Meldung ist eine offizielle Mitteilung oder Benachrichtigung."
    }
    
    # Fallback-Beschreibung
    return descriptions.get(
        type_name, 
        f"Keine spezifische Beschreibung für den Dokumenttyp '{type_name}' verfügbar."
    )

def _show_type_tips(frame, type_name, app):
    """
    Zeigt Tipps zur Verwendung des Dokumenttyps an.
    
    Args:
        frame: Container-Frame
        type_name: Name des Dokumenttyps
        app: GuiApp-Instanz
    """
    # Tipps-Titel
    tk.Label(
        frame,
        text="Tipps zur Verwendung:",
        font=app.fonts["normal"],
        bg=app.colors["card_background"],
        fg=app.colors["text_primary"]
    ).pack(anchor=tk.W, pady=(10, 5))
    
    # Standard-Tipps für alle Typen
    general_tips = [
        f"• Filterung: Nutzen Sie die Filteroptionen, um nur Dokumente vom Typ '{type_name}' anzuzeigen",
        f"• Sortierung: Dokumente vom Typ '{type_name}' können Sie im Dashboard nach Datum sortieren",
        f"• Archivierung: Bei {type_name}-Dokumenten empfiehlt sich eine regelmäßige Archivierung"
    ]
    
    # Spezifische Tipps basierend auf Dokumenttyp
    specific_tips = {
        "Rechnung": [
            "• Steuerrechtliche Aufbewahrung: Rechnungen müssen mindestens 10 Jahre aufbewahrt werden",
            "• Status-Tracking: Setzen Sie in der Excel-Tabelle den Status auf 'bezahlt', wenn die Rechnung beglichen ist"
        ],
        "Vertrag": [
            "• Ablaufdatum beachten: Prüfen Sie die Laufzeit und Kündigungsfristen",
            "• Änderungen dokumentieren: Nachträge sollten immer schriftlich festgehalten werden"
        ],
        "Bescheid": [
            "• Widerspruchsfrist: Beachten Sie die Fristen für eventuelle Widersprüche",
            "• Rechtsmittel: Bei Bedarf sollten Sie rechtliche Beratung in Anspruch nehmen"
        ]
    }
    
    # Zeige alle Tipps an
    all_tips = general_tips + specific_tips.get(type_name, [])
    
    for tip in all_tips:
        tk.Label(
            frame,
            text=tip,
            font=app.fonts["small"],
            bg=app.colors["card_background"],
            fg=app.colors["text_primary"],
            wraplength=460,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=2)