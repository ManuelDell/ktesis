import frappe
from frappe import _


@frappe.whitelist()
def get_dashboard_stats():
	"""Return summary statistics for the Ktesis dashboard."""
	fahrzeuge = frappe.db.count("Fahrzeug")
	wohnungen = frappe.db.count("Wohnung")
	aktive_vertraege = frappe.db.count("Vertrag", {"aktiv": 1})

	bank_saldo = frappe.db.sql("""
		SELECT COALESCE(SUM(saldo), 0) FROM `tabBankkonto` WHERE aktiv = 1
	""")[0][0] or 0

	darlehen_betrag = frappe.db.sql("""
		SELECT COALESCE(SUM(darlehensbetrag), 0) FROM `tabDarlehen` WHERE status = 'Aktiv'
	""")[0][0] or 0

	restschuld = frappe.db.sql("""
		SELECT COALESCE(SUM(restschuld), 0) FROM `tabDarlehen` WHERE status = 'Aktiv'
	""")[0][0] or 0

	monatliche_kosten = frappe.db.sql("""
		SELECT COALESCE(SUM(kosten_monatlich), 0) FROM `tabVertrag` WHERE aktiv = 1
	""")[0][0] or 0

	return {
		"fahrzeuge": fahrzeuge,
		"wohnungen": wohnungen,
		"aktive_vertraege": aktive_vertraege,
		"bank_saldo": bank_saldo,
		"darlehensbetrag": darlehen_betrag,
		"restschuld": restschuld,
		"monatliche_kosten": monatliche_kosten
	}


@frappe.whitelist()
def get_finance_summary():
	"""Return finance overview: bank accounts, loans, contract costs."""
	bankkonten = frappe.get_all(
		"Bankkonto",
		filters={"aktiv": 1},
		fields=["name", "bezeichnung", "bank_name", "kontotyp", "saldo", "waehrung"]
	)

	darlehen = frappe.get_all(
		"Darlehen",
		filters={"status": "Aktiv"},
		fields=["name", "titel", "bank_name", "darlehensbetrag", "restschuld",
		        "sollzins", "monatliche_rate", "enddatum"]
	)

	vertragskosten = frappe.db.sql("""
		SELECT
			COALESCE(SUM(kosten_monatlich), 0) as monatlich,
			COALESCE(SUM(kosten_jaehrlich), 0) as jaehrlich
		FROM `tabVertrag`
		WHERE aktiv = 1
	""", as_dict=True)[0]

	return {
		"bankkonten": bankkonten,
		"darlehen": darlehen,
		"vertragskosten": {
			"monatlich": vertragskosten.monatlich or 0,
			"jaehrlich": vertragskosten.jaehrlich or 0
		}
	}


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
def get_properties(name=None):
	"""Return list of properties or single property detail with depreciations."""
	if name:
		prop = frappe.get_doc("Wohnung", name)
		data = prop.as_dict()
		data.abschreibungen = frappe.get_all(
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
def get_contracts(name=None):
	"""Return list of contracts or single contract detail."""
	if name:
		contract = frappe.get_doc("Vertrag", name)
		return contract.as_dict()

	contracts = frappe.get_all(
		"Vertrag",
		fields=["name", "titel", "vertragstyp", "aktiv", "vertragspartner",
		        "vertragsbeginn", "vertragsende", "kosten_monatlich", "kosten_jaehrlich",
		        "referenz_doctype", "referenz_name"]
	)
	return {"contracts": contracts}
