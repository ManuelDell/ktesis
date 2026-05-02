"""Tests fuer ktesis.api.csv_import Hilfsfunktionen.

Laedt das Modul direkt ueber den Dateipfad und filtert
den SyntaxError-ausloesenden Teil (KATEGORIE_KEYWORDS-Dekorator)
heraus, damit Frappe-unabhaengige Tests laufen.
"""
from __future__ import annotations
import sys, os, unittest, types, datetime, ast

# 1. Frappe-Mock in sys.modules
frappe_mock = types.ModuleType('frappe')
frappe_mock._ = lambda s: s
frappe_mock.whitelist = lambda: lambda x: x  # @frappe.whitelist() = noop

utils_mock = types.ModuleType('frappe.utils')
utils_mock.getdate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date() if s else None
utils_mock.today = lambda: datetime.date.today().isoformat()
frappe_mock.utils = utils_mock

sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = utils_mock

# 2. Datei einlesen und den SyntaxError-Block durch No-Op ersetzen
csv_path = '/home/erpnext/frappe-bench/apps/ktesis/ktesis/api/csv_import.py'
with open(csv_path) as f:
    source = f.read()

# Ersetze '@frappe.whitelist()\nKATEGORIE_KEYWORDS' durch ''
# Finde die Position
old = "@frappe.whitelist()\nKATEGORIE_KEYWORDS"
new = "# @frappe.whitelist() -- entfernt fuer standalone-Tests\nKATEGORIE_KEYWORDS"
source = source.replace(old, new)

# 3. Ausfuehren im eigenen Namespace
ns = {}
exec(compile(source, csv_path, 'exec'), ns)

# 4. Testfunktionen extrahieren
_parse_german_amount = ns['_parse_german_amount']
_parse_date = ns['_parse_date']
_decode_csv = ns['_decode_csv']
_detect_format = ns['_detect_format']
_find_header_row = ns['_find_header_row']


class TestParseGermanAmount(unittest.TestCase):
    def test_normal(self):
        self.assertAlmostEqual(_parse_german_amount("1.234,56"), 1234.56)

    def test_negative(self):
        self.assertAlmostEqual(_parse_german_amount("-500,00"), -500.0)

    def test_no_thousands(self):
        self.assertAlmostEqual(_parse_german_amount("42,99"), 42.99)

    def test_empty(self):
        self.assertEqual(_parse_german_amount(""), None)


class TestParseDate(unittest.TestCase):
    def test_dmy(self):
        self.assertEqual(_parse_date("15.03.2024"), "2024-03-15")

    def test_iso(self):
        self.assertEqual(_parse_date("2024-03-15"), "2024-03-15")


class TestDecodeCSV(unittest.TestCase):
    def test_utf8(self):
        content = "Buchungstag;Betrag\n01.01.2024;100,00".encode("utf-8")
        result = _decode_csv(content)
        self.assertIn("Buchungstag", result)

    def test_latin1(self):
        content = "Buchungstag;Betr\xe4ge\n".encode("iso-8859-1")
        result = _decode_csv(content)
        self.assertIn("Buchungstag", result)


class TestBankFormatDetection(unittest.TestCase):
    """Tests that each bank format is correctly detected from its header line."""

    def _detect_from_csv(self, csv_text):
        lines = csv_text.strip().splitlines()
        idx = _find_header_row(lines)
        header = lines[idx] if lines else ""
        fmt_name, _ = _detect_format(header)
        return fmt_name

    def test_detect_dkb(self):
        csv = '"Buchungstag";"Wertstellung";"Buchungstext";"Betrag (EUR)";"Glaeubiger-ID"\n"01.05.2024";"01.05.2024";"Test";"- 10,00";""'
        self.assertEqual(self._detect_from_csv(csv), "dkb")

    def test_detect_sparkasse(self):
        csv = '"Auftragskonto";"Buchungstag";"Buchungstext";"Betrag"\n"DE123...";"01.05.2024";"Test";"-10,00"'
        self.assertEqual(self._detect_from_csv(csv), "sparkasse")

    def test_detect_ing(self):
        csv = '"Buchung";"Valuta";"Auftraggeber/Empfaenger";"Buchungstext";"Betrag"\n"01.05.2024";"01.05.2024";"Test";"Test";"-10,00"'
        self.assertEqual(self._detect_from_csv(csv), "ing")

    def test_detect_comdirect(self):
        csv = '"Buchungstag";"Wertstellung (Buchungstag)";"Vorgang";"Buchungstext";"Umsatz in EUR"\n"01.05.2024";"01.05.2024";"Lastschrift";"Amazon";"- 29,99"'
        self.assertEqual(self._detect_from_csv(csv), "comdirect")

    def test_detect_commerzbank(self):
        csv = '"Buchungstag";"Wertstellung";"Buchungstext";"Auftraggeber / Beg\u00fcnstigter";"IBAN";"BIC";"Betrag EUR"\n"01.05.2024";"01.05.2024";"Lastschrift";"Amazon";"DE123";"COBADEFF";"-29,99"'
        self.assertEqual(self._detect_from_csv(csv), "commerzbank")

    def test_detect_deutsche_bank(self):
        csv = '"Buchungstag";"Wert";"Umsatzart";"Beg\u00fcnstigter / Auftraggeber";"Verwendungszweck";"Betrag EUR"\n"01.05.2024";"01.05.2024";"Lastschrift";"Amazon";"Kauf";"-29,99"'
        self.assertEqual(self._detect_from_csv(csv), "deutsche_bank")

    def test_detect_n26(self):
        csv = '"Datum","Empf\u00e4nger","Kontonummer","Transaktionstyp","Verwendungszweck","Betrag (EUR)"\n"2024-05-01","Amazon","","MasterCard-Zahlung","Kauf","-29.99"'
        self.assertEqual(self._detect_from_csv(csv), "n26")

    def test_detect_trade_republic(self):
        csv = '"Datum";"Typ";"Beschreibung";"Betrag (EUR)";"ISIN"\n"2024-05-01";"Einzahlung";"Geldeingang";"100,00";""'
        self.assertEqual(self._detect_from_csv(csv), "trade_republic")


class TestParseGermanAmountExtended(unittest.TestCase):
    """Tests for edge cases in amount parsing."""

    def test_comdirect_minus_space(self):
        """Comdirect uses '- 29,99' (space after minus)."""
        self.assertAlmostEqual(_parse_german_amount("- 29,99"), -29.99)

    def test_comdirect_plus_thousands(self):
        """Comdirect uses '+ 1.200,00'."""
        self.assertAlmostEqual(_parse_german_amount("+ 1.200,00"), 1200.0)

    def test_n26_dot_decimal(self):
        """N26 uses English decimal format."""
        result = _parse_german_amount("-29.99", decimal_sep=".")
        self.assertAlmostEqual(result, -29.99)

    def test_n26_positive(self):
        result = _parse_german_amount("1234.56", decimal_sep=".")
        self.assertAlmostEqual(result, 1234.56)


if __name__ == "__main__":
    unittest.main()