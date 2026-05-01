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
}


def _parse_german_amount(amount_str):
    if not amount_str:
        return None
    cleaned = amount_str.strip().strip('"').replace("\xa0", "").replace(" ", "")
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(date_str):
    date_str = date_str.strip().strip('"')
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            from datetime import datetime
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _decode_csv(raw_bytes):
    for enc in ["utf-8-sig", "utf-8", "iso-8859-1", "cp1252"]:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, AttributeError):
            continue
    return raw_bytes.decode("iso-8859-1", errors="replace")


def _find_header_row(lines):
    for i, line in enumerate(lines[:15]):
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
def preview_csv(bankkonto, csv_content):
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

    data_lines = lines[header_idx:]
    reader = csv.DictReader(io.StringIO("\n".join(data_lines)), delimiter=fmt.get("delimiter", ";"))
    rows = []
    for i, row in enumerate(reader):
        if i >= 5:
            break
        date_str = _get_col(row, [fmt["date_col"]])
        betrag_str = _get_col(row, [fmt["amount_col"]])
        buchungstext = _get_col(row, fmt["text_cols"])
        betrag = _parse_german_amount(betrag_str)
        datum = _parse_date(date_str)
        if not datum or betrag is None:
            continue
        rows.append({
            "datum": datum,
            "buchungstext": buchungstext[:140],
            "betrag": betrag,
            "kategorie": "Eingang" if betrag > 0 else "Ausgang",
        })
    return {"format": fmt_name, "rows": rows}


@frappe.whitelist()
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


def import_bankbuchungen(bankkonto, csv_content):
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
            betrag = _parse_german_amount(betrag_str)
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
            })
            doc.insert(ignore_permissions=True)
            imported += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:100]}")

    frappe.db.commit()
    return {"imported": imported, "duplicates": duplicates, "errors": errors, "format": fmt_name}
