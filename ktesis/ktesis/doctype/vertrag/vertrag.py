import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Vertrag(Document):
    def validate(self):
        if self.vertragsbeginn and self.vertragsende:
            if getdate(self.vertragsende) <= getdate(self.vertragsbeginn):
                frappe.throw(_("Vertragsende muss nach dem Vertragsbeginn liegen"))
