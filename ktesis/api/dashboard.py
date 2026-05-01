from __future__ import annotations
import frappe
from datetime import datetime, timedelta


@frappe.whitelist()
def get_finance_summary() -> dict:
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
def get_vertrags_ampel() -> list:
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
def get_vermoegensentwicklung() -> dict:
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


@frappe.whitelist()
def get_budget_vs_ist(monat: int, jahr: int) -> list:
    """Return budget vs. actual spending per category for given month/year."""
    from datetime import datetime
    now = datetime.now()
    monat = int(monat or now.month)
    jahr = int(jahr or now.year)

    datum_von = f"{jahr}-{monat:02d}-01"
    if monat == 12:
        datum_bis = f"{jahr+1}-01-01"
    else:
        datum_bis = f"{jahr}-{monat+1:02d}-01"

    # Get budgets
    budgets = frappe.get_all("Budgetposten", fields=["kategorie", "betrag_monatlich"])
    budget_map = {b.kategorie: float(b.betrag_monatlich or 0) for b in budgets}

    # Get actual spending per buchungskategorie
    ist_rows = frappe.db.sql("""
        SELECT buchungskategorie, SUM(ABS(betrag)) as gesamt
        FROM `tabBankbuchung`
        WHERE datum >= %s AND datum < %s
          AND kategorie = 'Ausgang'
          AND buchungskategorie IS NOT NULL AND buchungskategorie != ''
        GROUP BY buchungskategorie
    """, (datum_von, datum_bis), as_dict=True)

    ist_map = {r.buchungskategorie: float(r.gesamt or 0) for r in ist_rows}

    kategorien = ["Wohnen", "Mobilitaet", "Versicherung", "Lebensmittel", "Freizeit", "Einkommen", "Sonstiges"]
    result = []
    for kat in kategorien:
        budget = budget_map.get(kat, 0)
        ist = ist_map.get(kat, 0)
        result.append({
            "kategorie": kat,
            "budget": budget,
            "ist": ist,
            "differenz": budget - ist,
            "ueberschritten": ist > budget and budget > 0,
        })

    return {"monat": monat, "jahr": jahr, "kategorien": result}


@frappe.whitelist()
def get_monatsuebersicht(monat: int, jahr: int) -> dict:
    """Return monthly income, expenses, balance."""
    from datetime import datetime
    now = datetime.now()
    monat = int(monat or now.month)
    jahr = int(jahr or now.year)

    datum_von = f"{jahr}-{monat:02d}-01"
    if monat == 12:
        datum_bis = f"{jahr+1}-01-01"
    else:
        datum_bis = f"{jahr}-{monat+1:02d}-01"

    rows = frappe.db.sql("""
        SELECT kategorie, SUM(ABS(betrag)) as gesamt
        FROM `tabBankbuchung`
        WHERE datum >= %s AND datum < %s
        GROUP BY kategorie
    """, (datum_von, datum_bis), as_dict=True)

    einnahmen = 0.0
    ausgaben = 0.0
    for r in rows:
        if r.kategorie == "Eingang":
            einnahmen = float(r.gesamt or 0)
        elif r.kategorie == "Ausgang":
            ausgaben = float(r.gesamt or 0)

    return {
        "monat": monat,
        "jahr": jahr,
        "einnahmen": einnahmen,
        "ausgaben": ausgaben,
        "saldo": einnahmen - ausgaben,
    }


@frappe.whitelist()
def get_buchungen_verlauf(monate: int = 12) -> list:
    """Return monthly income/expense totals for the last N months."""
    import calendar
    from datetime import date, datetime as dt

    monate = int(monate)
    today = date.today()
    result = []

    for i in range(monate - 1, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        datum_von = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        datum_bis = f"{year}-{month:02d}-{last_day}"

        rows = frappe.db.sql("""
            SELECT kategorie, COALESCE(SUM(ABS(betrag)), 0) as gesamt
            FROM `tabBankbuchung`
            WHERE datum BETWEEN %s AND %s
            GROUP BY kategorie
        """, (datum_von, datum_bis), as_dict=True)

        einnahmen = 0.0
        ausgaben = 0.0
        for r in rows:
            if r.kategorie == "Eingang":
                einnahmen = float(r.gesamt)
            elif r.kategorie == "Ausgang":
                ausgaben = float(r.gesamt)

        label = dt(year, month, 1).strftime("%b %y")
        result.append({
            "label": label,
            "einnahmen": einnahmen,
            "ausgaben": ausgaben,
        })

    return result


@frappe.whitelist()
def get_vertraege_mit_fristen() -> list:
    """Alle Vertraege mit berechneter naechster Kuendigungsfrist und Ampel-Status."""
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    vertraege = frappe.get_all(
        "Vertrag",
        fields=["name", "vertragspartner", "vertragstyp", "vertragsbeginn",
                "vertragsende", "kuendigungsfrist", "kosten_monatlich"],
        order_by="vertragsende asc",
    )

    heute = date.today()
    result = []
    for v in vertraege:
        ende = v.get("vertragsende")
        frist_raw = v.get("kuendigungsfrist") or "1"
        try:
            frist = int(frist_raw)
        except (ValueError, TypeError):
            frist = 1
        naechste_frist = None
        ampel = "gruen"

        if ende:
            from frappe.utils import getdate
            ende_dt = getdate(ende)
            kuendigungs_deadline = ende_dt - relativedelta(months=frist)
            naechste_frist = str(kuendigungs_deadline)

            tage_bis_deadline = (kuendigungs_deadline - heute).days
            if tage_bis_deadline < 0:
                ampel = "abgelaufen"
            elif tage_bis_deadline <= 14:
                ampel = "rot"
            elif tage_bis_deadline <= 60:
                ampel = "gelb"
            else:
                ampel = "gruen"

        result.append({**v, "naechste_kuendigungsfrist": naechste_frist, "ampel": ampel})

    return result
