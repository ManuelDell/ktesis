import frappe
from frappe.tests.utils import FrappeTestCase


class TestDashboardAPI(FrappeTestCase):
    def test_get_dashboard_stats_structure(self):
        """get_dashboard_stats muss alle erwarteten Felder zurückgeben."""
        from ktesis.api.__init__ import get_dashboard_stats
        result = get_dashboard_stats()
        expected_keys = [
            "fahrzeuge", "wohnungen", "aktive_vertraege",
            "bank_saldo", "darlehensbetrag", "restschuld", "monate_kosten"
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Feld '{key}' fehlt in get_dashboard_stats")
            self.assertIsInstance(result[key], (int, float), f"Feld '{key}' muss numerisch sein")

    def test_get_finance_summary_structure(self):
        """get_finance_summary muss bankkonten, darlehen und vertragskosten zurückgeben."""
        from ktesis.api.dashboard import get_finance_summary
        result = get_finance_summary()
        self.assertIn("bankkonten", result)
        self.assertIn("darlehen", result)
        self.assertIn("vertragskosten", result)
        self.assertIsInstance(result["bankkonten"], list)
        self.assertIsInstance(result["darlehen"], list)
        self.assertIsInstance(result["vertragskosten"], dict)
        if result["bankkonten"]:
            bk = result["bankkonten"][0]
            self.assertIn("bezeichnung", bk)
            self.assertIn("kontostand_manuell", bk)

    def test_get_vermoegensentwicklung_structure(self):
        """get_vermoegensentwicklung muss Vermögensdaten zurückgeben."""
        from ktesis.api.dashboard import get_vermoegensentwicklung
        result = get_vermoegensentwicklung()
        expected_keys = [
            "immobilien_wert", "fahrzeuge_wert", "bank_saldo",
            "restschuld", "nettovermoegen", "bruttovermoegen"
        ]
        for key in expected_keys:
            self.assertIn(key, result)
            self.assertIsInstance(result[key], (int, float))

    def test_get_vertrags_ampel_structure(self):
        """get_vertrags_ampel muss Liste mit ampel-Feld zurückgeben."""
        from ktesis.api.dashboard import get_vertrags_ampel
        result = get_vertrags_ampel()
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIn("ampel", item)
            self.assertIn(item["ampel"], ("gruen", "gelb", "rot"))
