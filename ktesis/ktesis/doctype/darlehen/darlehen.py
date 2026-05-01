import frappe
from frappe import _
from frappe.model.document import Document


class Darlehen(Document):
    def validate(self):
        if self.zinssatz is not None and not (0 <= self.zinssatz <= 100):
            frappe.throw(_("Zinssatz muss zwischen 0 und 100% liegen"))
        if self.darlehensbetrag is not None and self.darlehensbetrag <= 0:
            frappe.throw(_("Darlehensbetrag muss größer als 0 sein"))
        if self.laufzeit_jahre is not None and self.laufzeit_jahre <= 0:
            frappe.throw(_("Laufzeit muss größer als 0 Jahre sein"))
