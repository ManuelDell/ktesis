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
	vertraege_raw = frappe.get_all(
		"Vertrag",
		filters={"aktiv": 1},
		fields=["name", "titel", "vertragstyp", "vertragspartner",
		        "kosten_monatlich", "kosten_jaehrlich", "zahlungsrhythmus", "vertragsbeginn"],
		order_by="titel asc"
	)
	monatlich_gesamt = 0.0
	jaehrlich_gesamt = 0.0
	for v in vertraege_raw:
		km = float(v.kosten_monatlich or 0)
		kj = float(v.kosten_jaehrlich or 0)
		r = (v.zahlungsrhythmus or "").strip()
		if r == "Einmalig":
			continue
		# Monthly equivalent: use kosten_monatlich if set, else derive from jaehrlich
		m = km if km else (kj / 12 if kj else 0)
		# Annual equivalent: use kosten_jaehrlich if set, else derive from monatlich
		j = kj if kj else (km * 12 if km else 0)
		monatlich_gesamt += m
		jaehrlich_gesamt += j
	vertraege_list = [
		{"name": v.name, "titel": v.titel, "vertragstyp": v.vertragstyp,
		 "vertragspartner": v.vertragspartner,
		 "kosten_monatlich": float(v.kosten_monatlich or 0),
		 "kosten_jaehrlich": float(v.kosten_jaehrlich or 0),
		 "zahlungsrhythmus": v.zahlungsrhythmus or "",
		 "vertragsbeginn": str(v.vertragsbeginn) if v.vertragsbeginn else ""}
		for v in vertraege_raw
	]
	return {
		"bankkonten": bankkonten,
		"darlehen": darlehen,
		"vertragskosten": {
			"monatlich": round(monatlich_gesamt, 2),
			"jaehrlich": round(jaehrlich_gesamt, 2),
			"vertraege": vertraege_list,
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
def get_budget_vs_ist(monat: int = None, jahr: int = None) -> dict:
    """Return budget vs. actual spending. Aggregates by budgetposten link OR buchungskategorie fallback."""
    from datetime import datetime
    now = datetime.now()
    monat = int(monat or now.month)
    jahr = int(jahr or now.year)

    datum_von = f"{jahr}-{monat:02d}-01"
    datum_bis = f"{jahr+1}-01-01" if monat == 12 else f"{jahr}-{monat+1:02d}-01"

    budgets = frappe.get_all("Budgetposten", fields=["name", "kategorie", "betrag_monatlich"])
    budget_map = {b.name: {"kategorie": b.kategorie, "budget": float(b.betrag_monatlich or 0)} for b in budgets}

    # Aggregate by budgetposten link (primary)
    linked_rows = frappe.db.sql("""
        SELECT budgetposten, SUM(betrag) as gesamt
        FROM `tabBankbuchung`
        WHERE datum >= %s AND datum < %s
          AND budgetposten IS NOT NULL AND budgetposten != ''
        GROUP BY budgetposten
    """, (datum_von, datum_bis), as_dict=True)
    linked_map = {r.budgetposten: float(r.gesamt or 0) for r in linked_rows}

    # Aggregate by buchungskategorie (fallback for unlinked bookings)
    fallback_rows = frappe.db.sql("""
        SELECT buchungskategorie, SUM(betrag) as gesamt
        FROM `tabBankbuchung`
        WHERE datum >= %s AND datum < %s
          AND (budgetposten IS NULL OR budgetposten = '')
          AND buchungskategorie IS NOT NULL AND buchungskategorie != ''
        GROUP BY buchungskategorie
    """, (datum_von, datum_bis), as_dict=True)
    fallback_map = {r.buchungskategorie: float(r.gesamt or 0) for r in fallback_rows}

    # Dynamisch: alle Kategorien aus Budgetposten + Kategorien aus Buchungen ohne Budget
    alle_kat = [b.kategorie for b in budgets]
    for kat in list(linked_map.keys()) + list(fallback_map.keys()):
        bp_kat = next((b.kategorie for b in budgets if b.name == kat), kat)
        if bp_kat not in alle_kat:
            alle_kat.append(bp_kat)
    result = []
    seen = set()
    for kat in alle_kat:
        if kat in seen:
            continue
        seen.add(kat)
        bp = next((b for b in budgets if b.kategorie == kat), None)
        budget = float(bp.betrag_monatlich or 0) if bp else 0
        ist_linked = linked_map.get(bp.name, 0) if bp else 0
        ist_fallback = fallback_map.get(kat, 0)
        ist = ist_linked + ist_fallback
        result.append({
            "kategorie": kat,
            "budget": budget,
            "ist": ist,
            "differenz": budget - ist,
            "ueberschritten": ist > budget and budget > 0,
        })

    return {"kategorien": result}


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
        SELECT kategorie, SUM(betrag) as gesamt
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
            SELECT kategorie, COALESCE(SUM(betrag), 0) as gesamt
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
