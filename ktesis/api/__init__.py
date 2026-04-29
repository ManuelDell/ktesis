import frappe
from frappe import _


@frappe.whitelist()
def get_dashboard_stats():
    """Return summary statistics for the Ktesis dashboard."""
    fahrzeuge = frappe.db.count("Fahrzeug")
    wohnungen = frappe.db.count("Wohnung")
    aktive_vertraege = frappe.db.count("Vertrag", {"aktiv": 1})

    bank_saldo = frappe.db.sql("""
        SELECT COALESCE(SUM(kontostand_manuell), 0) FROM `tabBankkonto` WHERE aktiv = 1
    """)[0][0] or 0

    darlehen_betrag = frappe.db.sql("""
        SELECT COALESCE(SUM(darlehensbetrag), 0) FROM `tabDarlehen` WHERE aktiv = 1
    """)[0][0] or 0

    restschuld = frappe.db.sql("""
        SELECT COALESCE(SUM(restschuld), 0) FROM `tabDarlehen` WHERE aktiv = 1
    """)[0][0] or 0

    monatliche_kosten = frappe.db.sql("""
        SELECT COALESCE(SUM(kosten_monatlich), 0) FROM `tabVertrag` WHERE aktiv = 1
    """)[0][0] or 0

    return {
        "fahrzeuge": fahrzeuge,
        "wohnungen": wohnungen,
        "aktive_vertraege": aktive_vertraege,
        "bank_saldo": bank_saldo,
        "darlehensbetrag": darlehen_betrag,
        "restschuld": restschuld,
        "monatliche_kosten": monatliche_kosten
    }
