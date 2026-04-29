# Phase 4 — Auth-Flow, Desk-Link, FormControl & Datei-Upload

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Auth-Flow korrigieren (Desk als Einstieg), ktesis im Frappe Desk verlinken, FormControl in allen Detail-Views konsolidieren, echten Datei-Upload via frappe-ui integrieren.

**Architecture:**
- **Auth:** Login → Frappe Desk (kein Auto-Redirect). Guest → `/ktesis` → `/login`.
- **Desk:** `add_to_apps_screen` in `hooks.py` aktivieren → Icon im Desk → Klick → `/ktesis`.
- **Detail-Views:** Manuelles `<label> + <Input>` durch `FormControl` (frappe-ui, global registriert) ersetzen.
- **Datei-Upload:** Eigener `FileUploader.vue` löschen. Stattdessen `FileUploader` aus `frappe-ui` + `AttachmentList` in Detail-Views einbauen.
- **KachelCard:** Wird gesondert geplant (siehe `plan-kachelcard.md`).

**Tech Stack:** Vue 3, frappe-ui (^0.1.278), Tailwind CSS, Frappe API

---

## Task 1: Auth-Flow korrigieren — Kein Auto-Redirect nach Login

**Objective:** Nach Login landet der User auf dem Frappe Desk, nicht automatisch im ktesis Dashboard.

**Current:** `ktesis/auth.py` redirected eingeloggte User automatisch zu `/ktesis` via `get_home_page` Hook.

**Files:**
- Modify: `ktesis/auth.py`
- Modify: `ktesis/hooks.py`

**Steps:**
1. `auth.py`: `get_home_page` entweder löschen oder `return None` für alle User
2. `hooks.py`: Zeile `get_website_user_home_page = "ktesis.auth.get_home_page"` löschen oder auskommentieren
3. Test: Login → sollte jetzt auf Desk landen (Standard-Frappe-Verhalten)

**Verification:**
- Neuen Browser-Tab öffnen → Login → Erwartet: Frappe Desk, nicht ktesis

---

## Task 2: Desk-App-Verlinkung aktivieren

**Objective:** ktesis erscheint als App-Icon im Frappe Desk. Klick → `/ktesis`.

**Current:** `add_to_apps_screen` in `hooks.py` ist auskommentiert.

**Files:**
- Modify: `ktesis/hooks.py`
- Create/Verify: `ktesis/public/logo.png`

**Steps:**
1. `hooks.py`: `add_to_apps_screen` einkommentieren:
   ```python
   add_to_apps_screen = [
       {
           "name": "ktesis",
           "logo": "/assets/ktesis/logo.png",
           "title": "Ktesis",
           "route": "/ktesis",
       }
   ]
   ```
2. Logo-Datei erstellen: `ktesis/public/logo.png` (128x128 PNG). Falls kein Logo vorhanden, ein einfaches generieren.
3. `bench --site development migrate`
4. `supervisorctl restart all`
5. Test: Desk öffnen → ktesis-Icon sichtbar → Klick → ktesis Dashboard

**Verification:**
- Desk zeigt ktesis-Icon
- Klick öffnet `/ktesis`
- Guest → `/ktesis` redirected weiterhin zu `/login`

---

## Task 3: Guest-Redirect sicherstellen

**Objective:** Ohne Login zeigt ktesis Überhaupt nichts — direkt zum Frappe-Login.

**Current:** `www/ktesis.py` macht das bereits korrekt.

**Files:**
- Verify: `ktesis/www/ktesis.py`

**Steps:**
1. Prüfen dass `www/ktesis.py` Guest zu `/login?redirect-to=/ktesis` redirected — ist bereits so
2. API-Calls: `@frappe.whitelist()` erfordert standardmäßig Login — bereits geschützt
3. Test: `/ktesis` als Guest aufrufen → sollte auf Login umleiten

---

## Task 4: FormControl in FahrzeugDetail.vue migrieren

**Objective:** Erste Detail-View auf `FormControl` umstellen.

**Rationale:** `FormControl` ist in `main.js` global registriert. Vereint Label, Input und konsistentes Styling. Reduziert Boilerplate um ~50% pro Feld.

**Files:**
- Modify: `frontend/src/components/FahrzeugDetail.vue`

**Current (bad):**
```vue
<div>
  <label class="block text-xs font-medium text-ink-gray-5 mb-1">Kennzeichen *</label>
  <Input v-model="form.kennzeichen" type="text" required class="" />
</div>
```

