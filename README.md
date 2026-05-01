# ktesis — Persoenliche Vermoegensverwaltung

Frappe-App zur strukturierten Verwaltung von Finanzen, Vermoegenswerten und Vertraegen. Vue 3 SPA auf Frappe-Basis.

## Features

### Vermoegensverwaltung
- **Fahrzeuge** — Kennzeichen, FIN, Kilometerstand, Anschaffungswert, Fahrzeugbild
- **Wohnungen** — Kaufpreis, Wohnflaeche, Baujahr, laufende Kosten, Status (bewohnt/vermietet/leerstehend)
- **Darlehen** — Zinssatz, Laufzeit, monatliche Rate, Tilgungsplan-Berechnung
- **Abschreibungen** — Abschreibungssatz, -betrag, Zuordnung zu Assets

### Banking & Buchungen
- **Bankkonten** — IBAN-Validierung, mehrere Konten, Kontostaende
- **Bankbuchungen** — manuelle Erfassung + CSV-Import (DKB, Sparkasse, ING)
- **CSV-Auto-Import** — erkennt Bankformat automatisch, verhindert Duplikate, Vorschau (5 Zeilen)
- **Buchungskategorien** — Wohnen, Mobilitaet, Versicherung, Lebensmittel, Freizeit, Einkommen, Sonstiges

### Budget-Planung
- **Budgetposten** — monatliche Sollbetrage je Kategorie
- **Soll-Ist-Vergleich** — Monat auswaehlen, Fortschrittsbalken je Kategorie

### Vertraege
- **Vertragsverwaltung** — Laufzeit, monatliche Kosten, Kuendigungsfrist
- **Kuendigungsfristen-Ampel** — rot (<=14 Tage), gelb (<=60 Tage), gruen
- **Dokument-Anhang** — PDF/Scan direkt am Vertrag ablegen
- **E-Mail-Reminder** — woechentlicher Scheduler fuer nahende Kuendigungsfristen

### Dashboard
- **Einnahmen/Ausgaben-Chart** — Balkendiagramm der letzten 12 Monate (Chart.js)
- **Vermoegensuebersicht** — Kacheln mit Gesamtvermoegen, offene Darlehen, Monatssaldo
- **Tilgungsrechner** — Was-waere-wenn Sondertilgung mit Schieberegler

## DocTypes

| DocType | Beschreibung |
|---------|-------------|
| `Fahrzeug` | KFZ-Verwaltung |
| `Wohnung` | Immobilien |
| `Bankkonto` | Girokonten / Sparkonten |
| `Bankbuchung` | Ein-/Ausgaben mit Kategorie |
| `Darlehen` | Kredite und Hypotheken |
| `Vertrag` | Abonnements und Vertraege |
| `Abschreibung` | Wertverlust-Tracking |
| `Budgetposten` | Monatliche Soll-Budgets |

## Tech Stack

- **Backend:** Python 3 / Frappe Framework
- **Frontend:** Vue 3 + Vite (SPA via Frappe www-Route)
- **Charts:** Chart.js
- **UI:** frappe-ui Komponenten + eigene
- **Datenbank:** MariaDB (via Frappe ORM)
- **HTTPS:** nginx mit self-signed Cert (Port 443), Port 80/2024 -> Redirect

## Installation

### Voraussetzungen
- Frappe Bench (v15+)
- Node.js 18+
- Python 3.10+

### App installieren
```bash
cd /home/erpnext/frappe-bench
bench get-app ktesis https://github.com/ManuelDell/ktesis.git
bench --site development install-app ktesis
bench migrate
```

Der `install-app`-Befehl baut das Frontend automatisch (`npm install && npm run build`).
Voraussetzung: Node.js und npm sind auf dem System installiert.

### Frontend live (mit HMR)
```bash
cd apps/ktesis/frontend
npm run dev
```

### HTTPS einrichten (optional)
```bash
sudo bench setup-ktesis-https --site development
```
Generiert self-signed Zertifikat und nginx-Konfiguration fuer Port 443. Alle HTTP-Routen werden auf HTTPS umgeleitet.

