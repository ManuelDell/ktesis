import frappe


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


@frappe.whitelist()
def create_contract():
	"""Create a new Vertrag document."""
	data = frappe.local.form_dict
	doc = frappe.get_doc({
		"doctype": "Vertrag",
		"titel": data.get("titel"),
		"vertragstyp": data.get("vertragstyp"),
		"referenz_doctype": data.get("referenz_doctype"),
		"referenz_name": data.get("referenz_name"),
		"vertragspartner": data.get("vertragspartner"),
		"vertragsnummer": data.get("vertragsnummer"),
		"vertragsbeginn": data.get("vertragsbeginn"),
		"vertragsende": data.get("vertragsende"),
		"kuendigungsfrist": data.get("kuendigungsfrist"),
		"kosten_monatlich": data.get("kosten_monatlich"),
		"kosten_jaehrlich": data.get("kosten_jaehrlich"),
		"aktiv": data.get("aktiv", 1),
		"dokument": data.get("dokument"),
		"laufzeit_monate": data.get("laufzeit_monate"),
		"notizen": data.get("notizen"),
	})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_contract(name):
	"""Update an existing Vertrag document."""
	doc = frappe.get_doc("Vertrag", name)
	data = frappe.local.form_dict

	for field in ["titel", "vertragstyp", "referenz_doctype", "referenz_name",
	              "vertragspartner", "vertragsnummer", "vertragsbeginn", "vertragsende",
	              "kuendigungsfrist", "kosten_monatlich", "kosten_jaehrlich",
	              "aktiv", "dokument", "laufzeit_monate", "notizen"]:
		if field in data:
			doc.set(field, data.get(field))

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_contract(name):
	"""Delete a Vertrag document."""
	frappe.get_doc("Vertrag", name).delete()
	return {"status": "ok"}
