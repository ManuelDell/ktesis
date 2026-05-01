# FinTS / HBCI Protokoll — Tiefenanalyse & Knowledge Base

**Projekt:** ktesis  
**Erstellt:** 2026-04-29  
**Status:** comdirect-Verbindung problematisch — Analyse abgeschlossen  
**Quellen:** python-fints Source-Code, GitHub Issues, direkte Server-Abfragen, FinTS-Spezifikation

---

## 1. Executive Summary / TL;DR

### Das Problem
comdirect (`fints.comdirect.de/fints`) und Commerzbank (`fints.commerzbank.de/fints`) sind **unterschiedliche Server** mit **unterschiedlichen Fehlermustern**.

| Server | Fehler auf leere Anfrage | Bedeutung |
|--------|--------------------------|-----------|
| **comdirect** | `9110::Falsche Segmentzusammenstellung:no data` | Die Bank empfängt Daten, aber die Segmentstruktur ist formal falsch oder unvollständig |
| **Commerzbank** | `9010::Nachricht ungueltig.:Validierung fehlgeschlagen.` | Die Bank lehnt die Nachricht generisch ab (auch bei korrekter Struktur aber fehlenden Pflichtfeldern) |

### Die wahrscheinlichste Ursache für "Nachricht ungültig" bei Commerzbank
Die `product_id` wird in `HKVVB3` (Verarbeitungsvorbereitung) als `product_name` eingebettet. Das Feld hat `max_length=25` (FinTS-Standard). Deine aktuelle ID `9FA6681DEC0CF3046BFC2F8A6` hat **exakt 25 Zeichen** — sie passt gerade so rein, ist aber möglicherweise im **falschen Format** für die Bank.

**Empfohlene Tests:**
1. `product_id` auf 8 Zeichen + `/Version` kürzen (z.B. `9FA6681D/1`)
2. BLZ für comdirect auf `20041166` ändern (nicht `20040000`)
3. comdirect-Login: **Kontonummer** statt Kundennummer verwenden

---

## 2. FinTS / HBCI Protokoll Grundlagen

### 2.1 Versionen & Historie

| Version | Name | Jahr | Status |
|---------|------|------|--------|
| HBCI 2.1 | Home Banking Computer Interface | 1998 | Veraltet |
| HBCI 2.2 | HBCI Erweitert | 2003 | Noch von einigen Banken unterstützt |
| **FinTS 3.0** | **Financial Transaction Services** | **2009** | **Aktueller Standard** |
| FinTS 4.0 | Erweitert (PSD2) | 2018 | Nur teilweise implementiert |

**Wichtig:** comdirect und Commerzbank unterstützen beide **FinTS 3.0** (HBCI-Version 300). python-fints sendet ausschließlich FinTS 3.0.

### 2.2 Nachrichtenaufbau (Segmentstruktur)

Eine FinTS-Nachricht ist eine Kette von **Segmenten**, getrennt durch `'` (Apostroph). Jedes Segment hat einen Kopf:

```
SegmentID:Segmentnummer:Segmentversion+DE1+DE2+DE3+...
```

**Wichtige Segmente:**

| Segment | Name | Beschreibung |
|---------|------|--------------|
| `HNHBK` | Nachrichtenkopf | Länge, HBCI-Version, Dialog-ID, Nachrichtennummer |
| `HNHBS` | Nachrichtenabschluss | Beendet die Nachricht |
| `HNVSK` | Verschlüsselungskopf | Sicherheitsprofil, Algorithmus, Schlüssel |
| `HNVSD` | Verschlüsselte Daten | Enthält die eigentlichen Segmente |
| `HNSHK` | Signaturkopf | Signaturprofil, Referenz, Hash-Algorithmus |
| `HNSHA` | Signaturabschluss | PIN/TAN |
| `HKIDN` | Identifikation | Bank, Kunden-ID, System-ID |
| `HKVVB` | Verarbeitungsvorbereitung | BPD/UPD-Version, Sprache, **Produktname**, Produktversion |
| `HKSYN` | Synchronisation | System-ID anfordern (NEU/WIEDER) |
| `HKTAN` | TAN-Einreichung | Zwei-Schritt-TAN-Verfahren |
| `HIRMG` | Antwort (Gesamt) | Rückmeldung zur gesamten Nachricht |
| `HIRMS` | Antwort (Segment) | Rückmeldung zu einem Segment |

### 2.3 Dialogablauf (Initialisierung)

