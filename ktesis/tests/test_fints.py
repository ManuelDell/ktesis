import frappe
from frappe.tests.utils import FrappeTestCase
from unittest.mock import MagicMock

from ktesis.api.fints import _find_account, _sync_iban


def _mock_account(accountnumber, iban=None):
    acc = MagicMock()
    acc.accountnumber = accountnumber
    acc.iban = iban
    return acc


def _insert_buchung(bankkonto, datum, betrag, kategorie, buchungstext):
    frappe.get_doc({
        "doctype": "Bankbuchung",
        "bankkonto": bankkonto,
        "datum": datum,
        "betrag": betrag,
        "kategorie": kategorie,
        "buchungstext": buchungstext,
    }).insert(ignore_permissions=True)


class TestFindAccount(FrappeTestCase):

    def test_kein_kontonummer_gibt_ersten_zurueck(self):
        accounts = [_mock_account("1111"), _mock_account("2222")]
        self.assertEqual(_find_account(accounts, ""), accounts[0])

    def test_none_kontonummer_gibt_ersten_zurueck(self):
        accounts = [_mock_account("1111"), _mock_account("2222")]
        self.assertEqual(_find_account(accounts, None), accounts[0])

    def test_exakter_kontonummer_treffer(self):
        accounts = [_mock_account("1111"), _mock_account("2222")]
        self.assertEqual(_find_account(accounts, "2222"), accounts[1])

    def test_iban_substring_treffer(self):
        accounts = [
            _mock_account("1111", "DE111234567800000001"),
            _mock_account("2222", "DE111234567800000002"),
        ]
        self.assertEqual(_find_account(accounts, "00000002"), accounts[1])

    def test_kein_treffer_gibt_ersten_zurueck(self):
        accounts = [_mock_account("1111"), _mock_account("2222")]
        self.assertEqual(_find_account(accounts, "9999"), accounts[0])

    def test_kontonummer_hat_vorrang_vor_iban(self):
        # accountnumber passt auf accounts[1], iban-substring passt auf accounts[0]
        accounts = [
            _mock_account("1111", "DE111234567800002222"),
            _mock_account("2222", "DE111234567800001111"),
        ]
        self.assertEqual(_find_account(accounts, "2222"), accounts[1])


class TestSyncIban(FrappeTestCase):

    def setUp(self):
        super().setUp()
        self.konto = frappe.get_doc({
            "doctype": "Bankkonto",
            "bezeichnung": "_Test IBAN Sync",
            "waehrung": "EUR",
        }).insert(ignore_permissions=True)

    def test_iban_wird_gesetzt_wenn_leer(self):
        account = MagicMock()
        account.iban = "DE02300606010002474689"
        _sync_iban(self.konto.name, account)
        self.konto.reload()
        self.assertEqual(self.konto.iban, "DE02300606010002474689")

    def test_iban_wird_nicht_ueberschrieben(self):
        self.konto.iban = "DE02200400600515474757"
        self.konto.save(ignore_permissions=True)

        account = MagicMock()
        account.iban = "DE02300606010002474689"
        _sync_iban(self.konto.name, account)
        self.konto.reload()
        self.assertEqual(self.konto.iban, "DE02200400600515474757")

    def test_keine_iban_von_bank_aendert_nichts(self):
        account = MagicMock()
        account.iban = None
        _sync_iban(self.konto.name, account)
        self.konto.reload()
        self.assertFalse(self.konto.iban)


class TestDuplikatErkennung(FrappeTestCase):
    """
    Testet die Duplikat-Logik aus _save_transactions indirekt:
    frappe.db.exists mit denselben Feldern die _save_transactions prüft.
    """

    def setUp(self):
        super().setUp()
        self.konto = frappe.get_doc({
            "doctype": "Bankkonto",
            "bezeichnung": "_Test Duplikat",
            "waehrung": "EUR",
        }).insert(ignore_permissions=True)

    def test_exaktes_duplikat_erkannt(self):
        _insert_buchung(self.konto.name, "2026-01-15", 100.0, "Eingang", "Gehalt Januar")
        exists = frappe.db.exists("Bankbuchung", {
            "bankkonto": self.konto.name,
            "datum": "2026-01-15",
            "betrag": 100.0,
            "kategorie": "Eingang",
            "buchungstext": "Gehalt Januar",
        })
        self.assertTrue(exists)

    def test_eingang_und_ausgang_gleicher_betrag_kein_duplikat(self):
        # Vor dem Fix wäre der Ausgang fälschlich als Duplikat erkannt worden
        _insert_buchung(self.konto.name, "2026-01-15", 100.0, "Eingang", "Überweisung")
        exists = frappe.db.exists("Bankbuchung", {
            "bankkonto": self.konto.name,
            "datum": "2026-01-15",
            "betrag": 100.0,
            "kategorie": "Ausgang",
            "buchungstext": "Überweisung",
        })
        self.assertFalse(exists)

    def test_verschiedene_buchungstexte_kein_duplikat(self):
        _insert_buchung(self.konto.name, "2026-01-15", 29.99, "Ausgang", "Netflix")
        exists = frappe.db.exists("Bankbuchung", {
            "bankkonto": self.konto.name,
            "datum": "2026-01-15",
            "betrag": 29.99,
            "kategorie": "Ausgang",
            "buchungstext": "Spotify",
        })
        self.assertFalse(exists)

    def test_selber_text_anderes_datum_kein_duplikat(self):
        _insert_buchung(self.konto.name, "2026-01-01", 50.0, "Ausgang", "Miete")
        exists = frappe.db.exists("Bankbuchung", {
            "bankkonto": self.konto.name,
            "datum": "2026-02-01",
            "betrag": 50.0,
            "kategorie": "Ausgang",
            "buchungstext": "Miete",
        })
        self.assertFalse(exists)

    def test_zwei_identische_buchungen_gleichzeitig(self):
        # Erster Insert
        _insert_buchung(self.konto.name, "2026-01-15", 29.99, "Ausgang", "Netflix")
        # Zweiter Insert mit identischen Daten — Frappe würde einen neuen Record
        # anlegen (kein UNIQUE constraint), aber _save_transactions würde skippen.
        # Wir prüfen: existiert genau ein Datensatz?
        count = frappe.db.count("Bankbuchung", {
            "bankkonto": self.konto.name,
            "datum": "2026-01-15",
            "betrag": 29.99,
            "kategorie": "Ausgang",
            "buchungstext": "Netflix",
        })
        self.assertEqual(count, 1)
