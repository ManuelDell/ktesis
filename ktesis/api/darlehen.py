import frappe
from frappe import _
from datetime import date, timedelta


@frappe.whitelist()
def get_loans(name=None):
	"""Return list of loans or single loan detail."""
	if name:
		doc = frappe.get_doc("Darlehen", name)
		data = doc.as_dict()
		return data
	loans = frappe.get_all(
		"Darlehen",
		filters={"aktiv": 1},
		fields=["name", "bezeichnung", "darlehensgeber", "darlehensbetrag",
		        "restschuld", "zinssatz", "monatliche_rate", "beginn", "ende",
		        "status", "wohnung"]
	)
	return {"loans": loans}


@frappe.whitelist()
def create_loan():
	"""Create a new Darlehen document."""
	data = frappe.local.form_dict
	doc = frappe.get_doc({
		"doctype": "Darlehen",
		"bezeichnung": data.get("bezeichnung"),
		"wohnung": data.get("wohnung"),
		"darlehensgeber": data.get("darlehensgeber"),
		"darlehensnummer": data.get("darlehensnummer"),
		"darlehensbetrag": data.get("darlehensbetrag"),
		"zinssatz": data.get("zinssatz"),
		"tilgungssatz": data.get("tilgungssatz"),
		"monatliche_rate": data.get("monatliche_rate"),
		"rate_inkl_zins_tilgung": data.get("rate_inkl_zins_tilgung", 1),
		"laufzeit_jahre": data.get("laufzeit_jahre"),
		"beginn": data.get("beginn"),
		"ende": data.get("ende"),
		"restschuld": data.get("restschuld"),
		"tilgungsfreie_jahre": data.get("tilgungsfreie_jahre"),
		"sollzinsbindung_bis": data.get("sollzinsbindung_bis"),
		"pdf_dokument": data.get("pdf_dokument"),
		"notizen": data.get("notizen"),
		"aktiv": data.get("aktiv", 1),
	})
	doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def update_loan(name):
	"""Update an existing Darlehen document."""
	doc = frappe.get_doc("Darlehen", name)
	data = frappe.local.form_dict

	for field in ["bezeichnung", "wohnung", "darlehensgeber", "darlehensnummer",
	              "darlehensbetrag", "zinssatz", "tilgungssatz", "monatliche_rate",
	              "rate_inkl_zins_tilgung", "laufzeit_jahre", "beginn", "ende",
	              "restschuld", "tilgungsfreie_jahre", "sollzinsbindung_bis",
	              "pdf_dokument", "notizen", "aktiv"]:
		if field in data:
			doc.set(field, data.get(field))

	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_loan(name):
	"""Delete a Darlehen document."""
	frappe.get_doc("Darlehen", name).delete()
	return {"status": "ok"}


@frappe.whitelist()
def calculate_amortization_schedule(name):
	"""
	Calculate and return the amortization (Tilgungsplan) for a loan.

	Returns a list of monthly entries with:
	- month (int), date, rate, interest, repayment, remaining_balance
	"""
	loan = frappe.get_doc("Darlehen", name)

	if not loan.darlehensbetrag or not loan.zinssatz:
		return {"error": "Darlehensbetrag und Zinssatz müssen gesetzt sein."}

	# Determine monthly rate
	if loan.monatliche_rate and loan.monatliche_rate > 0:
		monthly_rate = loan.monatliche_rate
	elif loan.tilgungssatz and loan.tilgungssatz > 0:
		# Calculate rate: (loan_amount * (interest + repayment) / 12) / 100
		monthly_rate = loan.darlehensbetrag * (loan.zinssatz + loan.tilgungssatz) / 12 / 100
	else:
		return {"error": "Bitte monatliche Rate oder Tilgungssatz angeben."}

	interest_rate_monthly = loan.zinssatz / 12 / 100
	remaining = loan.restschuld or loan.darlehensbetrag

	schedule = []
	max_months = loan.laufzeit_jahre * 12 if loan.laufzeit_jahre else 12 * 30  # max 30 Jahre default
	tilgungsfreie_monate = (loan.tilgungsfreie_jahre or 0) * 12

	start_date = loan.beginn or date.today()

	for i in range(1, min(max_months, 360) + 1):
		if remaining <= 0:
			break

		interest = remaining * interest_rate_monthly

		if i <= tilgungsfreie_monate:
			# Tilgungsfreie Zeit: nur Zinsen zahlen
			repayment = 0
			rate = interest
		else:
			repayment = min(monthly_rate - interest, remaining)
			rate = monthly_rate
			if repayment < 0:
				repayment = 0
				rate = interest

		remaining -= repayment

		# Calculate date
		month = (start_date.month - 1 + i - 1) % 12 + 1
		year = start_date.year + (start_date.month - 1 + i - 1) // 12
		try:
			entry_date = date(year, month, start_date.day)
		except ValueError:
			entry_date = date(year, month, 1)

		schedule.append({
			"monat": i,
			"datum": entry_date.isoformat(),
			"rate": round(rate, 2),
			"zins": round(interest, 2),
			"tilgung": round(repayment, 2),
			"restschuld": round(max(remaining, 0), 2),
		})

	return {
		"loan_name": name,
		"loan_bezeichnung": loan.bezeichnung,
		"darlehensbetrag": loan.darlehensbetrag,
		"zinssatz": loan.zinssatz,
		"monatliche_rate": round(monthly_rate, 2),
		"tilgungsplan": schedule
	}
