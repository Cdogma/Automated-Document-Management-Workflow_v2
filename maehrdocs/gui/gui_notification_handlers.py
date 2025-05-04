"""
Benachrichtigungshandler für MaehrDocs
Enthält Funktionen zur Verarbeitung von speziellen Benachrichtigungen
"""

def handle_duplicate_from_log(app, log_line):
    """
    Verarbeitet Duplikatbenachrichtigungen aus der Protokollausgabe
    
    Args:
        app: Instanz der GuiApp
        log_line: Log-Zeile mit Duplikatinformationen
    """
    try:
        # Aus dem Log-Text die relevanten Informationen extrahieren
        # Format könnte sein: "DUPLICATE DETECTED: [Original: file1.pdf] [Duplicate: file2.pdf] [Similarity: 0.92]"
        if "[Original:" in log_line and "[Duplicate:" in log_line and "[Similarity:" in log_line:
            # Original-Datei extrahieren
            original_start = log_line.find("[Original:") + 10
            original_end = log_line.find("]", original_start)
            original_file = log_line[original_start:original_end].strip()
            
            # Duplikat-Datei extrahieren
            duplicate_start = log_line.find("[Duplicate:") + 11
            duplicate_end = log_line.find("]", duplicate_start)
            duplicate_file = log_line[duplicate_start:duplicate_end].strip()
            
            # Ähnlichkeitswert extrahieren
            similarity_start = log_line.find("[Similarity:") + 12
            similarity_end = log_line.find("]", similarity_start)
            similarity_str = log_line[similarity_start:similarity_end].strip()
            similarity_score = float(similarity_str)
            
            # Popup anzeigen, wenn aktiviert
            if app.config.get("gui", {}).get("show_duplicate_popup", True):
                from .gui_document_viewer import show_duplicate_alert
                show_duplicate_alert(app, original_file, duplicate_file, similarity_score)
    except Exception as e:
        app.log(f"Fehler bei der Verarbeitung der Duplikatbenachrichtigung: {str(e)}", level="error")