"""
Dateinamengenerator für MaehrDocs
Generiert standardisierte Dateinamen basierend auf extrahierten Dokumentinformationen.

Dieses Modul implementiert die Logik zur Erzeugung konsistenter, strukturierter Dateinamen
für verarbeitete Dokumente auf Basis der durch die KI-Analyse extrahierten Metadaten.
Es sorgt für einheitliche Benennung und bessere Auffindbarkeit der Dokumente.
"""

import os
import re
import logging
from datetime import datetime

class FilenameGenerator:
    """
    Klasse zur Generierung standardisierter Dateinamen für verarbeitete Dokumente.
    
    Diese Klasse ist verantwortlich für:
    - Formatierung von Datumsangaben in ein einheitliches Format
    - Validierung und Normalisierung von Dokumenttypen
    - Bereinigung von Absender- und Betreffsinformationen
    - Zusammenstellung der Informationen zu einem strukturierten Dateinamen
    
    Der generierte Dateiname folgt dem Schema:
    YYYY-MM-DD_Dokumenttyp_Absender_Betreff.pdf
    """
    
    def __init__(self, config):
        """
        Initialisiert den FilenameGenerator mit der Anwendungskonfiguration.
        
        Richtet Logging ein und initialisiert Parameter für die Dateinamensgenerierung,
        einschließlich ungültiger Zeichen und Längenbeschränkungen.
        
        Args:
            config (dict): Konfigurationsdaten mit gültigen Dokumenttypen
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Ungültige Zeichen für Dateinamen
        self.invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        
        # Maximale Länge für Dateinamen (für Dateisystembeschränkungen)
        self.max_filename_length = 240
    
    def generate_filename(self, doc_info):
        """
        Generiert einen standardisierten Dateinamen basierend auf den extrahierten Informationen.
        
        Verarbeitet die von der KI-Analyse extrahierten Dokumentinformationen und
        erstellt daraus einen konsistenten, strukturierten Dateinamen nach dem
        definierten Schema: YYYY-MM-DD_Dokumenttyp_Absender_Betreff.pdf
        
        Args:
            doc_info (dict): Extrahierte Dokumentinformationen (Datum, Typ, Absender, Betreff)
            
        Returns:
            str: Generierter Dateiname oder None bei Fehler
        """
        try:
            # Validiere und formatiere das Datum
            date_str = self._format_date(doc_info.get('datum', ''))
            
            # Validiere und formatiere den Dokumenttyp
            doc_type = self._format_document_type(doc_info.get('dokumenttyp', ''))
            
            # Formatiere den Absender
            sender = self._format_sender(doc_info.get('absender', ''))
            
            # Formatiere den Betreff
            subject = self._format_subject(doc_info.get('betreff', ''))
            
            # Generiere den Dateinamen im Format YYYY-MM-DD_Dokumenttyp_Absender_Betreff.pdf
            filename = f"{date_str}_{doc_type}_{sender}_{subject}.pdf"
            
            # Begrenze die Länge des Dateinamens
            if len(filename) > self.max_filename_length:
                base, ext = os.path.splitext(filename)
                filename = base[:self.max_filename_length - len(ext)] + ext
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Generierung des Dateinamens: {str(e)}")
            return None
    
    def _format_date(self, date_str):
        """
        Formatiert ein Datum im einheitlichen Format YYYY-MM-DD.
        
        Konvertiert verschiedene Datumsformate (DD.MM.YYYY, YYYY/MM/DD, etc.)
        in das standardisierte Format YYYY-MM-DD und behandelt unvollständige
        oder ungültige Datumsangaben, indem das aktuelle Datum als Fallback 
        verwendet wird.
        
        Args:
            date_str (str): Zu formatierendes Datum aus der Dokumentenanalyse
            
        Returns:
            str: Formatiertes Datum im Format YYYY-MM-DD
        """
        # Versuche, das Datum zu extrahieren und zu validieren
        try:
            # Wenn das Datum bereits im Format YYYY-MM-DD vorliegt
            if re.match(r'^\d{4}-\d{2}-\d{2}', date_str):
                return date_str[:10]  # Schneide auf YYYY-MM-DD
                
            # Versuche, das Datum im Format DD.MM.YYYY zu parsen
            elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}', date_str):
                day, month, year = map(int, date_str.split('.')[:3])
                return f"{year:04d}-{month:02d}-{day:02d}"
                
            # Versuche, andere gängige Datumsformate zu parsen
            else:
                for fmt in ["%d.%m.%Y", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                        
            # Wenn kein passendes Format gefunden wurde, verwende das aktuelle Datum
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception as e:
            self.logger.warning(f"Fehler beim Formatieren des Datums '{date_str}': {str(e)}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def _format_document_type(self, doc_type):
        """
        Formatiert und validiert den Dokumenttyp gegen die Liste gültiger Typen.
        
        Normalisiert den Dokumenttyp und prüft, ob er in der konfigurierten Liste
        gültiger Dokumenttypen enthalten ist. Versucht auch, ähnliche Dokumenttypen
        zu finden, falls kein exakter Treffer vorliegt.
        
        Args:
            doc_type (str): Zu formatierender Dokumenttyp aus der Dokumentenanalyse
            
        Returns:
            str: Formatierter und validierter Dokumenttyp oder "dokument" als Fallback
        """
        # Normalisiere den Dokumenttyp (Kleinbuchstaben, Leerzeichen entfernen)
        doc_type = doc_type.lower().strip()
        
        # Prüfe, ob der Dokumenttyp gültig ist
        valid_doc_types = self.config.get('document_processing', {}).get('valid_doc_types', [])
        
        if doc_type in valid_doc_types:
            return doc_type
        
        # Versuche, ähnliche Dokumenttypen zu finden
        for valid_type in valid_doc_types:
            if valid_type in doc_type or doc_type in valid_type:
                return valid_type
        
        # Fallback
        return "dokument"
    
    def _format_sender(self, sender):
        """
        Formatiert den Absender für die Verwendung im Dateinamen.
        
        Entfernt ungültige Zeichen aus dem Absender, begrenzt die Länge
        und ersetzt Leerzeichen durch Unterstriche, um einen gültigen
        Dateinamensteil zu erzeugen.
        
        Args:
            sender (str): Zu formatierender Absender aus der Dokumentenanalyse
            
        Returns:
            str: Formatierter Absender oder "unbekannt" als Fallback
        """
        if not sender or not sender.strip():
            return "unbekannt"
        
        # Normalisiere den Absender
        sender = sender.strip()
        
        # Ersetze ungültige Zeichen
        for char in self.invalid_chars:
            sender = sender.replace(char, '_')
        
        # Entferne doppelte Unterstriche
        sender = re.sub(r'_{2,}', '_', sender)
        
        # Begrenze die Länge
        if len(sender) > 50:
            sender = sender[:50]
        
        return sender
    
    def _format_subject(self, subject):
        """
        Formatiert den Betreff für die Verwendung im Dateinamen.
        
        Entfernt ungültige Zeichen aus dem Betreff, begrenzt die Länge
        und ersetzt Leerzeichen durch Unterstriche, um einen gültigen
        Dateinamensteil zu erzeugen.
        
        Args:
            subject (str): Zu formatierender Betreff aus der Dokumentenanalyse
            
        Returns:
            str: Formatierter Betreff oder "ohne_betreff" als Fallback
        """
        if not subject or not subject.strip():
            return "ohne_betreff"
        
        # Normalisiere den Betreff
        subject = subject.strip()
        
        # Ersetze ungültige Zeichen
        for char in self.invalid_chars:
            subject = subject.replace(char, '_')
        
        # Entferne doppelte Unterstriche
        subject = re.sub(r'_{2,}', '_', subject)
        
        # Begrenze die Länge
        if len(subject) > 100:
            subject = subject[:100]
        
        return subject