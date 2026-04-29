import frappe


@frappe.whitelist()
def get_bank_accounts(name=None):
	"""Return list of bank accounts or single account detail."""
	if name:
		acc = frappe.get_doc("Bankkonto", name)
		return acc.as_dict()

	accounts = frappe.get_all(
		"Bankkonto",
		fields=["name", "bezeichnung", "bank", "iban", "kontotyp",
		        "kontostand_manuell", "kontostand_live", "kontostand_abgerufen_am",
		        "waehrung", "fints_aktiv", "aktiv"]
	)
	return {"accounts": accounts}


@frappe.whitelist()
def create_bank_account():
	"""Create a new Bankkonto document."""
	data = frappe.local.form_dict
	doc = frappe.get_doc({
		"doctype": "Bankkonto",
		"bezeichnung": data.get("bezeichnung"),
		"bank": data.get("bank"),
		"iban": data.get("iban"),
		"bic": data.get("bic"),
		"blz": data.get("blz"),
		"fints_url": data.get("fints_url"),
		"fints_login": data.get("fints_login"),
		"kontonummer": data.get("kontonummer"),
		"kontostand_manuell": data.get("kontostand_manuell"),
		"kontotyp": data.get("kontotyp"),
		"waehrung": data.get("waehrung", "EUR"),
		"fints_aktiv": data.get("fints_aktiv", 0),
		"aktiv": data.get("aktiv", 1),
	})
	doc.insert()
	if data.get("fints_pin"):
		frappe.utils.password.update_password("Bankkonto", doc.name, "fints_pin", data["fints_pin"])
	return doc.as_dict()


@frappe.whitelist()
def update_bank_account(name):
	"""Update an existing Bankkonto document."""
	doc = frappe.get_doc("Bankkonto", name)
	data = frappe.local.form_dict

	for field in ["bezeichnung", "bank", "iban", "bic", "blz", "fints_url", "fints_login",
	              "kontonummer", "kontostand_manuell", "kontotyp", "waehrung",
	              "fints_aktiv", "aktiv"]:
		if field in data:
			doc.set(field, data.get(field))

	doc.save()
	if data.get("fints_pin"):
		frappe.utils.password.update_password("Bankkonto", name, "fints_pin", data["fints_pin"])
	return doc.as_dict()


@frappe.whitelist()
def delete_bank_account(name):
	"""Delete a Bankkonto document."""
	frappe.get_doc("Bankkonto", name).delete()
	return {"status": "ok"}


@frappe.whitelist()
def get_buchungen(limit=50):
	"""Return recent bank transactions with account names."""
	buchungen = frappe.get_all(
		"Bankbuchung",
		fields=["name", "bankkonto", "datum", "buchungstext", "betrag", "kategorie", "notizen"],
		limit=int(limit),
		order_by="datum desc",
	)
	# enrich with account name
	for b in buchungen:
		b["bankkonto_bezeichnung"] = frappe.db.get_value("Bankkonto", b["bankkonto"], "bezeichnung")
	return buchungen
