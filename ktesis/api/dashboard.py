import frappe
from datetime import datetime, timedelta


@frappe.whitelist()
def get_finance_summary():
	"""Return finance overview: bank accounts, loans, contract costs."""
	bankkonten = frappe.get_all(
		"Bankkonto",
		filters={"aktiv": 1},
		fields=["name", "bezeichnung", "bank", "kontotyp", "kontostand_manuell", "waehrung"]
	)

	darlehen = frappe.get_all(
		"Darlehen",
		filters={"aktiv": 1},
		fields=["name", "bezeichnung", "darlehensgeber", "darlehensbetrag", "restschuld",
		        "zinssatz", "monatliche_rate", "ende"]
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
def get_vertrags_ampel():
	"""Return contracts with traffic-light status based on end date / notice period."""
	vertraege = frappe.get_all(
		"Vertrag",
		filters={"aktiv": 1},
		fields=["name", "titel", "vertragstyp", "vertragspartner", "vertragsende", "kuendigungsfrist", "kosten_monatlich", "kosten_jaehrlich"]
	)

	today = datetime.today().date()
	result = []

	for v in vertraege:
		ende = v.vertragsende
		if not ende:
			result.append({**v, "ampel": "gruen", "tage_bis_ende": None, "message": "Kein Enddatum"})
			continue

		if isinstance(ende, str):
			ende = datetime.strptime(ende, "%Y-%m-%d").date()

		tage_bis_ende = (ende - today).days

		if tage_bis_ende < 0:
			result.append({**v, "ampel": "rot", "tage_bis_ende": tage_bis_ende, "message": "Abgelaufen"})
		elif tage_bis_ende <= 30:
			result.append({**v, "ampel": "rot", "tage_bis_ende": tage_bis_ende, "message": f"Endet in {tage_bis_ende} Tagen"})
		elif tage_bis_ende <= 90:
			result.append({**v, "ampel": "gelb", "tage_bis_ende": tage_bis_ende, "message": f"Endet in {tage_bis_ende} Tagen"})
		else:
			result.append({**v, "ampel": "gruen", "tage_bis_ende": tage_bis_ende, "message": f"Endet in {tage_bis_ende} Tagen"})

	return result


@frappe.whitelist()
def get_vermoegensentwicklung():
	"""Return asset overview for wealth calculation."""
	# Immobilienwerte
	immobilien = frappe.get_all(
		"Wohnung",
		fields=["bezeichnung", "aktueller_wert", "kauf_wert", "status"]
	)
	immobilien_wert = sum(w.aktueller_wert or 0 for w in immobilien)

	# Fahrzeuge (nur aktive)
	fahrzeuge = frappe.get_all(
		"Fahrzeug",
		filters={"status": "Aktiv"},
		fields=["kennzeichen", "kaufpreis"]
	)
	fahrzeuge_wert = sum(f.kaufpreis or 0 for f in fahrzeuge)

	# Bankguthaben
	bank_saldo = frappe.db.sql("""
		SELECT COALESCE(SUM(kontostand_manuell), 0) FROM `tabBankkonto` WHERE aktiv = 1
	""")[0][0] or 0

	# Darlehen (Restschuld als negatives Vermögen)
	restschuld = frappe.db.sql("""
		SELECT COALESCE(SUM(restschuld), 0) FROM `tabDarlehen` WHERE aktiv = 1
	""")[0][0] or 0

	# Nettovermögen
	nettovermoegen = immobilien_wert + fahrzeuge_wert + bank_saldo - restschuld

	return {
		"immobilien_wert": immobilien_wert,
		"fahrzeuge_wert": fahrzeuge_wert,
		"bank_saldo": bank_saldo,
		"restschuld": restschuld,
		"nettovermoegen": nettovermoegen,
		"bruttovermoegen": immobilien_wert + fahrzeuge_wert + bank_saldo,
	}
