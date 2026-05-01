import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime


class Wohnung(Document):
    def validate(self):
        current_year = datetime.now().year
        if self.kaufpreis is not None and self.kaufpreis <= 0:
            frappe.throw(_("Kaufpreis muss größer als 0 sein"))
        if self.wohnflaeche is not None and self.wohnflaeche <= 0:
            frappe.throw(_("Wohnfläche muss größer als 0 sein"))
        if self.baujahr is not None and not (1800 <= self.baujahr <= current_year):
            frappe.throw(_(f"Baujahr muss zwischen 1800 und {current_year} liegen"))
