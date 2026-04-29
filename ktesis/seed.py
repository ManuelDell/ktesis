import frappe
from datetime import datetime, timedelta

def run():
    today = datetime.today().date()

    # Bankkonten
    konten = [
        {'bezeichnung': 'Sparkonto ING', 'bank': 'ING', 'iban': 'DE75512108001245126199', 'kontotyp': 'Sparbuch', 'kontostand_manuell': 12500.00, 'waehrung': 'EUR', 'aktiv': 1},
        {'bezeichnung': 'Kreditkarte Visa', 'bank': 'Commerzbank', 'kontotyp': 'Kreditkarte', 'kontostand_manuell': -450.20, 'waehrung': 'EUR', 'aktiv': 1},
    ]
    for k in konten:
        if not frappe.db.exists('Bankkonto', {'bezeichnung': k['bezeichnung']}):
            doc = frappe.get_doc({'doctype': 'Bankkonto', **k})
            doc.insert()
            print(f'Bankkonto: {k["bezeichnung"]}')

    # Vertraege
    vertraege = [
        {'titel': 'Strom Lieferant', 'vertragstyp': 'Sonstiges', 'vertragspartner': 'E.ON', 'vertragsbeginn': '2025-01-01', 'vertragsende': str(today + timedelta(days=45)), 'kuendigungsfrist': 1, 'kosten_monatlich': 85.5, 'kosten_jaehrlich': 1026, 'aktiv': 1},
        {'titel': 'Internet Vodafone', 'vertragstyp': 'Sonstiges', 'vertragspartner': 'Vodafone', 'vertragsbeginn': '2025-06-01', 'vertragsende': str(today + timedelta(days=10)), 'kuendigungsfrist': 1, 'kosten_monatlich': 45, 'kosten_jaehrlich': 540, 'aktiv': 1},
        {'titel': 'KFZ Versicherung', 'vertragstyp': 'Versicherung', 'vertragspartner': 'HUK-Coburg', 'vertragsbeginn': '2024-03-01', 'vertragsende': str(today + timedelta(days=120)), 'kuendigungsfrist': 1, 'kosten_monatlich': 65, 'kosten_jaehrlich': 780, 'aktiv': 1},
        {'titel': 'Netflix Abo', 'vertragstyp': 'Sonstiges', 'vertragspartner': 'Netflix Inc.', 'vertragsbeginn': '2023-01-01', 'vertragsende': None, 'kuendigungsfrist': 0, 'kosten_monatlich': 12.99, 'kosten_jaehrlich': 155.88, 'aktiv': 1},
        {'titel': 'Fitnessstudio', 'vertragstyp': 'Sonstiges', 'vertragspartner': 'McFit', 'vertragsbeginn': '2025-01-01', 'vertragsende': str(today - timedelta(days=5)), 'kuendigungsfrist': 1, 'kosten_monatlich': 29.99, 'kosten_jaehrlich': 359.88, 'aktiv': 1},
    ]
    for v in vertraege:
        if not frappe.db.exists('Vertrag', {'titel': v['titel']}):
            doc = frappe.get_doc({'doctype': 'Vertrag', **v})
            doc.insert()
            print(f'Vertrag: {v["titel"]}')

    frappe.db.commit()
    print('=== FERTIG ===')
