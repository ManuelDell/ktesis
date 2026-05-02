# Ktesis — Persönliche Vermögensverwaltung

Ktesis ist eine [Frappe](https://frappe.io/) v15 App zur persönlichen Vermögensverwaltung. Sie läuft als Single-Tenant-Instanz und bietet:

- **Bankkonten & Buchungen** — CSV-Import (DKB, Sparkasse, ING, Comdirect, Commerzbank, Deutsche Bank, N26, Trade Republic), manuelle Zuordnung zu Budgettöpfen
- **KI-Kategorisierung** — automatische Buchungszuordnung via OpenCode-kompatible LLM-APIs (OpenAI-Format)
- **Budget-Planung** — Monats- und Jahresübersicht, Soll-Ist-Vergleich, Saldo-Anzeige
- **Immobilien** — Wohnungen mit Typen (Eigentum/Gemietet/Vermietet), Soll-Ist-Budget-Verknüpfung, Abschreibungen
- **Fahrzeuge** — Fahrzeugverwaltung mit Dokument-Upload (Fahrzeugschein/Fahrzeugbrief)
- **Darlehen** — Tilgungsplan, Sondertilgungssatz, Was-wäre-wenn-Rechner
- **Verträge** — Kündigungsfristen-Ampel, E-Mail-Reminder
- **Dashboard** — Einnahmen/Ausgaben-Chart (12 Monate) mit Trendlinien, Tilgungsrechner

## Voraussetzungen

- Frappe v15 Bench
- Python 3.10+
- Node.js 18+
- MariaDB 10.6+

## Installation

```bash
cd frappe-bench
bench get-app ktesis git@github.com:ManuelDell/ktesis.git
bench --site <deine-site> install-app ktesis
bench --site <deine-site> migrate
cd apps/ktesis/frontend && npm install && npm run build
```

## Frontend bauen

```bash
cd apps/ktesis/frontend
./node_modules/.bin/vite build
```

## KI-Einstellungen

Unter **Einstellungen** kann ein OpenAI-kompatibler LLM-API-Endpunkt konfiguriert werden (z.B. OpenCode Go `https://opencode.ai/zen/go/v1`). Ohne API-Key erfolgt ein Keyword-Fallback.

## CSV-Import

Unterstützte Formate: DKB, Sparkasse, ING, Comdirect, Commerzbank, Deutsche Bank, N26, Trade Republic.

## Sicherheit

- Alle Endpunkte erfordern einen eingeloggten Frappe-User (`@frappe.whitelist()`)
- Guest-Zugriff ist nicht möglich
- Empfohlen: hinter NGINX mit HTTPS betreiben (siehe `nginx.conf`-Beispiel in Frappe-Docs)

## FinTS

FinTS-Integration ist vorbereitet aber deaktiviert (kein Produktions-Schlüssel). Wird in einer späteren Version aktiviert.

## Lizenz

MIT