```
Kunde                           Bank
  |                               |
  |--- HKIDN + HKVVB + HKSYN --->|  Dialog initialisieren
  |                               |
  |<--- HIRMG + HIBPA + HISYN ---|  Bankparameter, System-ID
  |                               |
  |--- HKIDN + HKVVB + Auftrag -->|  Geschäftsvorfall senden
  |                               |
  |<--- HIRMG + HIRMS + Antwort --|  Ergebnis
  |                               |
  |--- HKEND -------------------->|  Dialog beenden
  |                               |
```

### 2.4 HKSYN (Synchronisation)

- **HKSYN v3** ist Standard in FinTS 3.0
- python-fints sendet **immer HKSYN3** mit `SynchronizationMode.NEW_SYSTEM_ID`
- Die Version ist **nicht konfigurierbar** in python-fints
- HKSYNv2 existiert nur in HBCI 2.2 und ist obsolet

**Fazit:** HKSYNv3 ist NICHT das Problem.

### 2.5 HKVVB3 — Verarbeitungsvorbereitung (entscheidend!)

Dieses Segment enthält die **Produktbezeichnung** und wird in **jeder** Dialog-Initialisierung gesendet:

```
HKVVB:Segmentnummer:3+BPD-Version+UPD-Version+Sprache+Produktname+Produktversion
```

**Spezifikation aus python-fints Source (`segments/auth.py`):**
```python
class HKVVB3(FinTS3Segment):
    bpd_version = DataElementField(type='num', max_length=3)
    upd_version = DataElementField(type='num', max_length=3)
    language = CodeField(enum=Language2, max_length=3)
    product_name = DataElementField(type='an', max_length=25, _d="Produktbezeichnung")
    product_version = DataElementField(type='an', max_length=5, _d="Produktversion")
```

**Kritisch:**
- `product_name`: max. **25 Zeichen**, alphanumerisch (`type='an'`)
- `product_version`: max. **5 Zeichen**, alphanumerisch
- Die Bank validiert oft das **Format** (nicht nur die Länge)

### 2.6 HNVSK3 — Verschlüsselungskopf

Enthält KEIN product_name Feld. Die Verschlüsselung ist standardisiert (PIN/TAN, 2-Schritt-3DES).

---

## 3. comdirect Spezifika

### 3.1 Server-Daten

| Attribut | Wert |
|----------|------|
| **FinTS-URL** | `https://fints.comdirect.de/fints` |
| **BLZ** | `20041166` (nicht `20040000`!) |
| **Bankname** | comdirect bank AG |
| **Mutterkonzern** | Commerzbank AG (vollständige Tochter) |
| **Eigene FinTS-Infra** | Ja (`fints.comdirect.de` ≠ `fints.commerzbank.de`) |

### 3.2 Login-Formate

| Anmeldeart | Format | Hinweis |
|------------|--------|---------|
| **Kontonummer** | 8-stellig | Wird für FinTS empfohlen |
| Kundennummer | 10-stellig | Auch möglich |
| Online-Banking-ID | 8-stellig | Nicht für FinTS |
| PIN | 5-38 Zeichen | Standard-PIN |

**Wichtig:** comdirect verwendet für FinTS primär die **Kontonummer**, nicht die Kundennummer.

### 3.3 Unterstützte TAN-Verfahren

- **photoTAN** (Verfahren 900)
- **pushTAN** / appTAN
- smsTAN (veraltet, wird abgeschaltet)

### 3.4 comdirect vs. Commerzbank

| Aspekt | comdirect | Commerzbank |
|--------|-----------|-------------|
| FinTS-URL | `fints.comdirect.de/fints` | `fints.commerzbank.de/fints` |
| BLZ | `20041166` | `20040000` |
| Server-Fehler (leer) | `9110` Segmentzusammenstellung | `9010` Nachricht ungültig |
| photoTAN | Ja (900) | Ja (900) |
| TAN-Mechanismen | 900, 999 | 900, 999 |
| Kreditkarten-FinTS | Separater Dialog nötig | Nicht verfügbar |

### 3.5 Bekannte comdirect-Probleme in python-fints

**GitHub Issue #73:** Kreditkartenkonto wird nicht als SEPA-Konto erkannt
- `get_sepa_accounts()` liefert nur Girokonto und Tagesgeld
- Kreditkarte muss über `get_information()` + manuelle Kontonummer abgefragt werden

---

## 4. python-fints Implementierungsdetails

### 4.1 Bibliotheks-Status

| Attribut | Wert |
|----------|------|
| **Version** | 5.0 (aktuell im ktesis venv) |
| **Maintenance** | Minimal — letzte bedeutende Aktivität 2024 |
| **Autor** | Raphael Michel |
| **product_id Pflicht** | Ja (seit Version 4.0, September 2019) |

