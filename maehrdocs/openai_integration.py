"""
OpenAI-Integration für MaehrDocs
Verwaltet die Interaktion mit der OpenAI API
"""

import os
import json
import logging
import openai
from dotenv import load_dotenv

class OpenAIIntegration:
    """
    Klasse zur Interaktion mit der OpenAI API
    """
    
    def __init__(self, config):
        """
        Initialisiert die OpenAI-Integration
        
        Args:
            config (dict): Konfigurationsdaten mit OpenAI-Einstellungen
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
        Analysiert einen Dokumenttext mit der OpenAI API
        
        Args:
            text (str): Zu analysierender Text
            valid_doc_types (list): Liste gültiger Dokumenttypen
            
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
        Erstellt den Prompt für die Dokumentanalyse
        
        Args:
            text (str): Zu analysierender Text
            valid_doc_types (list): Liste gültiger Dokumenttypen
            
        Returns:
            str: Formatierter Prompt
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
        Ruft die OpenAI API auf
        
        Args:
            prompt (str): Prompt für die API
            
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
        Parst die JSON-Antwort der API
        
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