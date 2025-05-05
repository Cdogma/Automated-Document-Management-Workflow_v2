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
import openai
from dotenv import load_dotenv

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
        
        # OpenAI API-Key aus .env-Datei laden
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Prüfen, ob der API-Key gesetzt ist
        if not openai.api_key:
            self.logger.warning("OpenAI API-Key nicht gefunden. Bitte .env-Datei mit OPENAI_API_KEY erstellen.")
    
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
        # Begrenze die Textlänge für die API-Anfrage
        truncated_text = text[:3000] if text else ""
        
        if not truncated_text:
            self.logger.error("Kein Text zur Analyse vorhanden")
            return None
            
        prompt = self._create_analysis_prompt(truncated_text, valid_doc_types)
        max_retries = self.config['openai'].get('max_retries', 3)
        
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
                        
            except Exception as e:
                self.logger.warning(f"OpenAI API-Fehler: {str(e)}. Versuch {attempt+1}/{max_retries}")
                
                if attempt == max_retries - 1:
                    self.logger.error("Maximale Anzahl an Versuchen erreicht.")
        
        return None
    
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
            model = self.config['openai'].get('model', 'gpt-3.5-turbo')
            temperature = self.config['openai'].get('temperature', 0.3)
            
            response = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": "Du bist ein Experte für Dokumentenanalyse."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aufruf der OpenAI API: {str(e)}")
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