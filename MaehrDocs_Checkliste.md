
# ✅ MaehrDocs – Verarbeitungs-Checkliste

## Ablauf bei Ankunft einer neuen PDF in `01_InboxDocs`

1. 📥 **Datei erkannt**
   - Wird regelmäßig auf neue PDFs geprüft

2. ✅ **Vorverarbeitung**
   - Prüfung auf gültiges PDF
   - OCR, Seitenzahl, Größe
   - ggf. in „Processed“-Ordner verschieben

3. 🧠 **GPT-Analyse**
   - Extraktion: Datum, Typ, Absender, Betreff, Betrag, Rechnungsnummer
   - Klassifikation: `art` (business, privat, bar)
   - Brutto/Netto/MwSt/Steuersatz

4. 🔍 **Duplikaterkennung**
   - Vergleich mit Zielordnern & Historie

5. 🧾 **Dateiname generieren**
   - Nach YAML-Regeln mit Kürzung, Groß-/Kleinschreibung, Formatierung

6. 📂 **Ablage**
   - In `02_FinalDocs`
   - Zusätzlich in Monatsordner `05_Archive_Rechnungen` (wenn business oder bar)

7. 📊 **Excel-Eintrag**
   - Mit allen Feldern (Datum, Betrag, Link, Status, etc.)

8. 💶 **Zahlungsabgleich (optional)**
   - Abgleich mit Bank-CSV
   - Update: Bezahlt = Ja/Nein

9. 📤 **Lexware-Upload (optional)**
   - Automatisch via API
   - Status im Excel aktualisieren

10. 🗄️ **Archivierung (optional)**
    - Monats-ZIP der PDFs
    - Export Excel als PDF

11. 📈 **GUI-Anzeige (optional)**
    - Filterfunktion, Suche, Vorschau, Datei-Öffnung
