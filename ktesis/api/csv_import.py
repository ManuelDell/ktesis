from __future__ import annotations
import csv
import io
import frappe
from frappe import _
from frappe.utils import getdate, today


BANK_FORMATS = {
    "dkb": {
        "detect": lambda h: "Buchungstag" in h and ("Betrag (EUR)" in h or "Glaeubiger-ID" in h),
        "date_col": "Buchungstag",
        "text_cols": ["Auftraggeber / Beguenstigter", "Auftraggeber/Beguenstigter", "Buchungstext"],
        "amount_col": "Betrag (EUR)",
        "delimiter": ";",
    },
    "sparkasse": {
        "detect": lambda h: "Auftragskonto" in h and "Buchungstag" in h,
        "date_col": "Buchungstag",
        "text_cols": ["Verwendungszweck", "Buchungstext", "Auftraggeber/Zahlungsempfaenger"],
        "amount_col": "Betrag",
        "delimiter": ";",
    },
    "ing": {
        "detect": lambda h: "Buchung" in h and "Valuta" in h and "Auftraggeber" in h,
        "date_col": "Buchung",
        "text_cols": ["Buchungstext", "Verwendungszweck"],
        "amount_col": "Betrag",
        "delimiter": ";",
    },
    "comdirect": {
        "detect": lambda h: "Umsatz in EUR" in h,
        "date_col": "Buchungstag",
        "text_cols": ["Buchungstext", "Vorgang"],
        "amount_col": "Umsatz in EUR",
        "delimiter": ";",
    },
    "commerzbank": {
        "detect": lambda h: "Betrag EUR" in h and "Auftraggeber / Begünstigter" in h,
        "date_col": "Buchungstag",
        "text_cols": ["Buchungstext", "Auftraggeber / Begünstigter", "Verwendungszweck"],
        "amount_col": "Betrag EUR",
        "delimiter": ";",
    },
    "deutsche_bank": {
        "detect": lambda h: "Umsatzart" in h and "Betrag EUR" in h,
        "date_col": "Buchungstag",
        "text_cols": ["Verwendungszweck", "Begünstigter / Auftraggeber", "Umsatzart"],
        "amount_col": "Betrag EUR",
        "delimiter": ";",
    },
    "n26": {
        "detect": lambda h: "Transaktionstyp" in h,
        "date_col": "Datum",
        "text_cols": ["Empfänger", "Verwendungszweck", "Transaktionstyp"],
        "amount_col": "Betrag (EUR)",
        "delimiter": ",",
        "decimal_sep": ".",
    },
    "trade_republic": {
        "detect": lambda h: "ISIN" in h and ("Betrag" in h or "Betrag (EUR)" in h),
        "date_col": "Datum",
        "text_cols": ["Beschreibung", "Typ", "Wertpapiername"],
        "amount_col": "Betrag (EUR)",
        "delimiter": ";",
    },
}


def _parse_german_amount(s: str, decimal_sep: str = ",") -> float:
    if not s:
        return None
    cleaned = s.strip().strip('"').replace("\xa0", "").replace(" ", "")
    if decimal_sep == ".":
        # English format (N26): remove thousands comma, dot is decimal
        cleaned = cleaned.replace(",", "")
    else:
        # German format: remove thousands dot, replace decimal comma with dot
        cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(s: str) -> str:
    s = s.strip().strip('"')
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _decode_csv(content: bytes) -> str:
    for enc in ["utf-8-sig", "utf-8", "iso-8859-1", "cp1252"]:
        try:
            return content.decode(enc)
        except (UnicodeDecodeError, AttributeError):
            continue
    return content.decode("iso-8859-1", errors="replace")


def _find_header_row(rows: list) -> int:
    for i, line in enumerate(rows[:15]):
        if any(k in line for k in ["Buchungstag", "Auftragskonto", "Buchung", "Datum"]):
            return i
    return 0


def _detect_format(header_line):
    for fmt_name, fmt in BANK_FORMATS.items():
        if fmt["detect"](header_line):
            return fmt_name, fmt
    return None, None


def _get_col(row, candidates):
    for c in candidates:
        if c in row and row[c].strip():
            return row[c].strip().strip('"')
    for c in candidates:
        for key in row:
            if c.lower() in key.lower() and row[key].strip():
                return row[key].strip().strip('"')
    return ""


