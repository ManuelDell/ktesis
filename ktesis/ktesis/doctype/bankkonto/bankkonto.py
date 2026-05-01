import re
import frappe
from frappe import _
from frappe.model.document import Document


class Bankkonto(Document):
    def validate(self):
        self._validate_iban()
        self._validate_blz()

    def _validate_iban(self):
        if self.iban:
            iban = self.iban.replace(' ', '').upper()
            if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$', iban):
                frappe.throw(_("Ungültiges IBAN-Format (Beispiel: DE89370400440532013000)"))
            self.iban = iban

    def _validate_blz(self):
        if self.blz and len(self.blz.strip()) != 8:
            frappe.throw(_("BLZ muss genau 8 Stellen haben"))
