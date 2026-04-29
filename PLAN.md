# KTESIS Masterplan: Vom Dashboard zum privaten Finanz-Copilot

## Phase 1: Design-Fundament (Abgeschlossen ✅)
**Ziel:** Gameplan-Level Professionalität
- [x] Tailwind-Config auf `frappeUIPreset` umstellen
- [x] Alle `kt-*` Custom-CSS-Klassen entfernt (nur Chrome in AppSidebar/AppTopbar bleibt)
- [x] Semantic Colors (`bg-surface-*`, `text-ink-*>`, `border-outline-*`) durchgängig
- [x] Sidebar, Cards, Buttons, Badges auf frappe-ui-Komponenten/Tailwind umgestellt
- [x] Dashboard-JS-Fehler behoben (API-Feldnamen `bezeichnung`, `kontostand_manuell`, `vertragskosten`)
- [x] Tests: 4x Python API-Tests + 4x Frontend-Tests alle grün
- [x] Deployed: migrate + restart erfolgreich

## Phase 2: Dashboard-Upgrade
**Ziel:** Vom leeren Dashboard zur echten Finanz-Übersicht
- [ ] Nettovermögens-Charts (ECharts/Chart.js)
- [ ] Budget-Planung (Doctype `Budget` + Ampel)
- [ ] Monats-Report (PDF-Export)
- [ ] "Was-wäre-wenn"-Simulator
- [ ] Bankbuchungen-View (eigene Seite)

## Phase 3: Verträge 2.0
**Ziel:** Smarte Vertragsverwaltung
- [ ] Kündigungs-Assistent (Fristenberechnung)
- [ ] Kündigungsvorlagen (Jinja → PDF)
- [ ] Dokumenten-Safe (File-Upload)
- [ ] Vertrags-Scan-Upload

## Phase 4: Erweiterte Module
- [ ] Investitionen-Tracking
- [ ] Altersvorsorge-Planer
- [ ] Ziel-Tracker
- [ ] Steuer-Checkliste

## Phase 5: KI & Automatisierung
- [ ] Ollama-Setup (on-premise)
- [ ] KI-Dokumenten-Parser
- [ ] Telegram-Bot
- [ ] E-Mail-Eingang (IMAP)

---
*Erstellt: 2026-04-28*
*Status: Phase 1 in Bearbeitung*