@frappe.whitelist()
def preview_csv(bankkonto: str, csv_content: str) -> dict:
    frappe.get_doc("Bankkonto", bankkonto)
    if isinstance(csv_content, str):
        raw = csv_content.encode("utf-8")
    else:
        raw = csv_content

    text = _decode_csv(raw)
    lines = text.splitlines()
    header_idx = _find_header_row(lines)
    header_line = lines[header_idx] if lines else ""
    fmt_name, fmt = _detect_format(header_line)
    if not fmt_name:
        frappe.throw(_("CSV-Format nicht erkannt. Unterstützt: DKB, Sparkasse, ING, Comdirect, Commerzbank, Deutsche Bank, N26, Trade Republic"))

    decimal_sep = fmt.get("decimal_sep", ",")
    reader = csv.DictReader(io.StringIO("\n".join(lines[header_idx:])), delimiter=fmt.get("delimiter", ";"))

    # Budgetposten-Mapping: buchungskategorie → Budgetposten-Name
    bp_list = frappe.get_all("Budgetposten", fields=["name", "kategorie"])
    bp_map = {b.kategorie: b.name for b in bp_list}

    # Vorab alle existierenden Buchungen für schnellen Duplicate-Check laden
    existing = set(
        (d[0], d[1], float(d[2]))
        for d in frappe.db.sql(
            "SELECT datum, buchungstext, betrag FROM `tabBankbuchung` WHERE bankkonto = %s",
            (bankkonto,)
        )
    )

    rows = []
    for row in reader:
        date_str = _get_col(row, [fmt["date_col"]])
        betrag_str = _get_col(row, [fmt["amount_col"]])
        buchungstext = _get_col(row, fmt["text_cols"])
        betrag = _parse_german_amount(betrag_str, decimal_sep)
        if date_str and date_str.strip().lower() == "offen":
            datum = None
        else:
            datum = _parse_date(date_str)
        if betrag is None or betrag == 0:
            continue
        if not buchungstext:
            buchungstext = f"Buchung {datum or 'offen'}"
        buchungskategorie = _auto_kategorisieren(buchungstext)
        is_duplicate = False
        if datum:
            is_duplicate = (datum, buchungstext[:140], betrag) in existing
        rows.append({
            "datum": datum,
            "buchungstext": buchungstext[:140],
            "betrag": betrag,
            "kategorie": "Eingang" if betrag > 0 else "Ausgang",
            "buchungskategorie": buchungskategorie,
            "budgetposten": bp_map.get(buchungskategorie, ""),
            "duplicate": is_duplicate,
        })
    return {"format": fmt_name, "rows": rows}


KATEGORIE_KEYWORDS = {
    "Wohnen": ["miete", "nebenkosten", "strom", "gas", "wasser", "heizung", "haus", "wohnung", "grundsteuer"],
    "Mobilitaet": ["tankstelle", "benzin", "diesel", "öl", "rewe", "edeka", "supermarkt", "kfz", "tüv", "fahrzeug", "auto", "bahn", "bvg", "mvv", "db ", "parken"],
    "Versicherung": ["versicherung", "allianz", "huk", "axa", "debeka", "signal", "beitrag"],
    "Lebensmittel": ["rewe", "edeka", "aldi", "lidl", "kaufland", "netto", "penny", "bäckerei", "metzgerei", "bio"],
    "Freizeit": ["netflix", "spotify", "amazon prime", "kino", "theater", "restaurant", "cafe", "hotel", "urlaub"],
    "Einkommen": ["gehalt", "lohn", "rente", "erstattung", "rueckzahlung", "steuererstattung"],
}

def _auto_kategorisieren(buchungstext):
    text = buchungstext.lower()
    for kat, keywords in KATEGORIE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return kat
    return "Sonstiges"