### 4.2 FinTS3PinTanClient Konstruktor

```python
FinTS3PinTanClient(
    bank_identifier,   # BLZ als String
    user_id,           # Login-Name
    pin,               # PIN
    server,            # FinTS-URL
    product_id=None,   # SEIT V4 PFLICHTIG
    product_version=None,  # Default: fints-Version (z.B. "5.0.0")
    mode=FinTSClientMode.INTERACTIVE
)
```

**Kritischer Codepfad:**
```python
# client.py Zeile 192
self.product_name = product_id   # -> wird als product_name in HKVVB3 verwendet

# dialog.py Zeile 65-70
HKVVB3(
    self.client.bpd_version,      # 0 bei erstem Aufruf
    self.client.upd_version,      # 0 bei erstem Aufruf
    Language2.DE,
    self.client.product_name,     # <-- DEIN product_id WERT
    self.client.product_version   # z.B. "5.0.0"
)
```

### 4.3 product_id Format-Validierung

**Keine Format-Validierung in python-fints!**
- Die Library prüft nur `max_length=25` (über `_check_value_length` in `types.py`)
- Es gibt KEINE Prüfung auf gültiges Format (z.B. `XXXXXXXX/V`)
- Es gibt KEINE Prüfung auf registrierte ID

**Aber:** Die Bank validiert das Format serverseitig!

### 4.4 HKSYN Implementierung

```python
# client.py Zeile 1320
HKSYN3(SynchronizationMode.NEW_SYSTEM_ID)
```

- **Nicht konfigurierbar**
- Immer Version 3
- Immer `NEW_SYSTEM_ID` bei erster Verbindung

### 4.5 Fehlerbehandlung

python-fints wirft bei Server-Fehlern:
- `FinTSUnsupportedOperation` — Bank unterstützt Operation nicht
- `NeedTANResponse` — TAN erforderlich
- `ValueError` — z.B. "Could not find system_id"
- Generische Exceptions bei Verbindungsfehlern

### 4.6 Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Das gibt die **kompletten rohen FinTS-Nachrichten** aus (Senden & Empfangen).

---

## 5. Fehlercodes & Diagnose

### 5.1 Häufige FinTS-Fehlercodes

| Code | Deutsch | Bedeutung | Häufige Ursache |
|------|---------|-----------|------------------|
| `9010` | Nachricht ungültig | Generische Validierungsablehnung | Falsches Format, ungültige product_id, falsche BLZ |
| `9050` | Die Nachricht enthält Fehler | Gesamt-Fehler | Mehrere Segment-Fehler |
| `9110` | Falsche Segmentzusammenstellung | Struktureller Fehler | Fehlende Pflichtsegmente, falsche Reihenfolge, unbekannte Segmente |
| `9800` | Dialog abgebrochen | Folgefehler | Wird immer mit 9010/9050/9110 kombiniert |
| `9120` | Verarbeitung nicht möglich | Technischer Fehler | Server-Überlastung, Wartung |
| `9210` | Auftrag nicht ausgeführt | Geschäftslogik | Konto nicht gefunden, keine Berechtigung |
| `9400` | Berechtigung nicht ausreichend | Sicherheit | Falsche PIN, keine Berechtigung für Operation |
| `9900` | Abschluss der Verarbeitung | Hinweis | Erfolgreich oder Teilweise erfolgreich |

### 5.2 Spezifische Fehlermuster

#### "9010 Nachricht ungültig" bei Commerzbank
- Tritt auch bei leerer/ungültiger Anfrage auf
- Wahrscheinlichste Ursachen:
  1. `product_id` im falschen Format (nicht nur Länge, sondern Inhalt)
  2. Falsche BLZ (Commerzbank hat mehrere: 20040000, 20041180)
  3. Falsches Login-Format

#### "9110 Falsche Segmentzusammenstellung" bei comdirect
- Tritt bei leerer Anfrage auf (erwartet, da keine Segmente vorhanden)
- Bei python-fints: Deutet auf fehlende/unvollständige Segmente hin
- **Speziell:** comdirect scheint **strenger** zu validieren als Commerzbank

#### "Could not find system_id" (python-fints)
- Bank antwortet ohne HISYN-Segment
- Ursachen: Falsche Credentials, Bank blockt Client, TAN-Dialog nötig

### 5.3 Direkte Server-Tests (ohne python-fints)

