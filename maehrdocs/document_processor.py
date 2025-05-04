import os
import logging
import fitz  # PyMuPDF
import json
import shutil
import openai
from dotenv import load_dotenv

# Lokale Module importieren
from .duplicate_detector import DuplicateDetector

class DocumentProcessor:
    def __init__(self, config_manager):
        """Initialisiert den DocumentProcessor mit einer Konfiguration"""
        self.config = config_manager.get_config()
        self.duplicate_detector = DuplicateDetector()
        
        # OpenAI API-Key aus .env-Datei laden
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Logging konfigurieren
        self.logger = logging.getLogger(__name__)
    
    def process_document(self, file_path, dry_run=False, force=False):
        """Verarbeitet ein einzelnes Dokument"""
        try:
            # Prüfe, ob die Datei existiert und eine PDF ist
            if not os.path.exists(file_path) or not file_path.lower().endswith('.pdf'):
                self.logger.error(f"Datei existiert nicht oder ist keine PDF: {file_path}")
                return None
            
            # Dateigröße prüfen
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > self.config['document_processing']['max_file_size_mb']:
                self.logger.warning(f"Datei zu groß ({file_size_mb:.2f} MB): {file_path}")
                return None
            
            # Text aus PDF extrahieren
            text = self._extract_text_from_pdf(file_path)
            if not text:
                self.logger.error(f"Konnte keinen Text aus der PDF extrahieren: {file_path}")
                return None
            
            # OpenAI-API verwenden, um Metadaten zu extrahieren
            doc_info = self._analyze_document_with_ai(text)
            if not doc_info:
                self.logger.error(f"Fehler bei der KI-Analyse des Dokuments: {file_path}")
                return None
            
            # Prüfe, ob das Dokument ein Duplikat ist
            is_duplicate, duplicate_path = self._check_for_duplicates(text, file_path)
            
            # Erzeuge einen neuen Dateinamen basierend auf den extrahierten Informationen
            new_filename = self._generate_filename(doc_info)
            if not new_filename:
                self.logger.error(f"Konnte keinen gültigen Dateinamen generieren: {file_path}")
                return None
            
            # Ergebnisbericht erstellen
            result = {
                "original_file": file_path,
                "extracted_info": doc_info,
                "new_filename": new_filename,
                "is_duplicate": is_duplicate,
                "duplicate_path": duplicate_path if is_duplicate else None
            }
            
            # Wenn nicht im Simulationsmodus, führe die Dateioperationen aus
            if not dry_run:
                self._move_and_rename_file(file_path, new_filename, is_duplicate, force)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung von {file_path}: {str(e)}")
            return None
    
    def _extract_text_from_pdf(self, file_path):
        """Extrahiert Text aus einer PDF-Datei"""
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren des Textes aus {file_path}: {str(e)}")
            return None
    
    def _analyze_document_with_ai(self, text):
        """Analysiert den Dokumenttext mit OpenAI API"""
        prompt = f"""Analysiere folgendes Dokument und extrahiere:
1. Absender (Firma/Person, die das Dokument erstellt hat)
2. Datum (im Format YYYY-MM-DD)
3. Dokumenttyp (einer der folgenden: {', '.join(self.config['valid_doc_types'])})
4. Betreff/Titel (kurz und prägnant)
5. Wichtige Kennzahlen (z.B. Rechnungsbetrag, Vertragsnummer)

Gib deine Antwort als JSON-Objekt mit den Schlüsseln 'absender', 'datum', 'dokumenttyp', 'betreff' und 'kennzahlen' zurück.

Dokumenttext:
{text[:3000]}"""  # Begrenze die Textlänge
        
        max_retries = self.config['openai']['max_retries']
        
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.config['openai']['model'],
                    temperature=self.config['openai']['temperature'],
                    messages=[{"role": "system", "content": "Du bist ein Experte für Dokumentenanalyse."},
                             {"role": "user", "content": prompt}]
                )
                
                result_text = response.choices[0].message.content
                
                # Versuche, das Ergebnis als JSON zu parsen
                try:
                    doc_info = json.loads(result_text)
                    return doc_info
                except json.JSONDecodeError:
                    self.logger.warning(f"Konnte die API-Antwort nicht als JSON parsen. Versuch {attempt+1}/{max_retries}")
                    continue
                    
            except Exception as e:
                self.logger.warning(f"OpenAI API-Fehler: {str(e)}. Versuch {attempt+1}/{max_retries}")
                if attempt == max_retries - 1:
                    self.logger.error("Maximale Anzahl an Versuchen erreicht.")
                    return None
        
        return None
    
    def _check_for_duplicates(self, text, file_path):
        """Prüft, ob ein ähnliches Dokument bereits existiert"""
        output_dir = self.config['paths']['output_dir']
        
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    existing_file_path = os.path.join(root, file)
                    
                    # Prüfe, ob es die gleiche Datei ist
                    if os.path.samefile(file_path, existing_file_path):
                        continue
                    
                    # Extrahiere Text aus der bestehenden Datei
                    existing_text = self._extract_text_from_pdf(existing_file_path)
                    
                    if existing_text:
                        # Berechne Ähnlichkeit
                        similarity = self.duplicate_detector.calculate_similarity(text, existing_text)
                        
                        if similarity >= self.config['document_processing']['similarity_threshold']:
                            self.logger.info(f"Duplikat gefunden: {file_path} ist ähnlich zu {existing_file_path} (Ähnlichkeit: {similarity:.2f})")
                            return True, existing_file_path
        
        return False, None
    
    def _generate_filename(self, doc_info):
        """Generiert einen standardisierten Dateinamen basierend auf den extrahierten Informationen"""
        try:
            # Validiere und formatiere das Datum
            date_str = doc_info.get('datum', '')
            if date_str and len(date_str) >= 10:  # YYYY-MM-DD hat 10 Zeichen
                date_str = date_str[:10]  # Schneide auf YYYY-MM-DD
            else:
                date_str = "0000-00-00"  # Fallback
            
            # Validiere und formatiere den Dokumenttyp
            doc_type = doc_info.get('dokumenttyp', '').lower()
            if doc_type not in self.config['valid_doc_types']:
                doc_type = "dokument"  # Fallback
            
            # Formatiere den Absender
            sender = doc_info.get('absender', '').strip()
            if not sender:
                sender = "unbekannt"
            
            # Formatiere den Betreff
            subject = doc_info.get('betreff', '').strip()
            if not subject:
                subject = "ohne_betreff"
            
            # Ersetze ungültige Zeichen im Dateinamen
            for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                sender = sender.replace(char, '_')
                subject = subject.replace(char, '_')
            
            # Generiere den Dateinamen im Format YYYY-MM-DD_Dokumenttyp_Absender_Betreff.pdf
            filename = f"{date_str}_{doc_type}_{sender}_{subject}.pdf"
            
            # Begrenze die Länge des Dateinamens
            if len(filename) > 240:  # Wegen Pfadlängenbeschränkungen
                filename = filename[:240] + ".pdf"
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Generierung des Dateinamens: {str(e)}")
            return None
    
    def _move_and_rename_file(self, file_path, new_filename, is_duplicate, force=False):
        """Verschiebt und benennt die Datei basierend auf dem Analyseergebnis"""
        try:
            if is_duplicate and not force:
                # Verschiebe die Datei in den Papierkorb
                dest_path = os.path.join(self.config['paths']['trash_dir'], os.path.basename(file_path))
                self.logger.info(f"Verschiebe Duplikat nach: {dest_path}")
                shutil.move(file_path, dest_path)
            else:
                # Verschiebe die Datei in den Ausgabeordner mit neuem Namen
                dest_path = os.path.join(self.config['paths']['output_dir'], new_filename)
                
                # Prüfe, ob die Zieldatei bereits existiert
                if os.path.exists(dest_path) and not force:
                    # Füge eine Nummer hinzu, um Konflikte zu vermeiden
                    base, ext = os.path.splitext(new_filename)
                    counter = 1
                    while os.path.exists(os.path.join(self.config['paths']['output_dir'], f"{base}_{counter}{ext}")):
                        counter += 1
                    dest_path = os.path.join(self.config['paths']['output_dir'], f"{base}_{counter}{ext}")
                
                self.logger.info(f"Verschiebe Datei nach: {dest_path}")
                shutil.move(file_path, dest_path)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verschieben der Datei: {str(e)}")
            return False
    
    def process_all_documents(self, dry_run=False, force=False):
        """Verarbeitet alle PDF-Dokumente im Eingangsordner"""
        input_dir = self.config['paths']['input_dir']
        results = []
        
        # Stelle sicher, dass alle erforderlichen Verzeichnisse existieren
        for dir_path in [input_dir, self.config['paths']['output_dir'], self.config['paths']['trash_dir']]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Verarbeite alle PDF-Dateien im Eingangsordner
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(input_dir, filename)
                result = self.process_document(file_path, dry_run, force)
                if result:
                    results.append(result)
                    self.logger.info(f"Dokument verarbeitet: {filename} → {result['new_filename']}")
        
        return results