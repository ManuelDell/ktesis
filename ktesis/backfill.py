import frappe
from frappe.utils import today, add_years

def create_demo_data():
	frappe.db.commit()

	# --- Lösche alte Demo-Daten (idempotent) ---
	for dt in ["Vertrag", "Darlehen", "Bankkonto", "Wohnung", "Fahrzeug"]:
		for name in frappe.get_all(dt, pluck="name"):
			try:
				frappe.delete_doc(dt, name, force=1)
			except Exception:
				pass
	frappe.db.commit()

	# --- Fahrzeuge ---
	fz1 = frappe.get_doc({
		"doctype": "Fahrzeug",
		"kennzeichen": "B-XY 1234",
		"marke": "BMW",
		"modell": "320d Touring",
		"baujahr": 2019,
		"farbe": "Alpinweiß",
		"fin": "WBA1234567890ABCDE",
		"erstzulassung": "2019-06-15",
		"kaufpreis": 28500,
		"kaufdatum": "2021-03-10",
		"kilometerstand_kauf": 45000,
		"aktueller_km_stand": 78000,
		"kraftstoff": "Diesel",
		"leistung_ps": 190,
		"hubraum": 1995,
		"status": "Aktiv"
	}).insert()

	fz2 = frappe.get_doc({
		"doctype": "Fahrzeug",
		"kennzeichen": "B-AB 5678",
		"marke": "Volkswagen",
		"modell": "Golf 8 GTI",
		"baujahr": 2022,
		"farbe": "Kings Red Metallic",
		"fin": "WVWZZZCDZNW123456",
		"erstzulassung": "2022-01-20",
		"kaufpreis": 38000,
		"kaufdatum": "2022-02-15",
		"kilometerstand_kauf": 0,
		"aktueller_km_stand": 25000,
		"kraftstoff": "Benzin",
		"leistung_ps": 245,
		"hubraum": 1984,
		"status": "Aktiv"
	}).insert()

	fz3 = frappe.get_doc({
		"doctype": "Fahrzeug",
		"kennzeichen": "B-CD 9012",
		"marke": "Tesla",
		"modell": "Model 3",
		"baujahr": 2023,
		"farbe": "Midnight Silver",
		"fin": "5YJ3E1EA8PF000001",
		"erstzulassung": "2023-08-01",
		"kaufpreis": 42990,
		"kaufdatum": "2023-08-15",
		"kilometerstand_kauf": 1200,
		"aktueller_km_stand": 18500,
		"kraftstoff": "Elektro",
		"leistung_ps": 325,
		"status": "Aktiv"
	}).insert()

	# --- Wohnungen ---
	whg1 = frappe.get_doc({
		"doctype": "Wohnung",
		"bezeichnung": "Eigentumswohnung Berlin-Mitte",
		"strasse": "Alexanderplatz",
		"hausnummer": "1",
		"plz": "10178",
		"ort": "Berlin",
		"land": "Deutschland",
		"wohnflaeche": 85.5,
		"zimmer": 3.5,
		"baujahr": 2015,
		"kaufpreis": 450000,
		"kaufdatum": "2020-05-01",
		"kauf_wert": 450000,
		"aktueller_wert": 520000,
		"wohnungstyp": "Eigentumswohnung",
		"status": "Bewohnt",
		"abschreibungen": [
			{"jahr": 2020, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 441000, "bemerkung": "Erstjahr"},
			{"jahr": 2021, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 432000},
			{"jahr": 2022, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 423000},
			{"jahr": 2023, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 414000},
			{"jahr": 2024, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 405000},
			{"jahr": 2025, "abschreibungssatz": 2.0, "abschreibungsbetrag": 9000, "restbuchwert": 396000},
		]
	}).insert()

	whg2 = frappe.get_doc({
		"doctype": "Wohnung",
		"bezeichnung": "Reihenhaus Potsdam",
		"strasse": "Am Großen Holländer",
		"hausnummer": "12a",
		"plz": "14467",
		"ort": "Potsdam",
		"land": "Deutschland",
		"wohnflaeche": 145.0,
		"zimmer": 5.0,
		"baujahr": 2010,
		"kaufpreis": 680000,
		"kaufdatum": "2018-09-01",
		"kauf_wert": 680000,
		"aktueller_wert": 750000,
		"wohnungstyp": "Reihenhaus",
		"status": "Vermietet",
		"abschreibungen": [
			{"jahr": 2018, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 666400, "bemerkung": "Erstjahr"},
			{"jahr": 2019, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 652800},
			{"jahr": 2020, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 639200},
			{"jahr": 2021, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 625600},
			{"jahr": 2022, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 612000},
			{"jahr": 2023, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 598400},
			{"jahr": 2024, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 584800},
			{"jahr": 2025, "abschreibungssatz": 2.0, "abschreibungsbetrag": 13600, "restbuchwert": 571200},
		]
	}).insert()

	# --- Darlehen ---
	dlh1 = frappe.get_doc({
		"doctype": "Darlehen",
		"bezeichnung": "Annuitätendarlehen Berlin",
		"wohnung": whg1.name,
		"darlehensgeber": "Deutsche Bank AG",
		"darlehensnummer": "DL-2020-88421",
		"darlehensbetrag": 350000,
		"zinssatz": 1.85,
		"tilgungssatz": 2.0,
		"monatliche_rate": 1122.92,
		"rate_inkl_zins_tilgung": 1,
		"laufzeit_jahre": 30,
		"beginn": "2020-06-01",
		"ende": "2050-06-01",
		"restschuld": 298450,
		"tilgungsfreie_jahre": 0,
		"sollzinsbindung_bis": "2030-06-01",
		"aktiv": 1
	}).insert()

	dlh2 = frappe.get_doc({
		"doctype": "Darlehen",
		"bezeichnung": "Bausparer + Darlehen Potsdam",
		"wohnung": whg2.name,
		"darlehensgeber": "LBS Bausparkasse",
		"darlehensnummer": "BS-2018-11299",
		"darlehensbetrag": 500000,
		"zinssatz": 2.15,
		"tilgungssatz": 1.5,
		"monatliche_rate": 1520.83,
		"rate_inkl_zins_tilgung": 1,
		"laufzeit_jahre": 25,
		"beginn": "2018-10-01",
		"ende": "2043-10-01",
		"restschuld": 412000,
		"tilgungsfreie_jahre": 0,
		"sollzinsbindung_bis": "2028-10-01",
		"aktiv": 1
	}).insert()

	# --- Bankkonten ---
	bk1 = frappe.get_doc({
		"doctype": "Bankkonto",
		"bezeichnung": "Hauptgirokonto Privat",
		"bank": "Deutsche Bank AG",
		"iban": "DE02200400600515474757",
		"bic": "DEUTDEDBBER",
		"blz": "37040044",
		"kontonummer": "0515474757",
		"kontostand_manuell": 12450.35,
		"kontotyp": "Girokonto",
		"waehrung": "EUR",
		"fints_aktiv": 0,
		"aktiv": 1
	}).insert()

	bk2 = frappe.get_doc({
		"doctype": "Bankkonto",
		"bezeichnung": "Tagesgeld Plus",
		"bank": "ING-DiBa",
		"iban": "DE02300606010002474689",
		"bic": "INGDDEFFXXX",
		"blz": "51210800",
		"kontonummer": "0002474689",
		"kontostand_manuell": 85000.00,
		"kontotyp": "Tagesgeld",
		"waehrung": "EUR",
		"fints_aktiv": 0,
		"aktiv": 1
	}).insert()

	# --- Verträge ---
	v1 = frappe.get_doc({
		"doctype": "Vertrag",
		"titel": "KFZ-Vollkasko BMW",
		"vertragstyp": "Versicherung",
		"referenz_doctype": "Fahrzeug",
		"referenz_name": fz1.name,
		"vertragspartner": "HUK-COBURG",
		"vertragsnummer": "VK-2021-8844221",
		"vertragsbeginn": "2021-03-15",
		"vertragsende": "2026-03-15",
		"kuendigungsfrist": "3 Monate",
		"kosten_monatlich": 85.50,
		"kosten_jaehrlich": 1026.00,
		"zahlungsrhythmus": "Jährlich",
		"aktiv": 1
	}).insert()

	v2 = frappe.get_doc({
		"doctype": "Vertrag",
		"titel": "Darlehensvertrag Berlin",
		"vertragstyp": "Darlehen",
		"referenz_doctype": "Wohnung",
		"referenz_name": whg1.name,
		"vertragspartner": "Deutsche Bank AG",
		"vertragsnummer": "DL-2020-88421",
		"vertragsbeginn": "2020-06-01",
		"vertragsende": "2050-06-01",
		"kuendigungsfrist": "Sonderkündigung nach 10 Jahren",
		"kosten_monatlich": 1122.92,
		"kosten_jaehrlich": 13475.04,
		"zahlungsrhythmus": "Monatlich",
		"aktiv": 1
	}).insert()

	v3 = frappe.get_doc({
		"doctype": "Vertrag",
		"titel": "Wohngebäudeversicherung Potsdam",
		"vertragstyp": "Versicherung",
		"referenz_doctype": "Wohnung",
		"referenz_name": whg2.name,
		"vertragspartner": "Allianz Versicherung",
		"vertragsnummer": "WG-2018-99123",
		"vertragsbeginn": "2018-09-01",
		"vertragsende": "2028-09-01",
		"kuendigungsfrist": "3 Monate",
		"kosten_monatlich": 45.00,
		"kosten_jaehrlich": 540.00,
		"zahlungsrhythmus": "Jährlich",
		"aktiv": 1
	}).insert()

	v4 = frappe.get_doc({
		"doctype": "Vertrag",
		"titel": "Inspektionsvertrag Tesla",
		"vertragstyp": "Wartung",
		"referenz_doctype": "Fahrzeug",
		"referenz_name": fz3.name,
		"vertragspartner": "Tesla Service Center Berlin",
		"vertragsnummer": "SV-2023-4455",
		"vertragsbeginn": "2023-08-15",
		"vertragsende": "2026-08-15",
		"kuendigungsfrist": "1 Monat",
		"kosten_monatlich": 0,
		"kosten_jaehrlich": 299.00,
		"zahlungsrhythmus": "Jährlich",
		"aktiv": 1
	}).insert()

	frappe.db.commit()

	print("=" * 50)
	print("Demo-Daten erfolgreich erstellt!")
	print("=" * 50)
	print(f"Fahrzeuge:     3 ({fz1.name}, {fz2.name}, {fz3.name})")
	print(f"Wohnungen:     2 ({whg1.name}, {whg2.name})")
	print(f"Darlehen:      2 ({dlh1.name}, {dlh2.name})")
	print(f"Bankkonten:    2 ({bk1.name}, {bk2.name})")
	print(f"Vertr\u00e4ge:       4 ({v1.name}, {v2.name}, {v3.name}, {v4.name})")
	print("=" * 50)
