import re
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime


class Fahrzeug(Document):
    def validate(self):
        self._validate_fin()
        self._validate_kilometerstand()

    def _validate_fin(self):
        if self.fin and len(self.fin) != 17:
            frappe.throw(_("FIN muss genau 17 Zeichen lang sein"))

    def _validate_kilometerstand(self):
        if self.aktueller_km_stand is not None and self.aktueller_km_stand < 0:
            frappe.throw(_("Kilometerstand darf nicht negativ sein"))
        if self.kilometerstand_kauf is not None and self.kilometerstand_kauf < 0:
            frappe.throw(_("Kilometerstand beim Kauf darf nicht negativ sein"))
