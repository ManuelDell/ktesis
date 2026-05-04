import frappe

@frappe.whitelist()
def get_buchungsregeln():
    return frappe.get_all("Buchungsregel",
        fields=["name","empfaenger_pattern","budgetposten","match_count","aktiv"],
        filters={"aktiv": 1},
        order_by="match_count desc"
    )

@frappe.whitelist()
def create_buchungsregel(empfaenger_pattern, budgetposten):
    # Prüfe ob Pattern schon existiert
    existing = frappe.db.get_value("Buchungsregel", {"empfaenger_pattern": empfaenger_pattern}, "name")
    if existing:
        frappe.db.set_value("Buchungsregel", existing, "budgetposten", budgetposten)
        return {"name": existing, "updated": True}
    doc = frappe.get_doc({"doctype": "Buchungsregel", "empfaenger_pattern": empfaenger_pattern, "budgetposten": budgetposten})
    doc.insert(ignore_permissions=True)
    return {"name": doc.name, "created": True}

@frappe.whitelist()
def delete_buchungsregel(name):
    frappe.delete_doc("Buchungsregel", name, ignore_permissions=True)
    return {"deleted": True}

@frappe.whitelist()
def apply_buchungsregeln():
    """Wendet alle aktiven Regeln auf offene (nicht zugeordnete) Buchungen an"""
    regeln = frappe.get_all("Buchungsregel",
        fields=["name","empfaenger_pattern","budgetposten"],
        filters={"aktiv": 1}
    )
    total_assigned = 0
    for regel in regeln:
        pattern = regel.empfaenger_pattern.rstrip("*").lower()
        # Buchungen finden die passen (LIKE-Match auf buchungstext)
        buchungen = frappe.db.get_all("Bankbuchung",
            filters=[["budgetposten", "is", "not set"],
                     ["buchungstext", "like", f"%{pattern}%"]],
            fields=["name"]
        )
        if buchungen:
            for b in buchungen:
                frappe.db.set_value("Bankbuchung", b.name, "budgetposten", regel.budgetposten)
            frappe.db.set_value("Buchungsregel", regel.name, "match_count",
                regel.get("match_count", 0) + len(buchungen))
            total_assigned += len(buchungen)
    frappe.db.commit()
    return {"assigned": total_assigned}
