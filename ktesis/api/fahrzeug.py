import frappe


@frappe.whitelist()
def get_vehicles(name=None):
	"""Return list of vehicles or single vehicle detail."""
	if name:
		vehicle = frappe.get_doc("Fahrzeug", name)
		return vehicle.as_dict()

	vehicles = frappe.get_all(
		"Fahrzeug",
		fields=["name", "kennzeichen", "marke", "modell", "baujahr", "farbe",
		        "status", "aktueller_km_stand", "kaufpreis"]
	)
	return {"vehicles": vehicles}


@frappe.whitelist()
def create_vehicle():
	"""Create a new Fahrzeug document."""
	data = frappe.local.form_dict
	doc = frappe.get_doc({
		"doctype": "Fahrzeug",
		"kennzeichen": data.get("kennzeichen"),
		"marke": data.get("marke"),
		"modell": data.get("modell"),
		"baujahr": data.get("baujahr"),
		"farbe": data.get("farbe"),
		"fin": data.get("fin"),
		"erstzulassung": data.get("erstzulassung"),
		"kaufpreis": data.get("kaufpreis"),
		"kaufdatum": data.get("kaufdatum"),
		"kilometerstand_kauf": data.get("kilometerstand_kauf"),
		"aktueller_km_stand": data.get("aktueller_km_stand"),
		"kraftstoff": data.get("kraftstoff"),
		"leistung_ps": data.get("leistung_ps"),
		"hubraum": data.get("hubraum"),
		"schein_bild": data.get("schein_bild"),
		"fahrzeug_bild": data.get("fahrzeug_bild"),
		"status": data.get("status", "Aktiv"),
	})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_vehicle(name):
	"""Update an existing Fahrzeug document."""
	doc = frappe.get_doc("Fahrzeug", name)
	data = frappe.local.form_dict

	for field in ["kennzeichen", "marke", "modell", "baujahr", "farbe", "fin",
	              "erstzulassung", "kaufpreis", "kaufdatum", "kilometerstand_kauf",
	              "aktueller_km_stand", "kraftstoff", "leistung_ps", "hubraum",
	              "schein_bild", "fahrzeug_bild", "status"]:
		if field in data:
			doc.set(field, data.get(field))

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_vehicle(name):
	"""Delete a Fahrzeug document."""
	frappe.get_doc("Fahrzeug", name).delete()
	return {"status": "ok"}
