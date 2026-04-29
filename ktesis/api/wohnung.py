import frappe


@frappe.whitelist()
def get_properties(name=None):
	"""Return list of properties or single property detail with depreciations."""
	if name:
		prop = frappe.get_doc("Wohnung", name)
		data = prop.as_dict()
		data["abschreibungen"] = frappe.get_all(
			"Abschreibung",
			filters={"parent": name, "parenttype": "Wohnung"},
			fields=["jahr", "abschreibungssatz", "abschreibungsbetrag", "restbuchwert", "bemerkung"],
			order_by="jahr desc"
		)
		return data

	properties = frappe.get_all(
		"Wohnung",
		fields=["name", "bezeichnung", "wohnungstyp", "status", "ort", "plz",
		        "wohnflaeche", "kaufpreis", "aktueller_wert"]
	)
	return {"properties": properties}


@frappe.whitelist()
def create_property():
	"""Create a new Wohnung document."""
	data = frappe.local.form_dict
	doc = frappe.get_doc({
		"doctype": "Wohnung",
		"bezeichnung": data.get("bezeichnung"),
		"strasse": data.get("strasse"),
		"hausnummer": data.get("hausnummer"),
		"plz": data.get("plz"),
		"ort": data.get("ort"),
		"land": data.get("land", "Deutschland"),
		"wohnflaeche": data.get("wohnflaeche"),
		"zimmer": data.get("zimmer"),
		"baujahr": data.get("baujahr"),
		"kaufpreis": data.get("kaufpreis"),
		"kaufdatum": data.get("kaufdatum"),
		"kauf_wert": data.get("kauf_wert"),
		"aktueller_wert": data.get("aktueller_wert"),
		"wohnungstyp": data.get("wohnungstyp"),
		"status": data.get("status", "Aktiv"),
	})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_property(name):
	"""Update an existing Wohnung document."""
	doc = frappe.get_doc("Wohnung", name)
	data = frappe.local.form_dict

	for field in ["bezeichnung", "strasse", "hausnummer", "plz", "ort", "land",
	              "wohnflaeche", "zimmer", "baujahr", "kaufpreis", "kaufdatum",
	              "kauf_wert", "aktueller_wert", "wohnungstyp", "status"]:
		if field in data:
			doc.set(field, data.get(field))

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_property(name):
	"""Delete a Wohnung document."""
	frappe.get_doc("Wohnung", name).delete()
	return {"status": "ok"}
