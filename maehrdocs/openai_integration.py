"""
OpenAI-Integration für MaehrDocs
Implementiert die Integration mit der OpenAI API für die Analyse von Dokumenteninhalten.

Dieses Modul kapselt alle Interaktionen mit der OpenAI API und bietet robuste
Fehlerbehandlung, Wiederholungslogik und strukturierte Antwortverarbeitung.
Es ist ein zentraler Bestandteil der KI-gestützten Dokumentenverarbeitung.
"""

import os
import json
import logging
import random
from datetime import datetime
from pathlib import Path

# Versuche, das OpenAI-Modul zu importieren, aber erlaube auch Ausführung ohne
try:
    import openai
    from dotenv import load_dotenv
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OpenAIIntegration:
    """
    Klasse zur Interaktion mit der OpenAI API.
    
    Diese Klasse ist verantwortlich für:
    - Konfiguration und Initialisierung der OpenAI API-Verbindung
    - Formulierung von Prompts zur Dokumentenanalyse
    - Verarbeitung von API-Antworten und Konvertierung in strukturierte Daten
    - Fehlerbehandlung und automatische Wiederholungsversuche
    
    Die Integration verwendet primär das ChatCompletion-Feature der API,
    um intelligente Dokumentenanalyse durchzuführen.
    """
    
    def __init__(self, config):
        """
        Initialisiert die OpenAI-Integration mit Konfiguration und API-Schlüssel.
        
        Lädt den API-Schlüssel aus der .env-Datei und konfiguriert die
        OpenAI-Client-Bibliothek mit den übergebenen Einstellungen.
        
        Args:
            config (dict): Konfigurationsdaten mit OpenAI-Einstellungen (Modell, Temperatur, etc.)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.api_key_valid = False
        self.test_mode = True
        
        # Nur fortfahren, wenn OpenAI importiert werden konnte
        if OPENAI_AVAILABLE:
            # OpenAI API-Key aus .env-Datei laden
            try:
                load_dotenv()
                api_key = os.getenv("OPENAI_API_KEY")
                
                # API-Schlüssel aus Konfiguration verwenden, wenn in .env nicht gefunden
                if not api_key and 'openai' in config and 'api_key' in config['openai']:
                    api_key = config['openai']['api_key']
                    self.logger.info("API-Schlüssel aus Konfiguration geladen")
                
                # Prüfen, ob der API-Key gesetzt ist
                if not api_key:
                    self.logger.warning("OpenAI API-Key nicht gefunden. Wechsle in Testmodus.")
                    self.test_mode = True
                else:
                    try:
                        # Client initialisieren
                        self.client = openai.OpenAI(api_key=api_key)
                        # Wir setzen den Test-Modus erstmal auf False - wenn der erste API-Aufruf
                        # fehlschlägt, wird er wieder auf True gesetzt
                        self.test_mode = False
                        self.api_key_valid = True
                        self.logger.info("OpenAI API erfolgreich initialisiert")
                    except Exception as e:
                        self.logger.error(f"Fehler bei der Initialisierung der OpenAI API: {str(e)}")
                        self.test_mode = True
            except Exception as e:
                self.logger.error(f"Fehler beim Laden des API-Schlüssels: {str(e)}")
                self.test_mode = True
        else:
            self.logger.warning("OpenAI-Bibliothek nicht installiert. Wechsle in Testmodus.")
            self.test_mode = True
        
        # Ausgabe des aktuellen Modus
        if self.test_mode:
            self.logger.info("OpenAI-Integration läuft im TESTMODUS (simulierte Antworten)")
        else:
            self.logger.info("OpenAI-Integration läuft im ONLINE-MODUS")
    
    def analyze_document(self, text, valid_doc_types):
        """
        Analysiert einen Dokumenttext mit der OpenAI API.
        
        Sendet einen Teil des Dokumenttextes an die OpenAI API mit einem
        strukturierten Prompt zur Extraktion von Dokumentmetadaten wie
        Absender, Datum, Dokumenttyp und Betreff.
        
        Args:
            text (str): Zu analysierender Dokumenttext
            valid_doc_types (list): Liste gültiger Dokumenttypen zur Kategorisierung
            
        Returns:
            dict: Extrahierte Dokumentinformationen oder None bei Fehler
        """
        # Im Testmodus simulierte Daten zurückgeben
        if self.test_mode:
            self.logger.info("Verwende Test-Modus für Dokumentenanalyse")
            return self._generate_test_document_info(text, valid_doc_types)
        
        # Begrenze die Textlänge für die API-Anfrage
        truncated_text = text[:3000] if text else ""
        
        if not truncated_text:
            self.logger.error("Kein Text zur Analyse vorhanden")
            return None
            
        prompt = self._create_analysis_prompt(truncated_text, valid_doc_types)
        max_retries = self.config.get('openai', {}).get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                response = self._call_openai_api(prompt)
                
                if response:
                    # Versuche, das Ergebnis als JSON zu parsen
                    doc_info = self._parse_json_response(response)
                    
                    if doc_info:
                        return doc_info
                    else:
                        self.logger.warning(f"Konnte die API-Antwort nicht als JSON parsen. Versuch {attempt+1}/{max_retries}")
                else:
                    # Wenn Antwort None ist, zu Test-Modus wechseln
                    self.logger.warning("API-Antwort ist leer. Wechsle in Test-Modus.")
                    self.test_mode = True
                    if attempt == max_retries - 1:
                        return self._generate_test_document_info(text, valid_doc_types)
                        
            except Exception as e:
                self.logger.error(f"Fehler beim Aufruf der OpenAI API: {str(e)}")
                # Nach Fehler direkt in Test-Modus wechseln
                self.test_mode = True
                
                if attempt == max_retries - 1:
                    self.logger.warning("Maximale Anzahl an Versuchen erreicht. Wechsle in Testmodus für dieses Dokument.")
                    return self._generate_test_document_info(text, valid_doc_types)
        
        # Wenn alle Versuche fehlschlagen, Test-Daten zurückgeben
        self.test_mode = True
        return self._generate_test_document_info(text, valid_doc_types)
    
    def _generate_test_document_info(self, text, valid_doc_types):
        """
        Generiert simulierte Dokumentinformationen für den Testmodus.
        
        Extrahiert einfache Muster aus dem Text wie Datumsangaben und generiert
        plausible Werte für Absender, Dokumenttyp, Betreff usw.
        
        Args:
            text (str): Der Dokumenttext
            valid_doc_types (list): Liste gültiger Dokumenttypen
            
        Returns:
            dict: Generierte Dokumentinformationen
        """
        self.logger.info("Generiere Test-Dokumentinformationen")
        
        # Dateiname extrahieren, falls vorhanden
        filename = "Unbekanntes Dokument"
        if isinstance(text, str) and text.startswith("Dateiname:"):
            filename_end = text.find("\n")
            if filename_end > 0:
                filename = text[10:filename_end].strip()
        
        # Einfache Datum-Suche
        date_str = datetime.now().strftime("%Y-%m-%d")
        import re
        date_patterns = [
            r'(\d{2})\.(\d{2})\.(\d{4})',  # 01.01.2023
            r'(\d{4})-(\d{2})-(\d{2})'     # 2023-01-01
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text[:500])
            if matches:
                if '.' in pattern:  # DD.MM.YYYY
                    day, month, year = matches[0]
                    date_str = f"{year}-{month}-{day}"
                else:  # YYYY-MM-DD
                    date_str = '-'.join(matches[0])
                break
        
        # Zufälligen Dokumenttyp auswählen
        if valid_doc_types:
            doc_type = random.choice(valid_doc_types)
        else:
            doc_type = "dokument"
        
        # Kurzen Betreff aus Dateinamen generieren
        subject = Path(filename).stem if filename else "Dokument"
        
        # Test-Absender
        senders = ["Test GmbH", "Beispiel AG", "Muster Firma", "Max Mustermann"]
        sender = random.choice(senders)
        
        # Testdaten für Kennzahlen
        test_metrics = {
            "hinweis": "Testdaten (OpenAI nicht verfügbar)",
            "betrag": f"{random.randint(100, 10000)}.{random.randint(0, 99):02d} €"
        }
        
        return {
            "absender": sender,
            "datum": date_str,
            "dokumenttyp": doc_type,
            "betreff": subject,
            "kennzahlen": test_metrics
        }
    
    def _create_analysis_prompt(self, text, valid_doc_types):
        """
        Erstellt den Prompt für die Dokumentenanalyse.
        
        Formuliert einen strukturierten Prompt für die OpenAI API, der
        spezifische Anweisungen zur Extraktion von Dokumentinformationen
        und das Format der gewünschten Antwort enthält.
        
        Args:
            text (str): Zu analysierender Dokumenttext
            valid_doc_types (list): Liste gültiger Dokumenttypen
            
        Returns:
            str: Formatierter Prompt für die API-Anfrage
        """
        return f"""Analysiere folgendes Dokument und extrahiere:
