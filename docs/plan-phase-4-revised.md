# Phase 4 — Konsolidierung, Desk-Link & Datei-Upload

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** FormControl-Konsolidierung in allen Detail-Views, echter Datei-Upload via frappe-ui, KachelCard vereinfachen, Desk-App-Verlinkung aktivieren, Auth-Flow korrigieren.

**Architecture:**
- Detail-Views migrieren von manuellem `<label> + <Input>` zu `FormControl` (frappe-ui, bereits global registriert)
- FileUploader: Eigenen Code löschen, stattdessen `FileUploader` aus `frappe-ui` in Detail-Views integrieren (PDF, JPG etc. an DocType anhängen)
- KachelCard: `color`-Prop entfernen — monochrome Karten passen besser zum gewünschten Design
- Desk: App-Icon im Frappe Desk aktivieren → Login → Desk → Klick auf Icon → ktesis Dashboard
- Auth: Keine automatische Weiterleitung nach Login

**Tech Stack:** Vue 3, frappe-ui (^0.1.278), Tailwind CSS, Frappe API

---

## Task 1: Auth-Flow korrigieren — Kein Auto-Redirect nach Login

**Objective:** Nach Login landet der User auf dem Frappe Desk, nicht automatisch im ktesis Dashboard.

**Current problem:** `ktesis/auth.py` redirected eingeloggte User automatisch zu `/ktesis`.

**Files:**
- Modify: `ktesis/auth.py`
- Modify: `ktesis/hooks.py`

**Steps:**
1. `auth.py`: `get_home_page` entweder entfernen oder `return None` für alle User
2. `hooks.py`: Zeile `get_website_user_home_page = "ktesis.auth.get_home_page"` entfernen oder auskommentieren
3. Test: Login → sollte jetzt auf Desk landen (Standard-Frappe-Verhalten)

**Verification:**
- Neuen Browser-Tab öffnen
- Login
- Erwartet: Frappe Desk wird angezeigt, nicht ktesis

---

## Task 2: Desk-App-Verlinkung aktivieren

**Objective:** ktesis erscheint als App-Icon im Frappe Desk. Klick → `/ktesis`.

**Current:** `add_to_apps_screen` in `hooks.py` ist auskommentiert.

**Files:**
- Modify: `ktesis/hooks.py`
- Create: `ktesis/public/logo.png` (oder vorhandenes Logo nutzen)

**Steps:**
1. `hooks.py`: `add_to_apps_screen` einkommentieren:
   ```python
   add_to_apps_screen = [
       {
           "name": "ktesis",
           "logo": "/assets/ktesis/logo.png",
           "title": "Ktesis",
           "route": "/ktesis",
           # "has_permission": "ktesis.api.permission.has_app_permission"
       }
   ]
   ```
2. Logo-Datei prüfen/erstellen: `ktesis/public/logo.png` (min. 1 Datei für das Icon). Falls kein Logo existiert, ein einfaches 128x128 PNG erstellen oder Default verwenden.
3. `bench --site development migrate`
4. `supervisorctl restart all`
5. Test: Desk öffnen → ktesis-Icon sollte sichtbar sein → Klick → ktesis Dashboard

**Verification:**
- Desk zeigt ktesis-Icon
- Klick öffnet `/ktesis`
- Guest → `/ktesis` redirected immer noch zu `/login`

---

## Task 3: Guest-Redirect sicherstellen

**Objective:** Ohne Login zeigt ktesis Überhaupt nichts — direkt zum Frappe-Login.

**Current:** `www/ktesis.py` macht das bereits korrekt. Aber wir prüfen ob API-Calls ebenfalls geschützt sind.

**Files:**
- Verify: `ktesis/www/ktesis.py`

**Steps:**
1. Prüfen dass `www/ktesis.py` Guest zu `/login` redirected — ist bereits so
2. API-Calls: `@frappe.whitelist()` erfordert standardmäßig Login in Frappe — sollte bereits geschützt sein
3. Test: `/ktesis` als Guest aufrufen → sollte auf `/login?redirect-to=/ktesis` umleiten