**Target (good):**
```vue
<FormControl v-model="form.kennzeichen" type="text" label="Kennzeichen" required />
```

**Select:**
```vue
<FormControl v-model="form.kraftstoff" type="select" label="Kraftstoff"
  :options="['Benzin','Diesel','Elektro','Hybrid','Plug-in-Hybrid']" />
```

**Steps:**
1. Alle Felder auf `FormControl` umstellen
2. `Textarea` für Notizen: `FormControl type="textarea"`
3. Build: `npm run build`
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

## Task 10: AttachmentList.vue erstellen

**Objective:** Wiederverwendbare Komponente zur Anzeige von an DocType angehängten Dateien.

**Architecture:**
- Lädt Dateien über eigenen API-Endpoint `get_attachments(doctype, docname)`
- Zeigt Dateiname, Größe, Download-Link, Löschen-Button
- Download via Frappe's `/api/method/ktesis.api.attachments.download_file?name=...`

**Files:**
- Create: `frontend/src/components/AttachmentList.vue`
- Create: `ktesis/api/attachments.py`

**Steps:**
1. `attachments.py` erstellen mit:
   - `get_attachments(doctype, docname)` → Liste von File-Datensätzen
   - `delete_attachment(name)` → Löscht File-Datensatz
   - Beide mit `@frappe.whitelist()`
2. `AttachmentList.vue` erstellen:
   - Props: `doctype`, `docname`
   - Lädt Dateien bei Mount + wenn `docname` sich ändert
   - Zeigt Liste mit FeatherIcon (file-text, image, etc.)
   - Download-Link + Löschen-Button pro Datei
3. Build testen

---

## Task 11: Echten Datei-Upload in Detail-Views integrieren

**Objective:** In jeder Detail-View einen Upload-Bereich einbauen (nur beim Bearbeiten, nicht beim Anlegen).

**Architecture:**
- `FileUploader` aus `frappe-ui` (bereits installiert)
- Props: `fileTypes`, `uploadArgs` (mit `doctype`, `docname`, `is_private: 1`)
- `@success` → `AttachmentList` neu laden

**Files:**
- Modify: `frontend/src/components/FahrzeugDetail.vue`
- Modify: `frontend/src/components/WohnungDetail.vue`
- Modify: `frontend/src/components/VertragDetail.vue`
- Modify: `frontend/src/components/DarlehenDetail.vue`
- Modify: `frontend/src/components/BankkontoDetail.vue`

**Steps (pro Detail-View):**
1. `FileUploader` importieren (aus `frappe-ui`)
2. `AttachmentList` importieren
3. Nur anzeigen wenn `!isNew` (also nur beim Bearbeiten)
4. Upload-Bereich unterhalb des Formulars, oberhalb der Actions:
   ```vue
   <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5 mt-5">
     <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
     <FileUploader
       :uploadArgs="{ doctype: 'Fahrzeug', docname: props.name, is_private: 1 }"
       @success="loadAttachments"
     />
     <AttachmentList :doctype="'Fahrzeug'" :docname="props.name" ref="attachmentList" />
   </div>
   ```
5. `loadAttachments` Methode ruft `attachmentList.reload()` auf
6. Build testen

**Verification:**
- Fahrzeug-Detail öffnen → PDF hochladen
- Datei erscheint in AttachmentList
- Download funktioniert
- Löschen funktioniert

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
| 3 | `ktesis/public/logo.png` | Erstellen | ~10 min |
| 4 | `ktesis/www/ktesis.py` | Verify (bleibt) | ~2 min |
| 5 | `components/FahrzeugDetail.vue` | FormControl + Upload | ~20 min |
| 6 | `components/WohnungDetail.vue` | FormControl + Upload | ~20 min |
| 7 | `components/VertragDetail.vue` | FormControl + Upload | ~25 min |
| 8 | `components/DarlehenDetail.vue` | FormControl + Upload | ~20 min |
| 9 | `components/BankkontoDetail.vue` | FormControl + Upload | ~20 min |
| 10 | `components/FileUploader.vue` | Löschen | ~2 min |
| 11 | `components/AttachmentList.vue` | Neu erstellen | ~20 min |
| 12 | `api/attachments.py` | Neue API-Endpunkte | ~15 min |

**Gesamtaufwand geschätzt:** ~3,5 Stunden verteilt auf 12 Tasks
