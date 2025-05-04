class DuplicateDetector:
    def __init__(self):
        # Deutsche Stopwörter definieren
        self.STOPWORDS = {'der', 'die', 'das', 'und', 'mit', 'von', 'für', 'ist', 'ein', 'eine'}

    def calculate_similarity(self, text1, text2):
        """Berechnet die Textähnlichkeit zwischen zwei Dokumenten"""
        # Texte in Wörter aufteilen
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))

        # Leere Texte vermeiden
        if not words1 or not words2:
            return 0.0

        # Gemeinsame Wörter zählen
        common_words = words1.intersection(words2)

        # Jaccard-Ähnlichkeit berechnen
        similarity = len(common_words) / (len(words1) + len(words2) - len(common_words))
        return similarity

    def _tokenize(self, text):
        """Text in Wörter aufteilen und bereinigen"""
        if not text:
            return []

        # Alles klein schreiben und Sonderzeichen entfernen
        text = text.lower()
        import re

        # Nur Wörter mit mind. 3 Buchstaben behalten und Stopwörter entfernen
        words = [w for w in re.findall(r'\b[a-z]{3,}\b', text) if w not in self.STOPWORDS]
        return words