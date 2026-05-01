import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Bankbuchung(Document):
    def validate(self):
        if not self.betrag or self.betrag == 0:
            frappe.throw(_("Betrag darf nicht 0 sein"))
        if self.datum and getdate(self.datum) > getdate(today()):
            frappe.throw(_("Buchungsdatum kann nicht in der Zukunft liegen"))
