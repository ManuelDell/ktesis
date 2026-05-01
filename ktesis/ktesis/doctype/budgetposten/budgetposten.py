import frappe
from frappe import _
from frappe.model.document import Document


class Budgetposten(Document):
    def validate(self):
        if self.betrag_monatlich is not None and self.betrag_monatlich < 0:
            frappe.throw(_("Budget darf nicht negativ sein"))
