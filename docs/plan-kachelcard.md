# KachelCard — Design-Vorschlag (gesondert)

**Status:** Gesonderter Plan, nicht Teil von Phase 4.

**Ziel:** Monochrome, professionelle KPI-Karten ohne "Regenbogen"-Farben. Clean wie Gameplan.

---

## Aktuelles Problem

- `color` Prop wird vom Dashboard übergeben (`rust`, `olive`, `amber`, `sky`) aber im Component ignoriert
- Karten sind funktional, aber visuell austauschbar
- Keine visuelle Hierarchie zwischen Zählern (Fahrzeuge, Wohnungen) und Geldbeträgen (Bank-Saldo, Restschuld)

---

## Option A — Minimal & Monochrome (Empfohlen)

**Philosophie:** Gar keine Farben. Unterschiedliche KPI-Typen durch Layout und Icon-Position unterscheiden.

### Features:
- **Zähler-Karten** (Fahrzeuge, Wohnungen, Aktive Verträge): Zahl zentriert, Icon oben rechts
- **Geld-Karten** (Bank-Saldo, Darlehen, Restschuld, Monatliche Kosten): Betrag rechtsbündig fett, Label oben links
- **Restschuld** bekommt automatisch `text-ink-red-4` (negativ)
- **Bank-Saldo** positiv: `text-ink-gray-9`
- Keine `color` Prop nötig — Logik basiert auf `label`
- Subtiler Hover-Effekt (`hover:shadow-md`)

### Dashboard-Änderung:
```vue
<KachelCard label="Fahrzeuge" :value="stats.fahrzeuge" icon="truck" type="count" />
<KachelCard label="Bank-Saldo" :value="fmtEuro(stats.bank_saldo)" icon="credit-card" type="money" />
<KachelCard label="Restschuld" :value="fmtEuro(stats.restschuld)" icon="trending-down" type="negative" />
```

---

## Option B — Subtile Icon-Farbe

**Philosophie:** Monochrome Karte, aber das Icon hat eine sehr subtile Farbe je nach KPI-Typ.

### Features:
- Karte bleibt weiß/grau (keine bunten Rahmen/Hintergründe)
- Icon bekommt `text-ink-gray-4` als Default
- Nur für **negative Werte** (Restschuld): Icon `text-ink-red-4`
- Nur für **positive Vermögenswerte** (Bank-Saldo): Icon `text-ink-green-4`
- Alle anderen: neutral

### Vorteil:
- Minimaler Farbeinsatz
- Rot/Grün hat sofortige Bedeutung (Verlust/Gewinn)
- Keine "Regenbogen"

---

## Option C — Gar keine KachelCard

**Philosophie:** KPIs direkt im Dashboard inline rendern, kein separates Component.

### Features:
- KachelCard.vue löschen
- KPIs als einfache Grid-Items im Dashboard
- Weniger Abstraktion, weniger Dateien
- Einfacher anzupassen

### Nachteil:
- Wiederverwendbarkeit verloren (falls KPIs woanders gebraucht)
- Dashboard.vue wird länger

---

## Empfehlung

**Option A** — Minimal & Monochrome mit `type` Prop:
- Löscht `color` Prop komplett
- Führt `type` Prop ein (`count` | `money` | `negative`)
- Dashboard übergibt `type` statt `color`
- KachelCard rendert je nach Typ unterschiedliches Layout
- Keine Farben außer Rot für negative Werte
- Professionell, clean, Gameplan-ähnlich

**Dateien:**
- Modify: `components/KachelCard.vue`
- Modify: `views/Dashboard.vue`

**Aufwand:** ~10–15 Minuten

---

## Umsetzung (Beispielcode)

### KachelCard.vue:
```vue
<template>
  <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5 hover:shadow-md transition-shadow"
    :class="layoutClass">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-ink-gray-4">{{ label }}</p>
        <p class="text-2xl font-semibold mt-1" :class="valueClass">{{ value }}</p>
      </div>
      <FeatherIcon :name="icon" class="w-5 h-5 text-ink-gray-4" />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  label: String,
  value: [String, Number],
  icon: { type: String, default: 'bar-chart-2' },
  type: { type: String, default: 'count' } // count | money | negative
})

const valueClass = computed(() => {
  if (props.type === 'negative') return 'text-ink-red-4'
  return 'text-ink-gray-9'
})
</script>
```

### Dashboard.vue (Auszug):
```vue
<KachelCard label="Fahrzeuge" :value="stats.fahrzeuge" icon="truck" type="count" />
<KachelCard label="Wohnungen" :value="stats.wohnungen" icon="home" type="count" />
<KachelCard label="Aktive Verträge" :value="stats.aktive_vertraege" icon="file-text" type="count" />
<KachelCard label="Bank-Saldo" :value="fmtEuro(stats.bank_saldo)" icon="credit-card" type="money" />
<KachelCard label="Darlehen" :value="fmtEuro(stats.darlehensbetrag)" icon="dollar-sign" type="money" />
<KachelCard label="Restschuld" :value="fmtEuro(stats.restschuld)" icon="trending-down" type="negative" />
<KachelCard label="Monatliche Kosten" :value="fmtEuro(stats.monatliche_kosten)" icon="euro" type="money" />
```
