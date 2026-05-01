import re
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime


class Fahrzeug(Document):
    def validate(self):
        self._validate_kennzeichen()
        self._validate_fin()
        self._validate_kilometerstand()

    def _validate_kennzeichen(self):
        if self.kennzeichen:
            pattern = r'^[A-ZÄÖÜ]{1,3}-[A-Z]{1,2}-\d{1,4}[EH]?$'
            if not re.match(pattern, self.kennzeichen.upper()):
                frappe.throw(_("Ungültiges Kennzeichen-Format (Beispiel: B-AB-1234)"))

    def _validate_fin(self):
        if self.fin and len(self.fin) != 17:
            frappe.throw(_("FIN muss genau 17 Zeichen lang sein"))

    def _validate_kilometerstand(self):
        if self.aktueller_km_stand is not None and self.aktueller_km_stand < 0:
            frappe.throw(_("Kilometerstand darf nicht negativ sein"))
        if self.kilometerstand_kauf is not None and self.kilometerstand_kauf < 0:
            frappe.throw(_("Kilometerstand beim Kauf darf nicht negativ sein"))
