"""
Visueller Dokumentenvergleich für MaehrDocs
Stellt Funktionen zur visuellen Gegenüberstellung von Dokumenten bereit,
insbesondere für die Visualisierung von Duplikaterkennungen.
"""

import os
import logging
import datetime
import base64
from io import BytesIO

def generate_visual_comparison(visual_file, duplicate_file, original_file, config, logger=None):
    """
    Generiert einen visuellen Vergleich der Duplikatdateien.
    
    Diese Funktion erstellt eine HTML-Datei mit einem visuellen Vergleich
    der ersten Seiten beider Dokumente nebeneinander, wenn möglich.
    
    Args:
        visual_file (str): Pfad zur zu erstellenden HTML-Vergleichsdatei
        duplicate_file (str): Pfad zur Duplikatdatei
        original_file (str): Pfad zur Originaldatei
        config (dict): Die Anwendungskonfiguration
        logger: Logger-Instanz für die Protokollierung
    """
    # Logger initialisieren, falls nicht übergeben
    if logger is None:
        logger = logging.getLogger(__name__)
        
    try:
        # Prüfen, ob die benötigten Module verfügbar sind
        try:
            import fitz  # PyMuPDF
            from PIL import Image
        except ImportError as e:
            logger.warning(f"Modul für visuellen Vergleich nicht verfügbar: {str(e)}")
            return
        
        # Bilder der ersten Seiten extrahieren
        orig_img = _extract_first_page_image(original_file)
        dup_img = _extract_first_page_image(duplicate_file)
        
        # HTML-Datei mit Bildern erstellen
        with open(visual_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visueller Dokumentenvergleich</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
            text-align: center;
        }
        .comparison-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .document {
            flex: 1;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin: 0 10px;
            text-align: center;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <h1>Visueller Dokumentenvergleich</h1>
    <p style="text-align: center;">Erstellt am: """)
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            f.write("""</p>
    
    <div class="comparison-container">
        <div class="document">
            <h2>Original-Datei</h2>
            <p>""")
            f.write(os.path.basename(original_file))
            f.write("""</p>
            """)
            if orig_img:
                f.write(f'<img src="data:image/png;base64,{orig_img}" alt="Erste Seite des Originals">')
            else:
                f.write('<p>Vorschau nicht verfügbar</p>')
            f.write("""
        </div>
        
        <div class="document">
            <h2>Duplikat-Datei</h2>
            <p>""")
            f.write(os.path.basename(duplicate_file))
            f.write("""</p>
            """)
            if dup_img:
                f.write(f'<img src="data:image/png;base64,{dup_img}" alt="Erste Seite des Duplikats">')
            else:
                f.write('<p>Vorschau nicht verfügbar</p>')
            f.write("""
        </div>
    </div>
</body>
</html>""")
        
        logger.info(f"Visueller Vergleich erstellt: {visual_file}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Erstellung des visuellen Vergleichs: {str(e)}")

def _extract_first_page_image(pdf_path):
    """
    Extrahiert das Bild der ersten Seite eines PDF-Dokuments.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        
    Returns:
        str: Base64-codiertes Bild oder None bei Fehler
    """
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        
        doc = fitz.open(pdf_path)
        if len(doc) > 0:
            # Erste Seite rendern
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Höhere Auflösung
            
            # In ein PIL-Image konvertieren
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # In Base64 konvertieren für HTML-Einbettung
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return img_str
        return None
    except Exception:
        return None