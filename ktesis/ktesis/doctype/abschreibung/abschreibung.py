import frappe
from frappe import _
from frappe.model.document import Document


class Abschreibung(Document):
    def validate(self):
        if self.abschreibungssatz is not None and not (0 <= self.abschreibungssatz <= 100):
            frappe.throw(_("Abschreibungssatz muss zwischen 0 und 100% liegen"))
        if self.abschreibungsbetrag is not None and self.abschreibungsbetrag < 0:
            frappe.throw(_("Abschreibungsbetrag darf nicht negativ sein"))
