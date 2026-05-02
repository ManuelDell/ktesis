import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime


class Wohnung(Document):
    def validate(self):
        current_year = datetime.now().year
        # Nur validieren wenn Nutzungstyp Eigentum oder nicht gesetzt (Kauf-Felder)
        if self.nutzungstyp in ("Eigentum", "", None):
            kp = self.kaufpreis
            if kp not in (None, '', 0) and float(kp or 0) <= 0:
                frappe.throw(_("Kaufpreis muss größer als 0 sein"))
        wf = self.wohnflaeche
        if wf not in (None, '') and float(wf or 0) <= 0:
            frappe.throw(_("Wohnfläche muss größer als 0 sein"))
        bj = self.baujahr
        if bj not in (None, '') and not (1800 <= int(bj) <= current_year):
            frappe.throw(_(f"Baujahr muss zwischen 1800 und {current_year} liegen"))
