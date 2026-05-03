<div align="center">

# 💎 Ktesis

### Persönliche Vermögensverwaltung — klar, sicher, selbstgehostet.

[![License: MIT](https://img.shields.io/badge/License-MIT-silver.svg)](LICENSE)
[![Frappe](https://img.shields.io/badge/Frappe-v15-blue.svg)](https://frappe.io)
[![Vue](https://img.shields.io/badge/Vue-3-42b883.svg)](https://vuejs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)

</div>

---

Ktesis ist eine selbstgehostete Frappe-App, die alle wichtigen Aspekte persönlicher Finanzen an einem Ort vereint — Bankbuchungen, Budgets, Immobilien, Fahrzeuge, Darlehen und Verträge. Keine Cloud, keine Abos, keine Datenweitergabe.

> Der Name *Ktesis* (κτῆσις) kommt aus dem Altgriechischen und bedeutet **Besitz** oder **Vermögen**.

---

## ✨ Was Ktesis kann

| Bereich | Was du bekommst |
|---|---|
| 🏦 **Bankkonten & Buchungen** | CSV-Import für 8 Banken, automatische Duplikaterkennung, Budgettopf-Zuordnung, Mehrfachauswahl & Bulk-Aktionen |
| 🤖 **KI-Kategorisierung** | Automatische Buchungszuordnung via OpenAI-kompatibler API — mit Fallback auf Keyword-Matching |
| 📊 **Budget-Planung** | Monats- und Jahresübersicht, Soll-Ist-Vergleich, Saldo-Anzeige mit Einnahmen/Ausgaben-Unterscheidung |
| 🏠 **Immobilien** | Eigentum, Gemietet oder Vermietet — mit Miet-Budget-Verknüpfung, Nebenkosten und Soll-Ist-Auswertung |
| 🚗 **Fahrzeuge** | Fahrzeugdaten, Dokument-Upload (Fahrzeugschein & Fahrzeugbrief), Kilometerstand |
| 💰 **Darlehen** | Tilgungsplan, Sondertilgungssatz, interaktiver Was-wäre-wenn-Rechner |
| 📄 **Verträge** | Kündigungsfristen-Ampel, automatische E-Mail-Erinnerungen, Dokument-Upload |
| 📈 **Dashboard** | Einnahmen/Ausgaben-Balkendiagramm (12 Monate) mit Trendlinien, Tilgungsrechner |

---

## 🚀 Schnellstart

### Voraussetzungen

- [Frappe Bench](https://frappeframework.com/docs/user/en/installation) v15
- Node.js 18+, Python 3.10+, MariaDB 10.6+

### Installation

```bash
# App installieren
bench get-app ktesis git@github.com:ManuelDell/ktesis.git
bench --site <deine-site> install-app ktesis
bench --site <deine-site> migrate

# Frontend bauen
cd apps/ktesis/frontend
npm install
npm run build
```

### KI einrichten *(optional)*

Unter **Einstellungen → KI-Konfiguration** einen OpenAI-kompatiblen API-Endpunkt eintragen, z. B.:
- [OpenCode Go](https://opencode.ai) — `https://opencode.ai/zen/go/v1`
- OpenAI — `https://api.openai.com/v1`
- Jeder OpenAI-kompatibler lokaler Dienst (Ollama etc.)

Ohne API-Key greift automatisch das Keyword-Fallback-System.

---

## 🏗️ Technische Übersicht

### Stack

```
Backend   Frappe v15 (Python)  ·  MariaDB
Frontend  Vue 3 (Composition API)  ·  Vite  ·  Tailwind CSS  ·  frappe-ui
```

### DocTypes

| DocType | Beschreibung |
|---|---|
| `Bankkonto` | Bankverbindungen mit IBAN, Kontostand |
| `Bankbuchung` | Einzelne Buchungen mit Betrag, Datum, Budgettopf-Link |
| `Budgetposten` | Budget-Kategorien mit Soll-Betrag und KI-Beschreibung |
| `Wohnung` | Immobilien — Eigentum / Gemietet / Vermietet |
| `Fahrzeug` | Fahrzeuge mit Dokument-Upload |
| `Darlehen` | Darlehen mit Tilgungsplan und Sondertilgungssatz |
| `Vertrag` | Verträge mit Kündigungsfristen-Logik |
| `Ktesis Einstellungen` | Single DocType für KI-API-Konfiguration |

### API-Endpunkte (Auswahl)

```
ktesis.api.ai_assign.ai_assign_budgetposten   KI- oder Keyword-Kategorisierung
ktesis.api.ai_assign.get/save_einstellungen   KI-Konfiguration lesen/schreiben
ktesis.api.dashboard.get_budget_vs_ist        Soll-Ist-Vergleich (Monat)
ktesis.api.bankkonto.get_buchungen            Paginierte Buchungsliste
ktesis.api.budget.wohnung_budget_vergleich    Immobilien Soll-Ist
ktesis.api.csv_import.preview_csv             CSV-Vorschau mit Duplikat-Check
```

### Unterstützte CSV-Formate

DKB · Sparkasse · ING · Comdirect · Commerzbank · Deutsche Bank · N26 · Trade Republic

### Sicherheit

- Alle Endpunkte erfordern eine aktive Frappe-Session — kein Gast-Zugriff möglich
- CSRF-Schutz aktiv (Frappe-Standard)
- Alle SQL-Queries parametrisiert (kein Injection-Risiko)
- Empfohlen: NGINX Reverse Proxy mit HTTPS und Rate-Limiting auf `/api/`

---

## 🤖 KI-Mitwirkende

Dieses Projekt wurde mit Unterstützung mehrerer KI-Modelle entwickelt. Transparenz ist uns wichtig:

| Modell | Anbieter | Rolle |
|---|---|---|
| **Claude Sonnet 4.6** | Anthropic | Orchestrierung, Architekturentscheidungen, Code-Review, Security Audit |
| **Kimi K2.6** | Moonshot AI | Hauptimplementierung, komplexe Backend-Logik, CSV-Parser |
| **DeepSeek V4 Pro** | DeepSeek | Analyse, Konzeption, Optimierungen |
| **GLM-5.1** | Zhipu AI | Deployment-Automatisierung, Frontend-Patches |

Der menschliche Entwickler hat alle Anforderungen definiert, Entscheidungen getroffen und jede Änderung freigegeben.

---

## 🗺️ Roadmap

- [ ] FinTS-Integration *(Produktionsschlüssel ausstehend)*
- [ ] PDF-Export für Tilgungspläne und Budgetberichte
- [ ] Mobile-optimierte Ansicht

---

## 📄 Lizenz

MIT © [Manuel Dell](https://github.com/ManuelDell)