@frappe.whitelist()
def import_bankbuchungen(bankkonto, csv_content):
    frappe.get_doc("Bankkonto", bankkonto)  # raises if not found or no permission
    if isinstance(csv_content, str):
        raw = csv_content.encode("utf-8")
    else:
        raw = csv_content

    text = _decode_csv(raw)
    lines = text.splitlines()
    header_idx = _find_header_row(lines)
    header_line = lines[header_idx] if lines else ""
    fmt_name, fmt = _detect_format(header_line)

    if not fmt_name:
        frappe.throw(_("CSV-Format nicht erkannt. Unterstuetzt: DKB, Sparkasse, ING"))

    today_date = getdate(today())
    decimal_sep = fmt.get("decimal_sep", ",")
    reader = csv.DictReader(
        io.StringIO("\n".join(lines[header_idx:])),
        delimiter=fmt.get("delimiter", ";")
    )
    imported = 0
    duplicates = 0
    errors = []

    for i, row in enumerate(reader):
        try:
            date_str = _get_col(row, [fmt["date_col"]])
            betrag_str = _get_col(row, [fmt["amount_col"]])
            buchungstext = _get_col(row, fmt["text_cols"])
            betrag = _parse_german_amount(betrag_str, decimal_sep)
            datum = _parse_date(date_str)
            if not datum or betrag is None or betrag == 0:
                continue
            if not buchungstext:
                buchungstext = f"Buchung {datum}"
            if getdate(datum) > today_date:
                errors.append(f"Zeile {i+2}: Datum in der Zukunft, uebersprungen")
                continue
            exists = frappe.db.exists("Bankbuchung", {
                "bankkonto": bankkonto,
                "datum": datum,
                "buchungstext": buchungstext[:140],
                "betrag": betrag,
            })
            if exists:
                duplicates += 1
                continue
            doc = frappe.get_doc({
                "doctype": "Bankbuchung",
                "bankkonto": bankkonto,
                "datum": datum,
                "buchungstext": buchungstext[:140],
                "betrag": betrag,
                "kategorie": "Eingang" if betrag > 0 else "Ausgang",
                "buchungskategorie": _auto_kategorisieren(buchungstext),
            })
            doc.insert()
            imported += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:100]}")

    frappe.db.commit()
    return {"imported": imported, "duplicates": duplicates, "errors": errors, "format": fmt_name}


@frappe.whitelist()
def import_bankbuchungen_rows(bankkonto: str, rows: str | list) -> dict:
    """Import pre-processed rows (from preview_csv) with user-edited budgetposten."""
    frappe.get_doc("Bankkonto", bankkonto)
    if isinstance(rows, str):
        import json
        rows = json.loads(rows)

    today_date = getdate(today())
    imported = 0
    duplicates = 0
    errors = []

    for i, row in enumerate(rows):
        if row.get("duplicate"):
            duplicates += 1
            continue
        try:
            datum = row.get("datum")
            betrag = float(row.get("betrag", 0))
            buchungstext = (row.get("buchungstext") or "")[:140]
            if not datum or betrag == 0:
                continue
            if getdate(datum) > today_date:
                errors.append(f"Zeile {i+1}: Datum in der Zukunft, übersprungen")
                continue
            already = frappe.db.exists("Bankbuchung", {
                "bankkonto": bankkonto,
                "datum": datum,
                "buchungstext": buchungstext,
                "betrag": betrag,
            })
            if already:
                duplicates += 1
                continue
            doc = frappe.get_doc({
                "doctype": "Bankbuchung",
                "bankkonto": bankkonto,
                "datum": datum,
                "buchungstext": buchungstext,
                "betrag": betrag,
                "kategorie": row.get("kategorie", "Ausgang"),
                "buchungskategorie": row.get("buchungskategorie", "Sonstiges"),
                "budgetposten": row.get("budgetposten") or None,
            })
            doc.insert()
            imported += 1
        except Exception as e:
            errors.append(f"Zeile {i+1}: {str(e)[:100]}")

    frappe.db.commit()
    return {"imported": imported, "duplicates": duplicates, "errors": errors}

@frappe.whitelist()
def auto_assign_budgetposten(bankkonto: str = None) -> dict:
    """Auto-assign budgetposten to all Bankbuchungen without one, using category matching."""
    bp_list = frappe.get_all("Budgetposten", fields=["name", "kategorie"])
    bp_map = {b.kategorie: b.name for b in bp_list}
    if not bp_map:
        return {"assigned": 0}

    filters = {"budgetposten": ["is", "not set"], "kategorie": "Ausgang"}
    if bankkonto:
        filters["bankkonto"] = bankkonto

    buchungen = frappe.get_all("Bankbuchung", filters=filters, fields=["name", "buchungstext"])
    assigned = 0
    for b in buchungen:
        bp_name = bp_map.get(_auto_kategorisieren(b.buchungstext))
        if bp_name:
            frappe.db.set_value("Bankbuchung", b.name, "budgetposten", bp_name)
            assigned += 1

    frappe.db.commit()
    return {"assigned": assigned}
