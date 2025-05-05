"""
Duplikaterkennung für MaehrDocs
Enthält die DuplicateDetector-Klasse zur Erkennung von ähnlichen Dokumenten
mittels Textvergleich und Jaccard-Ähnlichkeit mit optimierter Verarbeitung für deutsche Texte.
"""

class DuplicateDetector:
    """
    Klasse zur Erkennung von Dokumentduplikaten durch intelligenten Textvergleich.
    
    Verwendet eine Kombination aus:
    - Tokenisierung mit Entfernung deutscher Stopwörter
    - Bereinigung von unwichtigen Textbestandteilen
    - Jaccard-Ähnlichkeitskoeffizient für präzisen Vergleich
    
    Die Ähnlichkeitsbewertung berücksichtigt den inhaltlichen Kern von Dokumenten
    und reduziert den Einfluss von Formatierungen und Standardphrasen.
    """
    def __init__(self):
        # Erweiterte Liste deutscher Stopwörter für eine bessere Filterung
        self.STOPWORDS = {
            'der', 'die', 'das', 'und', 'mit', 'von', 'für', 'ist', 'ein', 'eine',
            'in', 'zu', 'den', 'dem', 'des', 'auf', 'als', 'nach', 'bei', 'an',
            'im', 'um', 'aus', 'über', 'vor', 'zum', 'zur', 'durch', 'wegen',
            'aber', 'oder', 'wenn', 'weil', 'dass', 'daß', 'denn', 'bis', 'wie',
            'so', 'nur', 'noch', 'schon', 'auch', 'alle', 'jede', 'jeder', 'jedes',
            'am', 'einem', 'einen', 'einer', 'eines', 'wird', 'werden', 'wurde',
            'wurden', 'haben', 'hat', 'hatte', 'hatten', 'sein', 'sind', 'war',
            'waren', 'nicht', 'sehr', 'ihr', 'ihre', 'seinen', 'seiner', 'ihrem'
        }

    def calculate_similarity(self, text1, text2):
        """
        Berechnet die Textähnlichkeit zwischen zwei Dokumenten mittels Jaccard-Ähnlichkeit.
        
        Der Algorithmus transformiert beide Texte in Wortmengen, entfernt dabei Stopwörter
        und berechnet das Verhältnis der gemeinsamen Wörter zur Gesamtwortzahl.
        
        Args:
            text1 (str): Text des ersten Dokuments
            text2 (str): Text des zweiten Dokuments
            
        Returns:
            float: Ähnlichkeitswert zwischen 0 (keine Ähnlichkeit) und 1 (identisch)
        """
        # Text in Wörter aufteilen
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))

        # Leere Texte vermeiden
        if not words1 or not words2:
            return 0.0

        # Gemeinsame Wörter zählen
        common_words = words1.intersection(words2)

        # Jaccard-Ähnlichkeit berechnen:
        # J(A,B) = |A ∩ B| / |A ∪ B| = |A ∩ B| / (|A| + |B| - |A ∩ B|)
        similarity = len(common_words) / (len(words1) + len(words2) - len(common_words))
        return similarity

    def _tokenize(self, text):
        """
        Teilt einen Text in Wörter auf und bereinigt diese für den Vergleich.
        
        Der Prozess umfasst:
        1. Konvertierung in Kleinbuchstaben
        2. Extraktion von Wörtern mit regulärem Ausdruck
        3. Filterung von Stopwörtern
        4. Entfernung von Wörtern mit weniger als 3 Buchstaben
        
        Dies erhöht die Genauigkeit des Vergleichs, da unwichtige oder 
        sehr häufige Wörter den Ähnlichkeitswert nicht verzerren.
        
        Args:
            text (str): Der zu verarbeitende Text
            
        Returns:
            list: Liste der bereinigten, relevanten Wörter
        """
        if not text:
            return []

        # Alles klein schreiben
        text = text.lower()
        
        # Regular Expression für die Wortextraktion importieren
        import re

        # Wörter extrahieren, filtern und bereinigen:
        # - Nur Wörter mit mind. 3 Buchstaben behalten
        # - Stopwörter entfernen
        words = [w for w in re.findall(r'\b[a-z]{3,}\b', text) if w not in self.STOPWORDS]
        return words