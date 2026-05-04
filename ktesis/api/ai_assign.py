from __future__ import annotations
import re
import json
import difflib
import urllib.request
import urllib.error
import frappe
from frappe import _
from frappe.utils import getdate, today


def _get_settings() -> dict:
    try:
        d = frappe.db.get_singles_dict("Ktesis Einstellungen")
        aktiv = str(d.get("ki_aktiv") or "0") in ("1", "1.0", "true", "True")
        return {
            "aktiv": aktiv,
            "anbieter": d.get("ki_anbieter") or "opencode",
            "api_url": d.get("ki_api_url") or "https://opencode.ai/zen/go/v1",
            "api_key": d.get("ki_api_key") or "",
            "modell": d.get("ki_modell") or "kimi-k2.6",
        }
    except Exception:
        return {"aktiv": False}


_IBAN_RE = re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b')
_BIC_RE = re.compile(r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b')
_REF_RE = re.compile(r'(EREF|MREF|KREF|SVWZ|CRED|DEBT|ABWA|ABWE)\+[^\s+]+', re.IGNORECASE)
_DATE_RE = re.compile(r'\b\d{2}[.\-/]\d{2}[.\-/]\d{2,4}\b')
_MULTI_SPACE = re.compile(r'\s{2,}')


def _preprocess_buchungstext(text: str) -> str:
    if not text:
        return ""
    auftraggeber = ""
    m = re.search(r'(Auftraggeber|Empfaenger|Zahlungsempfaenger)[:\s]+([^/\n]+)', text, re.IGNORECASE)
    if m:
        auftraggeber = m.group(2).strip()
    verwendung = ""
    m2 = re.search(r'(Verwendungszweck|SVWZ\+)([^\n/]+)', text, re.IGNORECASE)
    if m2:
        verwendung = m2.group(2).strip()
    cleaned = _IBAN_RE.sub('', text)
    cleaned = _BIC_RE.sub('', cleaned)
    cleaned = _REF_RE.sub('', cleaned)
    cleaned = _DATE_RE.sub('', cleaned)
    cleaned = _MULTI_SPACE.sub(' ', cleaned).strip()
    if auftraggeber or verwendung:
        parts = [p for p in [auftraggeber, verwendung] if p]
        return ' - '.join(parts)[:200]
    return cleaned[:200]


def _call_api(url: str, api_key: str, modell: str, messages: list, max_tokens: int = 1024) -> str:
    payload = json.dumps({
        "model": modell,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "ktesis/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        frappe.throw(_(f"HTTP Error {e.code}: {e.reason} — {body}"))
    except Exception as e:
        frappe.throw(_(f"KI-Verbindungsfehler: {e}"))
    msg = data["choices"][0]["message"]
    return (msg.get("content") or msg.get("reasoning") or "").strip()


def _parse_mapping(content: str, n: int, kategorien: list) -> list | None:
    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if not json_match:
        return None
    try:
        mapping = json.loads(json_match.group())
    except json.JSONDecodeError:
        return None
    results = []
    for i in range(n):
        raw = mapping.get(str(i), "Sonstiges")
        matches = difflib.get_close_matches(raw, kategorien, n=1, cutoff=0.6)
        results.append(matches[0] if matches else (raw if raw in kategorien else "Sonstiges"))
    return results


def _classify_batch(texts: list, kategorien: list, settings: dict, beschreibungen: dict = None) -> list:
    base_url = settings.get("api_url", "").rstrip("/")
    api_key = settings.get("api_key", "")
    modell = settings.get("modell", "kimi-k2.6")
    url = f"{base_url}/chat/completions"

    kat_lines = []
    for k in kategorien:
        desc = (beschreibungen or {}).get(k, "")
        kat_lines.append(f"- {k}: {desc}" if desc else f"- {k}")
    kat_text = "\n".join(kat_lines)

    tx_entries = ",\n".join(f'  "{i}": "{t}"' for i, t in enumerate(texts))
    tx_text = "{\n" + tx_entries + "\n}"

    prompt = (
        f"Du bist ein Finanz-Kategorisierungsassistent. Ordne jede Transaktion einer Budgetkategorie zu.\n\n"
        f"KATEGORIEN:\n{kat_text}\n\n"
        f"TRANSAKTIONEN (JSON mit Index als Key):\n{tx_text}\n\n"
        f"Antworte NUR mit validem JSON: {{\"0\": \"Kategorie\", \"1\": \"Kategorie\", ...}}\n"
        f"Nur Kategorienamen aus der obigen Liste verwenden. Kein sonstiger Text."
    )

    content = _call_api(url, api_key, modell, [{"role": "user", "content": prompt}])
    result = _parse_mapping(content, len(texts), kategorien)
    if result is not None:
        return result

    # Fallback: vereinfachter Prompt
    simple_prompt = (
        f"Kategorien: {', '.join(kategorien)}\n\n"
        f"Transaktionen:\n" + "\n".join(f"{i}: {t}" for i, t in enumerate(texts)) +
        f"\n\nJSON-Antwort: {{\"0\": \"Kategorie\", ...}}"
    )
    content2 = _call_api(url, api_key, modell, [{"role": "user", "content": simple_prompt}], max_tokens=512)
    result2 = _parse_mapping(content2, len(texts), kategorien)
    return result2 if result2 is not None else ["Sonstiges"] * len(texts)


def _keyword_assign(buchungstext: str, bp_map: dict):
    KEYWORDS = {
        "Wohnen": ["miete", "nebenkosten", "strom", "gas", "wasser", "heizung", "haus", "wohnung", "grundsteuer"],
        "Mobilitaet": ["tankstelle", "benzin", "diesel", "kfz", "fahrzeug", "auto", "bahn", "bvg", "mvv", "db ", "parken"],
        "Versicherung": ["versicherung", "allianz", "huk", "axa", "debeka", "signal", "beitrag"],
        "Lebensmittel": ["rewe", "edeka", "aldi", "lidl", "kaufland", "netto", "penny", "baeckerei", "metzgerei", "bio"],
        "Freizeit": ["netflix", "spotify", "amazon", "kino", "theater", "restaurant", "cafe", "hotel", "urlaub"],
        "Einkommen": ["gehalt", "lohn", "rente", "erstattung", "rueckzahlung", "steuererstattung"],
    }
    text = (buchungstext or "").lower()
    for kat, keywords in KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return bp_map.get(kat)
    return None


BATCH_SIZE = 20


@frappe.whitelist()
def ai_assign_budgetposten(bankkonto: str = None) -> dict:
    settings = _get_settings()

    bp_list = frappe.get_all("Budgetposten", fields=["name", "kategorie", "ki_beschreibung"])
    bp_map = {b.kategorie: b.name for b in bp_list}
    beschreibungen = {b.kategorie: (b.get("ki_beschreibung") or "") for b in bp_list}
    kategorien = list(bp_map.keys())

    if not kategorien:
        return {"assigned": 0, "method": "none", "error": "Keine Budgetposten gefunden"}

    filters = {"budgetposten": ["is", "not set"]}
    if bankkonto:
        filters["bankkonto"] = bankkonto

    buchungen = frappe.get_all("Bankbuchung", filters=filters, fields=["name", "buchungstext"])
    if not buchungen:
        return {"assigned": 0, "total": 0, "method": "none"}

    assigned = 0
    method = "keyword"

    if settings.get("aktiv") and settings.get("api_key"):
        method = "ki"
        for i in range(0, len(buchungen), BATCH_SIZE):
            batch = buchungen[i:i + BATCH_SIZE]
            texts = [_preprocess_buchungstext(b.buchungstext) for b in batch]
            try:
                ki_kat = _classify_batch(texts, kategorien, settings, beschreibungen)
                for b, kat in zip(batch, ki_kat):
                    bp_name = bp_map.get(kat)
                    if bp_name:
                        frappe.db.set_value("Bankbuchung", b.name, "budgetposten", bp_name)
                        assigned += 1
            except Exception:
                method = "ki_with_fallback"
                for b in batch:
                    bp_name = _keyword_assign(b.buchungstext, bp_map)
                    if bp_name:
                        frappe.db.set_value("Bankbuchung", b.name, "budgetposten", bp_name)
                        assigned += 1
    else:
        for b in buchungen:
            bp_name = _keyword_assign(b.buchungstext, bp_map)
            if bp_name:
                frappe.db.set_value("Bankbuchung", b.name, "budgetposten", bp_name)
                assigned += 1

    frappe.db.commit()
    return {"assigned": assigned, "total": len(buchungen), "method": method}


@frappe.whitelist()
def get_einstellungen() -> dict:
    try:
        d = frappe.db.get_singles_dict("Ktesis Einstellungen")
        return {
            "ki_aktiv": 1 if str(d.get("ki_aktiv") or "0") in ("1", "1.0", "true", "True") else 0,
            "ki_anbieter": d.get("ki_anbieter") or "opencode",
            "ki_api_url": d.get("ki_api_url") or "",
            "ki_modell": d.get("ki_modell") or "",
        }
    except Exception:
        return {"ki_aktiv": 0, "ki_anbieter": "opencode", "ki_api_url": "", "ki_modell": ""}


@frappe.whitelist()
def save_einstellungen(ki_aktiv=None, ki_anbieter=None, ki_api_url=None, ki_api_key=None, ki_modell=None):
    from ktesis.api.auth import is_ktesis_admin
    if not is_ktesis_admin():
        frappe.throw(frappe._("Nur Ktesis Admin darf Einstellungen ändern"), frappe.PermissionError)
    frappe.db.set_single_value("Ktesis Einstellungen", "ki_aktiv",
        1 if str(ki_aktiv or "0") in ("1", "true", "True") else 0)
    frappe.db.set_single_value("Ktesis Einstellungen", "ki_anbieter", ki_anbieter or "opencode")
    frappe.db.set_single_value("Ktesis Einstellungen", "ki_api_url", ki_api_url or "")
    frappe.db.set_single_value("Ktesis Einstellungen", "ki_modell", ki_modell or "")
    if ki_api_key:
        frappe.db.set_single_value("Ktesis Einstellungen", "ki_api_key", ki_api_key)
    frappe.db.commit()
    return {"success": True}


@frappe.whitelist()
def get_ki_models(api_url: str = None, api_key: str = None) -> dict:
    from ktesis.api.auth import is_ktesis_admin
    from urllib.parse import urlparse
    if not is_ktesis_admin():
        frappe.throw(frappe._("Nur Ktesis Admin"), frappe.PermissionError)
    if api_url:
        _host = urlparse(api_url).hostname or ""
        _allowed = {"opencode.ai","api.openai.com","api.anthropic.com","api.mistral.ai",
                    "generativelanguage.googleapis.com","localhost","127.0.0.1"}
        if _host not in _allowed:
            frappe.throw(frappe._("API-URL nicht erlaubt"), frappe.ValidationError)
    d = frappe.db.get_singles_dict("Ktesis Einstellungen")
    if not api_url:
        api_url = d.get("ki_api_url") or "https://opencode.ai/zen/go/v1"
    if not api_key:
        api_key = d.get("ki_api_key") or ""
    url = api_url.rstrip("/") + "/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "ktesis/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = [m.get("id") or m.get("name") for m in data.get("data", [])]
        return {"models": [m for m in models if m]}
    except urllib.error.HTTPError as e:
        e.read()
        frappe.throw(_(f"HTTP Error {e.code}: {e.reason}"))
    except Exception as e:
        frappe.throw(_(f"Verbindungsfehler: {e}"))


@frappe.whitelist()
def delete_all_buchungen() -> dict:
    from ktesis.api.auth import is_ktesis_admin
    if not is_ktesis_admin():
        frappe.throw(_("Nur Ktesis Admin darf alle Buchungen löschen"), frappe.PermissionError)
    count = frappe.db.count("Bankbuchung")
    frappe.db.sql("DELETE FROM `tabBankbuchung`")
    frappe.db.commit()
    frappe.log_error(f"Alle {count} Bankbuchungen gelöscht von {frappe.session.user}", "Ktesis Admin Action")
    return {"deleted": count}


@frappe.whitelist()
@frappe.whitelist()
def start_ki_zuweisung():
    """Startet KI-Hintergrund-Job fuer automatische Buchungs-Kategorisierung"""
    from ktesis.api.auth import is_ktesis_admin
    if not is_ktesis_admin():
        frappe.throw(frappe._("Nur Ktesis Admin"), frappe.PermissionError)
    # Pruefe ob schon ein Job laeuft
    running = frappe.db.get_value("RQ Job",
        {"job_name": "ki_zuweisung", "status": ["in", ["queued", "started"]]}, "name")
    if running:
        return {"status": "already_running", "job_id": running}
    frappe.enqueue(
        "ktesis.api.ai_assign.run_ki_zuweisung_job",
        queue="long",
        job_name="ki_zuweisung",
        timeout=3600
    )
    return {"status": "started"}

@frappe.whitelist()
def get_ki_zuweisung_status():
    """Gibt Status des laufenden KI-Jobs zurueck (via Cache)"""
    progress = frappe.cache().get_value("ki_zuweisung_progress") or {}
    if not progress:
        return {"status": "idle", "done": 0, "total": 0}
    return progress

def run_ki_zuweisung_job():
    """Hintergrund-Job: Regeln anwenden, dann KI fuer Rest"""
    import frappe as _frappe
    # Schritt 1: Regeln anwenden
    from ktesis.api.buchungsregel import apply_buchungsregeln
    result = apply_buchungsregeln()

    # Schritt 2: Verbleibende offene Buchungen via KI
    offene = _frappe.get_all("Bankbuchung",
        filters=[["budgetposten", "is", "not set"]],
        fields=["name", "buchungstext", "betrag"],
        limit=200
    )
    total = len(offene)
    if total == 0:
        return

    def _set_progress(done, total, status="running"):
        _frappe.cache().set_value("ki_zuweisung_progress",
            {"status": status, "done": done, "total": total}, expires_in_sec=3600)

    _set_progress(0, total)

    # Budgettoepfe fuer Kontext laden — nutze kategorie als key (nicht titel)
    budgetposten_list = _frappe.get_all("Budgetposten", fields=["name", "kategorie"], limit=50)
    bp_map = {b.kategorie: b.name for b in budgetposten_list if b.kategorie}

    # Batch-Verarbeitung (10 pro Call)
    batch_size = 10
    done = 0
    for i in range(0, total, batch_size):
        batch = offene[i:i+batch_size]
        try:
            for b in batch:
                result = _keyword_assign(b.buchungstext, bp_map)
                if result:
                    _frappe.db.set_value("Bankbuchung", b.name, "budgetposten", result)
            done += len(batch)
            _set_progress(done, total)
        except Exception as e:
            _frappe.log_error(str(e), "KI Zuweisung Batch Error")

    _frappe.db.commit()
    _set_progress(done, total, status="finished")

def _ki_assign_batch(buchungen, budgetposten):
    """KI-Call fuer einen Batch von Buchungen - Stub, nutzt bestehende ai_assign Logik"""
    # Nutzt die bestehende ai_assign_budgetposten Logik als Fallback
    bp_map = {b.titel: b.name for b in budgetposten}
    for b in buchungen:
        result = _keyword_assign(b.buchungstext, bp_map)
        if result:
            frappe.db.set_value("Bankbuchung", b.name, "budgetposten", result)