**Bekannte Einschraenkungen:**
- Self-signed: Browser zeigt Zertifikatswarnung — kein Let's Encrypt, keine CA
- IP-gebunden: Zertifikat gilt fuer eine feste IP; bei IP-Wechsel neu generieren
- Development only: Fuer oeffentliche Server Let's Encrypt + Domain verwenden

### App oeffnen
Das Ktesis-Icon erscheint auf dem Frappe Desk. Direkt erreichbar unter: `https://<deine-site>/ktesis`

## API

Alle Endpunkte via `frappe.whitelist()` erreichbar:

### Dashboard & Auswertungen
| Endpoint | Beschreibung |
|----------|-------------|
| `ktesis.api.dashboard.get_finance_summary` | Vermoegensuebersicht-Kacheln |
| `ktesis.api.dashboard.get_buchungen_verlauf` | Monatliche Ein-/Ausgaben (Chart) |
| `ktesis.api.dashboard.get_budget_vs_ist` | Soll-Ist-Vergleich |
| `ktesis.api.dashboard.get_vertraege_mit_fristen` | Vertraege mit Ampel-Status |
| `ktesis.api.dashboard.get_monatsuebersicht` | Monatliche Uebersicht |
| `ktesis.api.dashboard.get_vermoegensentwicklung` | Nettovermoegen-Berechnung |
| `ktesis.api.dashboard.get_dashboard_stats` | KPI-Zahlen (Counts, Salden) |

### CSV-Import
| Endpoint | Beschreibung |
|----------|-------------|
| `ktesis.api.csv_import.preview_csv` | CSV-Vorschau (5 Zeilen) |
| `ktesis.api.csv_import.import_bankbuchungen` | CSV-Import mit Duplikat-Check |

### CRUD-Endpunkte
| DocType | Endpunkte |
|---------|-----------|
| Fahrzeug | `get_vehicles` * `create_vehicle` * `update_vehicle` * `delete_vehicle` |
| Wohnung | `get_properties` * `create_property` * `update_property` * `delete_property` |
| Vertrag | `get_contracts` * `create_contract` * `update_contract` * `delete_contract` |
| Darlehen | `get_loans` * `create_loan` * `update_loan` * `delete_loan` * `calculate_amortization_schedule` |
| Bankkonto | `get_bank_accounts` * `create_bank_account` * `update_bank_account` * `delete_bank_account` * `get_buchungen` |

### Anhaenge
| Endpoint | Beschreibung |
|----------|-------------|
| `ktesis.api.attachments.get_attachments` | Datei-Anhaenge zu einem Dokument |
| `ktesis.api.attachments.delete_attachment` | Anhang loeschen |

### FinTS (experimentell)
| Endpoint | Beschreibung |
|----------|-------------|
| `ktesis.api.fints.get_bank_list` | Unterstuetzte Banken |
| `ktesis.api.fints.start_fints_sync` | FinTS-Synchronisation starten |
| `ktesis.api.fints.get_fints_sync_status` | Sync-Status abfragen |
| `ktesis.api.fints.submit_tan` | TAN einreichen |

## Frontend-Views

| View | Pfad | Beschreibung |
|------|------|-------------|
| Dashboard | `/` | KPI-Kacheln, Charts, Tilgungsrechner |
| Fahrzeuge | `/fahrzeuge` | Liste & Detail Fahrzeuge |
| Wohnungen | `/wohnungen` | Liste & Detail Immobilien |
| Bankkonten | `/bankkonten` | Konten, Buchungen, CSV-Import |
| Vertraege | `/vertraege` | Vertragsliste mit Ampel & Kuendigungsfristen |
| Darlehen | `/darlehen` | Darlehensliste & Tilgungsplan |
| Budget | `/budget` | Budgetposten & Soll-Ist-Vergleich |

## Lizenz

MIT — siehe [license.txt](./license.txt)