```bash
# comdirect
curl -s https://fints.comdirect.de/fints
# Antwort: HNHBK:1:3...+HIRMG:2:2+9050::Die Nachricht enthaelt Fehler.+9800::Dialog abgebrochen+9110::Falsche Segmentzusammenstellung:no data'HNHBS:3:1+9999'

# Commerzbank
curl -s https://fints.commerzbank.de/fints
# Antwort: HNHBK:1:3...+HIRMG:2:2+9010::Nachricht ungueltig.:Validierung fehlgeschlagen.+9800::Dialog abgebrochen'HNHBS:3:1+1'
```

**Interpretation:** Beide Server sind online und sprechen FinTS. Der Fehler liegt in der Nachricht, nicht im Netzwerk.

---

## 6. Deutsche Banken — Vergleich

### 6.1 Banken-Gruppen

| Gruppe | Beispiele | Besonderheiten |
|--------|-----------|----------------|
| **Sparkassen** | Haspa, Stadtsparkasse | Eigene URLs pro Institut (fints-xxxyy.s-fints-pt-xx.de), OFT HKTAN-Probleme |
| **Genossenschaftsbanken** | Volksbank, Raiffeisen | VR-Bank FinTS, oft konservativ |
| **Großbanken** | Commerzbank, Deutsche Bank | Zentrale URLs, PSD2-konform |
| **Direktbanken** | **comdirect**, ING, DKB | Eigene URLs, manchmal abweichende Implementierungen |
| **PSD2 APIs** | Alle ab 2019 | XS2A als Alternative zu FinTS |

### 6.2 Unterschiedliche Anforderungen

| Aspekt | Sparkasse | comdirect | Commerzbank |
|--------|-----------|-----------|-------------|
| URL-Muster | Instituts-spezifisch | `fints.comdirect.de` | `fints.commerzbank.de` |
| BLZ | Eine pro Institut | `20041166` | `20040000` |
| HKTAN-Version | Oft v6 erforderlich | v2/v3 | v2/v3 |
| TAN-Verfahren | chipTAN, smsTAN | photoTAN, pushTAN | photoTAN, pushTAN |
| SCA (PSD2) | Streng | Streng | Streng |
| Zertifikat | DVBank | Commerzbank Root | Commerzbank Root |

---

## 7. PSD2 & Zukunft von FinTS

### 7.1 Aktueller Status (2026)
- FinTS ist weiterhin **das Standard-Protokoll** für deutsches Online-Banking
- PSD2 / XS2A APIs existieren, aber sind **nicht flächendeckend** verfügbar
- Starke Kundenauthentifizierung (SCA) ist **Pflicht** seit 2021
- Alle Banken erfordern **Zwei-Schritt-TAN** für Überweisungen

### 7.2 TAN-Prozesse im FinTS-Kontext

1. **Schritt 1:** Dialog initialisieren (HKIDN + HKVVB + HKTAN)
2. **Schritt 2:** Bank sendet Challenge (z.B. photoTAN-Bild)
3. **Schritt 3:** Benutzer gibt TAN ein
4. **Schritt 4:** Client sendet TAN zurück (HKTAN + Auftrag)
5. **Schritt 5:** Bank verarbeitet Auftrag

**Decoupled-TAN** (pushTAN): TAN wird auf Smartphone bestätigt, Client pollt auf Fertigstellung.

---

## 8. Konkrete Empfehlungen für ktesis

### 8.1 Sofortmaßnahmen (Commerzbank-Problem)

1. **product_id formatieren:**
   ```python
   # Aktuell (25 Zeichen, aber möglicherweise falsches Format):
   product_id="9FA6681DEC0CF3046BFC2F8A6"
   
   # Testen mit (8 Zeichen + / + Version):
   product_id="9FA6681D/1"
   product_version="1.0"
   ```

2. **BLZ prüfen:**
   - Commerzbank: `20040000` (Haupt-BLZ)
   - comdirect: `20041166` (eigene BLZ!)

3. **Login für comdirect:**
   - comdirect verwendet die **Kontonummer** (8-stellig) als `user_id`
   - Nicht die 10-stellige Kundennummer
   - Nicht die 8-stellige Online-Banking-ID

4. **Debugging aktivieren:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
   Damit siehst du die **exakte Nachricht**, die python-fints sendet.

### 8.2 Test-Sequenz für comdirect

```python
from fints.client import FinTS3PinTanClient
from frappe.utils.password import get_decrypted_password

pin = get_decrypted_password("Bankkonto", "BKT-XXXX", "fints_pin")

# Test 1: Korrekte BLZ und URL
client = FinTS3PinTanClient(
    "20041166",           # comdirect BLZ
    "12345678",           # Kontonummer (8-stellig)
    pin,
    "https://fints.comdirect.de/fints",
    product_id="9FA6681D/1",   # Gekürzt auf Standardformat
    product_version="1.0"
)

# Test 2: TAN-Mechanismen abrufen
mechanisms = client.fetch_tan_mechanisms()
print(mechanisms)
```

