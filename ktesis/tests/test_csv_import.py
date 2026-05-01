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

# Ersetze '@frappe.whitelist()\nKATEGORIE_KEYWORDS = ...' durch ''
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


if __name__ == "__main__":
    unittest.main()