1. Absender (Firma/Person, die das Dokument erstellt hat)
2. Datum (im Format YYYY-MM-DD)
3. Dokumenttyp (einer der folgenden: {', '.join(valid_doc_types)})
4. Betreff/Titel (kurz und prägnant)
5. Wichtige Kennzahlen (z.B. Rechnungsbetrag, Vertragsnummer)

Gib deine Antwort als JSON-Objekt mit den Schlüsseln 'absender', 'datum', 'dokumenttyp', 'betreff' und 'kennzahlen' zurück.

Dokumenttext:
{text}"""
    
    def _call_openai_api(self, prompt):
        """
        Ruft die OpenAI API mit dem gegebenen Prompt auf.
        
        Konfiguriert die API-Anfrage basierend auf den Anwendungseinstellungen
        (Modell, Temperatur) und sendet den Prompt an die OpenAI API.
        
        Args:
            prompt (str): Der vollständige Prompt für die API
            
        Returns:
            str: API-Antworttext oder None bei Fehler
        """
        try:
            if self.test_mode or not self.api_key_valid:
                raise ValueError("API nicht verfügbar (Test-Modus aktiv)")
                
            model = self.config.get('openai', {}).get('model', 'gpt-3.5-turbo')
            temperature = self.config.get('openai', {}).get('temperature', 0.3)
            
            # Neue API-Aufrufsyntax
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Du bist ein Experte für Dokumentenanalyse."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aufruf der OpenAI API: {str(e)}")
            # Bei Fehler in Test-Modus wechseln
            self.test_mode = True
            return None
    
    def _parse_json_response(self, response_text):
        """
        Parst die JSON-Antwort der API in ein Python-Dictionary.
        
        Extrahiert den JSON-Teil aus der API-Antwort und wandelt ihn in eine
        strukturierte Python-Datenstruktur um. Berücksichtigt verschiedene
        Formate, in denen die API das JSON zurückliefern kann.
        
        Args:
            response_text (str): Antworttext der API
            
        Returns:
            dict: Geparste JSON-Daten oder None bei Fehler
        """
        try:
            # Versuche, das JSON zu extrahieren, falls es in Markdown-Code-Blöcken steht
            if "```json" in response_text and "```" in response_text:
                # Extrahiere den JSON-Teil
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text and "```" in response_text:
                # Extrahiere den Code-Block
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON-Parsing-Fehler: {str(e)}")
            self.logger.debug(f"Antworttext: {response_text}")
            return None