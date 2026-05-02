from __future__ import annotations
import json
import frappe
from frappe import _


def _get_settings() -> dict:
    """Load KI settings from KtesisEinstellungen Single DocType."""
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


def _classify_batch(texts: list[str], kategorien: list[str], settings: dict) -> list[str]:
    """Send batch of texts to AI, return list of assigned categories."""
    import urllib.request

    base_url = settings["api_url"].rstrip("/")
    api_key = settings["api_key"]
    modell = settings["modell"]

    kat_list = "\n".join(f"- {k}" for k in kategorien)
    items = "\n".join(f'{i+1}. "{t}"' for i, t in enumerate(texts))

    system_prompt = (
        "Du bist ein Finanz-Kategorisierer. "
        "Ordne jeden Buchungstext einer der gegebenen Kategorien zu. "
        "Antworte NUR mit einem JSON-Array der Kategorienamen, ein Eintrag pro Buchungstext. "
        "Beispiel: [\"Lebensmittel\", \"Wohnen\", \"Sonstiges\"]"
    )

    user_prompt = (
        f"Kategorien:\n{kat_list}\n\n"
        f"Buchungstexte:\n{items}\n\n"
        f"Antworte mit einem JSON-Array mit genau {len(texts)} Einträgen."
    )

    payload = json.dumps({
        "model": modell,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": 512,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"].strip()
        # Extract JSON array from response (may have markdown fences)
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            result = json.loads(content[start:end])
            if isinstance(result, list) and len(result) == len(texts):
                return [str(r) for r in result]
    except Exception as e:
        frappe.log_error(f"AI classify error: {e}", "ai_assign")

    return ["Sonstiges"] * len(texts)


@frappe.whitelist()
def ai_assign_budgetposten(bankkonto: str = None) -> dict:
    """Assign budgetposten using AI categorization (OpenAI-compatible API)."""
    settings = _get_settings()
    if not settings.get("aktiv"):
        # Fall back to keyword matching
        from ktesis.api.csv_import import auto_assign_budgetposten
        return auto_assign_budgetposten(bankkonto=bankkonto)

    # Load Budgetposten
    bp_list = frappe.get_all("Budgetposten", fields=["name", "kategorie"])
    if not bp_list:
        return {"assigned": 0, "method": "ai", "error": "Keine Budgetposten vorhanden"}

    bp_map = {b.kategorie: b.name for b in bp_list}
    kategorien = list(bp_map.keys())

    # Load unassigned Bankbuchungen
    filters = {"budgetposten": ["is", "not set"]}
    if bankkonto:
        filters["bankkonto"] = bankkonto

    buchungen = frappe.get_all(
        "Bankbuchung",
        filters=filters,
        fields=["name", "buchungstext"],
        limit=500,
    )

    if not buchungen:
        return {"assigned": 0, "method": "ai"}

    # Process in batches of 20
    batch_size = 20
    assigned = 0

    for i in range(0, len(buchungen), batch_size):
        batch = buchungen[i : i + batch_size]
        texts = [b.buchungstext for b in batch]
        categories = _classify_batch(texts, kategorien, settings)

        for b, kat in zip(batch, categories):
            bp_name = bp_map.get(kat)
            if bp_name:
                frappe.db.set_value("Bankbuchung", b.name, "budgetposten", bp_name)
                assigned += 1

    frappe.db.commit()
    return {"assigned": assigned, "total": len(buchungen), "method": "ai"}

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
def get_ki_models(api_url=None, api_key=None):
    """Fetch available models from OpenAI-compatible API."""
    import urllib.request as urlreq
    if not api_url:
        d = frappe.db.get_singles_dict("Ktesis Einstellungen")
        api_url = d.get("ki_api_url") or "https://opencode.ai/zen/go/v1"
        api_key = d.get("ki_api_key") or ""
    base = api_url.rstrip("/")
    req = urlreq.Request(
        f"{base}/models",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="GET",
    )
    try:
        with urlreq.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        models = [m.get("id") or m.get("name") for m in data.get("data", data.get("models", []))]
        return sorted(m for m in models if m)
    except Exception as e:
        frappe.throw(str(e))