---

## Task 4: FormControl in FahrzeugDetail.vue migrieren

**Objective:** Erste Detail-View auf `FormControl` umstellen.

**Rationale:** `FormControl` ist in `main.js` global registriert. Es vereint Label, Input, Fehleranzeige und konsistentes Styling. Reduziert Boilerplate.

**Files:**
- Modify: `frontend/src/components/FahrzeugDetail.vue`

**Current pattern (bad):**
```vue
<div>
  <label class="block text-xs font-medium text-ink-gray-5 mb-1">Kennzeichen *</label>
  <Input v-model="form.kennzeichen" type="text" required class="" />
</div>
```

**Target pattern (good):**
```vue
<FormControl v-model="form.kennzeichen" type="text" label="Kennzeichen" required />
```

**For Select fields:**
```vue
<FormControl v-model="form.kraftstoff" type="select" label="Kraftstoff"
  :options="['Benzin','Diesel','Elektro','Hybrid','Plug-in-Hybrid']" />
```

**Steps:**
1. Alle Felder auf `FormControl` umstellen
2. `Textarea` für Notizen: `FormControl type="textarea"`
3. Build testen: `npm run build`
4. Visuell verifizieren

---

## Task 5: FormControl in WohnungDetail.vue migrieren

**Files:**
- Modify: `frontend/src/components/WohnungDetail.vue`

**Steps:** Analog Task 4.

---

## Task 6: FormControl in VertragDetail.vue migrieren

**Files:**
- Modify: `frontend/src/components/VertragDetail.vue`

**Steps:** Analog Task 4. Besonders viele Select-Felder.

---

## Task 7: FormControl in DarlehenDetail.vue migrieren

**Files:**
- Modify: `frontend/src/components/DarlehenDetail.vue`

**Steps:** Analog Task 4.

---

## Task 8: FormControl in BankkontoDetail.vue migrieren

**Files:**
- Modify: `frontend/src/components/BankkontoDetail.vue`

**Steps:** Analog Task 4.

---

## Task 9: Eigenen FileUploader löschen

**Objective:** Unser `FileUploader.vue` ist tot, veraltet und wird nicht genutzt.

**Files:**
- Delete: `frontend/src/components/FileUploader.vue`

**Steps:**
1. Datei löschen
2. Prüfen ob irgendwo importiert (sollte nicht sein)
3. Build testen

---

## Task 10: Echten Datei-Upload in Detail-Views integrieren

**Objective:** In jeder Detail-View einen Bereich zum Hochladen von Dateien (PDF, JPG) einbauen. Dateien werden an den aktuellen DocType-Eintrag gehängt.

**Architecture:**
- `frappe-ui` stellt `FileUploader` bereit (bereits installiert)
- Props: `fileTypes`, `uploadArgs` (mit `doctype`, `docname`, `is_private: 1`)
- Emits: `@success` → Datei-Liste neu laden
- Frappe speichert Dateien in `File` DocType mit `attached_to_doctype` + `attached_to_name`

**Files:**
- Modify: `frontend/src/components/FahrzeugDetail.vue`
- Modify: `frontend/src/components/WohnungDetail.vue`
- Modify: `frontend/src/components/VertragDetail.vue`
- Modify: `frontend/src/components/DarlehenDetail.vue`
- Modify: `frontend/src/components/BankkontoDetail.vue`
- Create: `frontend/src/components/AttachmentList.vue` (wiederverwendbar)

**Steps:**
1. `AttachmentList.vue` erstellen:
   - Zeigt hochgeladene Dateien als Liste
   - Lädt Dateien von Frappe `File` DocType (via `frappe.client.get_list` — ACHTUNG: nur in Desk verfügbar!)
   - Alternativ: eigener API-Endpoint `get_attachments(doctype, docname)` erstellen
   - Jede Datei: Name, Größe, Download-Link, Löschen-Button