### 8.3 Langfristige Architektur-Empfehlungen

1. **product_id aus Konfiguration lesen:**
   - Nicht hardcoded im Python-Code
   - In `ktesis/settings` oder `hooks.py` hinterlegen
   - Ermöglicht schnelles Wechseln bei Problemen

2. **Bank-spezifische Konfiguration:**
   ```python
   BANK_CONFIG = {
       "commerzbank": {
           "blz": "20040000",
           "url": "https://fints.commerzbank.de/fints",
           "login_type": "customer_number",
       },
       "comdirect": {
           "blz": "20041166",
           "url": "https://fints.comdirect.de/fints",
           "login_type": "account_number",
       }
   }
   ```

3. **Fehlercodes sauber behandeln:**
   - `9010` → product_id/Format-Problem
   - `9110` → Segmentstruktur-Problem (ggf. python-fints Version prüfen)
   - `9400` → PIN/Login falsch
   - `9800` → Dialog abgebrochen (Folgefehler)

4. **Alternative Bibliotheken evaluieren:**
   - `python-fints` ist kaum gewartet
   - `sepctrx` ist experimentell
   - `aqbanking` (C-Bibliothek) ist robuster, aber komplexer
   - Für Produktivbetrieb: Consider aqbanking Python-Bindings

### 8.4 Wichtige Warnung: python-fints Maintenance

- Letztes Release: 5.0 (2023)
- GitHub Issues häufen sich, werden kaum bearbeitet
- Keine Unterstützung für neue TAN-Verfahren (z.B. decoupled ist brüchig)
- **Für ktesis:** Überlege, ob FinTS-Integration langfristig auf aqbanking oder PSD2-API umgestellt werden sollte

---

## 9. Quellen & Referenzen

### Direkt abgefragte Ressourcen
- `https://fints.comdirect.de/fints` — Direkte Server-Antwort (Base64-FinTS)
- `https://fints.commerzbank.de/fints` — Direkte Server-Antwort (Base64-FinTS)
- `https://github.com/raphaelm/python-fints` — Source Code & Issues
- `https://python-fints.readthedocs.io` — Dokumentation

### Python-fints Source-Code (lokal analysiert)
- `fints/client.py` Zeile 170-192 (Konstruktor, product_id)
- `fints/dialog.py` Zeile 60-70 (HKVVB3 Erstellung)
- `fints/segments/auth.py` Zeile 25-35 (HKVVB3 Spezifikation)
- `fints/types.py` Zeile 10-70 (Längenvalidierung)
- `fints/security.py` Zeile 40-60 (HNVSK3 Erstellung)

### Relevante GitHub Issues
- **#84** — `9110 Falsche Segmentzusammenstellung` bei GLS Bank (HKTAN-Problem)
- **#73** — comdirect Kreditkartenkonto nicht SEPA
- **#212** — Commerzbank photoTAN Mechanismus 999 vs 900
- **#170** — "Could not find system_id" bei Sparkasse

### Spezifikationen
- FinTS 3.0 Master-Spezifikation — `hbci-zka.de` (redirect zu `fints.org`)
- `www.fints.org` — Offizielle FinTS-Webseite (Deutsche Kreditwirtschaft)

---

## 10. Glossar

| Begriff | Bedeutung |
|---------|-----------|
| **BLZ** | Bankleitzahl (8-stellig) |
| **BPD** | Bank-Parameter-Daten — Bank-Fähigkeiten |
| **HBCI** | Home Banking Computer Interface (Vorgänger von FinTS) |
| **FinTS** | Financial Transaction Services (aktueller Standard) |
| **HKTAN** | Segment für Zwei-Schritt-TAN |
| **HKVVB** | Verarbeitungsvorbereitung (enthält product_name) |
| **HNVSK** | Verschlüsselungskopf |
| **HNSHK** | Signaturkopf |
| **SCA** | Strong Customer Authentication (PSD2) |
| **UPD** | User-Parameter-Daten — Kunden-spezifische Einstellungen |
| **PIN/TAN** | Persönliche Identifikationsnummer / Transaktionsnummer |
| **product_id** | Hersteller-ID, registriert bei der Deutschen Kreditwirtschaft |
| **Segment** | Einzelne Dateneinheit in einer FinTS-Nachricht |
| **System-ID** | Vom Server vergebene Client-ID |
| **TAN** | Transaktionsnummer (Zwei-Faktor-Authentifizierung) |
