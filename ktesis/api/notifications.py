"""Scheduled notifications for ktesis."""
from __future__ import annotations
import frappe
from frappe.utils import today, add_months


def send_kuendigungsfrist_reminder() -> None:
    """Woechentlicher Check: Vertraege mit Kuendigungsfrist in <= 60 Tagen."""
    from datetime import date
    from dateutil.relativedelta import relativedelta

    vertraege = frappe.get_all(
        "Vertrag",
        fields=["name", "vertragspartner", "vertragsende", "kuendigungsfrist"],
        filters={"vertragsende": ["is", "set"]},
    )

    heute = date.today()
    warnung = []
    for v in vertraege:
        frist_raw = v.get("kuendigungsfrist") or "1"
        try:
            frist = int(frist_raw)
        except (ValueError, TypeError):
            frist = 1
        from frappe.utils import getdate
        ende_dt = getdate(v["vertragsende"])
        deadline = ende_dt - relativedelta(months=frist)
        tage = (deadline - heute).days
        if 0 <= tage <= 60:
            warnung.append(f"- {v['vertragspartner']} ({v['name']}): Kuendigung bis {deadline} ({tage} Tage)")

    if not warnung:
        return

    admin_email = frappe.db.get_single_value("System Settings", "email_footer_address") or frappe.session.user
    frappe.sendmail(
        recipients=[admin_email],
        subject=f"⚠️ Ktesis: {len(warnung)} Vertrag/Vertraege mit naher Kuendigungsfrist",
        message="<br>".join(warnung),
    )