2. In jeder Detail-View:
   - `FileUploader` aus `frappe-ui` importieren
   - Nur anzeigen wenn `!isNew` (also nur beim Bearbeiten, nicht beim Anlegen)
   - `uploadArgs = { doctype: 'Fahrzeug', docname: props.name, is_private: 1 }`
   - `@success` → `AttachmentList` neu laden
3. Backend: API-Endpunkt `get_attachments(doctype, docname)` und `delete_attachment(name)` erstellen

**Verification:**
- In einem Fahrzeug-Detail PDF hochladen
- Datei erscheint in AttachmentList
- Download funktioniert
- Löschen funktioniert

---

## Task 11: KachelCard vereinfachen — color-Prop entfernen

**Objective:** Keine Farbcodierung in KPI-Karten. Monochrome, professionell.

**Rationale:** Der Nutzer will kein "kindisches" Regenbogen-Dashboard. Die `color`-Prop (rust, olive, amber, sky) wird vom Dashboard übergeben aber im Component nicht genutzt. Statt sie zu aktivieren, entfernen wir sie komplett.

**Files:**
- Modify: `frontend/src/components/KachelCard.vue`
- Modify: `frontend/src/views/Dashboard.vue`

**Steps:**
1. `KachelCard.vue`: `color` Prop entfernen
2. `Dashboard.vue`: `color="..."` Attribute aus allen `<KachelCard>` entfernen
3. Icon behält `text-ink-gray-4` (bereits so)
4. Build testen

---

## Task 12: Finale Build- & Regressionstests

**Objective:** Alles zusammen testen.

**Checkliste:**
- [ ] `npm run build` erfolgreich
- [ ] `bench --site development migrate`
- [ ] `supervisorctl restart all`
- [ ] Login → Desk erscheint (nicht Auto-Redirect zu ktesis)
- [ ] ktesis-Icon im Desk sichtbar, Klick öffnet Dashboard
- [ ] Guest → `/ktesis` redirected zu Login
- [ ] Alle 5 Listen-Views laden
- [ ] Alle 5 Detail-Views öffnen/speichern/schließen
- [ ] FormControl-Inputs sehen konsistent aus
- [ ] Datei-Upload in Detail-Views funktioniert
- [ ] Keine Console-Fehler
- [ ] Mobile-Ansicht prüfen

---

## Zusammenfassung der Dateien

| # | Datei | Aktion | Aufwand |
|---|---|---|---|
| 1 | `ktesis/auth.py` | Auto-Redirect entfernen | ~5 min |
| 2 | `ktesis/hooks.py` | Desk-Link aktivieren | ~10 min |
| 3 | `ktesis/www/ktesis.py` | Verify (bleibt) | ~2 min |
| 4 | `components/FahrzeugDetail.vue` | FormControl + FileUploader | ~20 min |
| 5 | `components/WohnungDetail.vue` | FormControl + FileUploader | ~20 min |
| 6 | `components/VertragDetail.vue` | FormControl + FileUploader | ~25 min |
| 7 | `components/DarlehenDetail.vue` | FormControl + FileUploader | ~20 min |
| 8 | `components/BankkontoDetail.vue` | FormControl + FileUploader | ~20 min |
| 9 | `components/FileUploader.vue` | Löschen | ~2 min |
| 10 | `components/AttachmentList.vue` | Neu erstellen | ~20 min |
| 11 | `api/attachments.py` | Neue API-Endpunkte | ~15 min |
| 12 | `components/KachelCard.vue` | color-Prop entfernen | ~5 min |
| 13 | `views/Dashboard.vue` | color-Attribute entfernen | ~5 min |

**Gesamtaxif geschätzt:** ~4 Stunden verteilt auf 12 Tasks

---

## Offene Punkte (keine Blocker)

- **Logo für Desk-Icon:** Falls kein `logo.png` existiert, ein einfaches generieren oder Frappe-Default nutzen
- **Datei-Download/Löschen:** AttachmentList braucht API-Endpoints für Download-URL und Löschen
