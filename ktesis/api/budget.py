from __future__ import annotations
import calendar
import frappe
from frappe import _
from frappe.utils import today, getdate


@frappe.whitelist()
def wohnung_budget_vergleich(wohnung_name: str, monat: str = None) -> dict:
    """Soll-Ist-Vergleich für eine Wohnung. monat: YYYY-MM (Standard: aktueller Monat)."""
    if not monat:
        d = getdate(today())
        monat = f"{d.year}-{d.month:02d}"

    wohnung = frappe.get_doc("Wohnung", wohnung_name)
    jahr, mon = monat.split("-")
    letzter_tag = calendar.monthrange(int(jahr), int(mon))[1]
    monat_start = f"{monat}-01"
    monat_ende = f"{monat}-{letzter_tag:02d}"

    def _get_ist(bp_name):
        if not bp_name:
            return 0.0
        res = frappe.db.sql(
            "SELECT COALESCE(SUM(ABS(betrag)), 0) FROM `tabBankbuchung` "
            "WHERE budgetposten = %s AND datum BETWEEN %s AND %s",
            (bp_name, monat_start, monat_ende)
        )
        return float(res[0][0]) if res else 0.0

    posten = []
    nt = wohnung.nutzungstyp if hasattr(wohnung, "nutzungstyp") else ""

    if nt == "Gemietet":
        if wohnung.mietbudgetposten:
            ist = _get_ist(wohnung.mietbudgetposten)
            soll = float(wohnung.monatliche_miete or 0)
            posten.append({"label": "Kaltmiete", "budgetposten": wohnung.mietbudgetposten,
                           "soll": soll, "ist": ist, "differenz": soll - ist})
        if wohnung.nebenkostenbudgetposten:
            ist = _get_ist(wohnung.nebenkostenbudgetposten)
            soll = float(wohnung.nebenkosten_monatlich or 0)
            posten.append({"label": "Nebenkosten", "budgetposten": wohnung.nebenkostenbudgetposten,
                           "soll": soll, "ist": ist, "differenz": soll - ist})
    elif nt == "Vermietet":
        if wohnung.einnahmebudgetposten:
            ist = _get_ist(wohnung.einnahmebudgetposten)
            soll = float(wohnung.mieteinnahme_monatlich or 0)
            posten.append({"label": "Mieteinnahme", "budgetposten": wohnung.einnahmebudgetposten,
                           "soll": soll, "ist": ist, "differenz": ist - soll})
        if getattr(wohnung, "nebenkostenbudgetposten_verm", None):
            ist = _get_ist(wohnung.nebenkostenbudgetposten_verm)
            soll = float(getattr(wohnung, "nebenkosten_monatlich_verm", 0) or 0)
            posten.append({"label": "Nebenkosten", "budgetposten": wohnung.nebenkostenbudgetposten_verm,
                           "soll": soll, "ist": ist, "differenz": soll - ist})

    gesamt_soll = sum(p["soll"] for p in posten)
    gesamt_ist = sum(p["ist"] for p in posten)

    return {
        "wohnung": wohnung_name,
        "bezeichnung": wohnung.bezeichnung,
        "nutzungstyp": nt,
        "monat": monat,
        "posten": posten,
        "gesamt_soll": gesamt_soll,
        "gesamt_ist": gesamt_ist,
        "gesamt_differenz": gesamt_soll - gesamt_ist,
    }
