<template>
  <div class="max-w-5xl w-full mx-auto py-5 px-3 sm:px-5 pb-16 animate-[fadeIn_0.25s_ease]">
    <h2 class="text-2xl font-semibold text-ink-gray-9 mb-6">Dashboard</h2>

    <!-- KPI-Karten -->
    <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <KachelCard label="Fahrzeuge" :value="stats.fahrzeuge" icon="truck" type="count" />
      <KachelCard label="Wohnungen" :value="stats.wohnungen" icon="home" type="count" />
      <KachelCard label="Aktive Verträge" :value="stats.aktive_vertraege" icon="file-text" type="count" />
      <KachelCard label="Bank-Saldo" :value="fmtEuro(stats.bank_saldo)" icon="credit-card" type="money" />
      <KachelCard label="Darlehen" :value="fmtEuro(stats.darlehensbetrag)" icon="dollar-sign" type="money" />
      <KachelCard label="Restschuld" :value="fmtEuro(stats.restschuld)" icon="trending-down" type="negative" />
      <KachelCard label="Monatliche Kosten" :value="fmtEuro(stats.monatliche_kosten + savedSondertilgungenTotal)" icon="bar-chart-2" type="money" />
    </div>

    <!-- Vermögensübersicht -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-8">
      <!-- Nettovermögen Karte -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5 lg:col-span-1">
        <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="pie-chart" class="w-4 h-4 text-ink-gray-5" />
          Vermögen
        </h3>
        <div class="space-y-4">
          <div>
            <p class="text-xs text-ink-gray-5">Nettovermögen</p>
            <p class="text-2xl font-semibold text-ink-gray-9">{{ fmtEuro(vermoegen.nettovermoegen) }}</p>
          </div>
          <div class="h-px bg-outline-gray-2" />
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-ink-gray-5">Immobilien</span>
              <span class="font-medium text-ink-gray-9">{{ fmtEuro(vermoegen.immobilien_wert) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-ink-gray-5">Fahrzeuge</span>
              <span class="font-medium text-ink-gray-9">{{ fmtEuro(vermoegen.fahrzeuge_wert) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-ink-gray-5">Bankguthaben</span>
              <span class="font-medium text-ink-gray-9">{{ fmtEuro(vermoegen.bank_saldo) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-ink-gray-5">Restschulden</span>
              <span class="font-medium text-ink-red-4">-{{ fmtEuro(vermoegen.restschuld) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Vertrags-Ampel -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5 lg:col-span-2">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-semibold text-ink-gray-9 flex items-center gap-2">
            <FeatherIcon name="alert-circle" class="w-4 h-4 text-ink-gray-5" />
            Vertragsampel
          </h3>
          <div class="flex items-center gap-3 text-xs">
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-surface-green-2 border border-outline-green-2" /> Grün</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-surface-amber-1 border border-outline-amber-2" /> Gelb</span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-surface-red-2 border border-outline-red-2" /> Rot</span>
          </div>
        </div>

        <div v-if="ampelLoading" class="text-center py-8 text-ink-gray-4">Lade Vertragsampel...</div>
        <div v-else-if="ampel.length === 0" class="text-center py-8 text-ink-gray-4">Keine aktiven Verträge.</div>
        <div v-else class="space-y-2 max-h-72 overflow-y-auto pr-1">
          <div
            v-for="v in ampel"
            :key="v.name"
            class="flex items-center justify-between p-3 rounded-lg border"
            :class="ampelCardClass(v.ampel)"
          >
            <div class="min-w-0">
              <p class="text-sm font-medium line-clamp-1">{{ v.titel }}</p>
              <p class="text-xs text-ink-gray-5 line-clamp-1">{{ v.vertragstyp }} · {{ v.vertragspartner || '—' }}</p>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <Badge
                :theme="v.ampel === 'rot' ? 'red' : v.ampel === 'gelb' ? 'amber' : 'green'"
                variant="subtle"
                size="sm"
              >
                {{ v.message }}
              </Badge>
              <span class="text-xs font-medium text-ink-gray-6">{{ kostenAnzeige(v) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Finance Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Bankkonten -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5">
        <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="credit-card" class="w-4 h-4 text-ink-gray-5" />
          Bankkonten
        </h3>
        <div class="space-y-0">
          <div v-for="k in finance.bankkonten" :key="k.name"
            class="flex justify-between items-center py-2.5 border-b border-outline-gray-1 last:border-0">
            <div>
              <p class="font-medium text-ink-gray-9 text-sm">{{ k.bezeichnung || k.name }}</p>
              <p class="text-xs text-ink-gray-5">{{ k.kontotyp || '' }}</p>
            </div>
            <p class="font-semibold text-ink-gray-9 text-sm">{{ fmtEuro(k.kontostand_manuell) }}</p>
          </div>
        </div>
      </div>

      <!-- Darlehen -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5">
        <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="dollar-sign" class="w-4 h-4 text-ink-gray-5" />
          Darlehen
        </h3>
        <div class="space-y-0">
          <div v-for="d in finance.darlehen" :key="d.name"
            class="flex justify-between items-center py-2.5 border-b border-outline-gray-1 last:border-0">
            <div>
              <p class="font-medium text-ink-gray-9 text-sm">{{ d.bezeichnung }}</p>
              <p class="text-xs text-ink-gray-5">{{ d.darlehensgeber }} · {{ d.zinssatz }} %</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-ink-red-4 text-sm">-{{ fmtEuro(d.restschuld) }}</p>
              <p class="text-xs text-ink-gray-5">{{ fmtEuro(d.monatliche_rate) }}/Monat</p>
              <p v-if="getSavedSondertilgung(d.name) > 0" class="text-xs text-ink-green-3 mt-0.5">
                + {{ fmtEuro(getSavedSondertilgung(d.name)) }}/Mo Sondertilgung → Total: {{ fmtEuro((d.monatliche_rate || 0) + getSavedSondertilgung(d.name)) }}/Mo
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Vertragskosten -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5">
        <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="file-text" class="w-4 h-4 text-ink-gray-5" />
          Vertragskosten
        </h3>
        <div v-if="finance.vertragskosten" class="space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-ink-gray-5 mb-0.5">Monatliche Belastung</p>
              <p class="text-2xl font-bold text-ink-gray-9">{{ fmtEuro((finance.vertragskosten.monatlich || 0) + savedSondertilgungenTotal) }}</p>
            </div>
            <div class="text-right">
              <p class="text-xs text-ink-gray-5 mb-0.5">Jährliche Belastung</p>
              <p class="text-2xl font-bold text-ink-gray-9">{{ fmtEuro((finance.vertragskosten.jaehrlich || 0) + savedSondertilgungenTotal * 12) }}</p>
            </div>
          </div>
          <div v-if="finance.vertragskosten.vertraege?.length" class="border-t border-outline-gray-1 pt-2 space-y-0">
            <div v-for="v in finance.vertragskosten.vertraege" :key="v.name"
              class="flex justify-between items-center py-2 border-b border-outline-gray-1 last:border-0 text-sm">
              <div class="min-w-0">
                <p class="font-medium text-ink-gray-9">{{ v.titel }}</p>
                <p class="text-xs text-ink-gray-4">{{ faelligLabel(v) }}</p>
              </div>
              <div class="text-right shrink-0 ml-3">
                <p class="font-semibold text-ink-gray-9">{{ zahlungBetrag(v) }}</p>
                <p class="text-xs text-ink-gray-4">{{ rhythmusKurz(v.zahlungsrhythmus) }}</p>
              </div>
            </div>
            <template v-for="d in finance.darlehen" :key="'st-' + d.name">
              <div v-if="getSavedSondertilgung(d.name) > 0" class="flex justify-between items-center py-2 border-b border-outline-gray-1 last:border-0 text-sm">
                <div class="min-w-0">
                  <p class="font-medium text-ink-gray-9">{{ d.bezeichnung }}</p>
                  <p class="text-xs text-ink-gray-4">Sondertilgung (gespeichert)</p>
                </div>
                <div class="text-right shrink-0 ml-3">
                  <p class="font-semibold text-ink-gray-9">{{ fmtEuro(getSavedSondertilgung(d.name)) }}</p>
                  <p class="text-xs text-ink-gray-4">monatlich</p>
                </div>
              </div>
            </template>
          </div>
        </div>
        <div v-else class="text-sm text-ink-gray-4">Keine Vertragskosten erfasst</div>
      </div>
    </div>
    <!-- Einnahmen / Ausgaben Chart -->
    <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5 mt-5">
      <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
        <FeatherIcon name="bar-chart-2" class="w-4 h-4 text-ink-gray-5" />
        Einnahmen & Ausgaben (12 Monate)
      </h3>
      <div class="relative h-52 sm:h-40">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>

    <!-- Was-wäre-wenn Tilgungsrechner -->
    <div v-if="finance.darlehen && finance.darlehen.length" class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-3 sm:p-5 mt-5">
      <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
        <FeatherIcon name="sliders" class="w-4 h-4 text-ink-gray-5" />
        Was wäre wenn? — Sondertilgung
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="text-sm text-ink-gray-6 mb-1 block">Darlehen auswählen</label>
          <select v-model="tilgungDarlehenIdx" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm w-full bg-white">
            <option v-for="(d, i) in finance.darlehen" :key="d.name" :value="i">{{ d.bezeichnung }}</option>
          </select>
          <label class="text-sm text-ink-gray-6 mt-4 mb-1 block">
            Zusätzliche Tilgung: <strong>{{ extraTilgung }} €/Monat</strong>
          </label>
          <input type="range" v-model.number="extraTilgung" min="0" :max="maxSondertilgungMonatlich" step="25" class="w-full" />
          <p class="text-xs text-ink-gray-4 mt-1">
            Max. erlaubt: {{ fmtEuro(maxSondertilgungMonatlich) }}/Monat
            ({{ finance?.darlehen?.[tilgungDarlehenIdx]?.sondertilgungssatz || 5 }}% p.a.)
          </p>
          <p v-if="extraTilgung >= maxSondertilgungMonatlich && maxSondertilgungMonatlich > 0"
             class="text-xs text-ink-yellow-3 mt-1">
            ⚠ Limit erreicht — höhere Sondertilgung vertraglich nicht erlaubt
          </p>
        </div>
        <div v-if="tilgungErgebnis" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-surface-gray-1 rounded-lg p-3 text-center">
              <div class="text-xs text-ink-gray-5 mb-1">Laufzeit heute</div>
              <div class="font-semibold text-ink-gray-9">{{ tilgungErgebnis.monate_alt }} Mo.</div>
            </div>
            <div class="bg-surface-green-1 rounded-lg p-3 text-center border border-outline-green-2">
              <div class="text-xs text-ink-gray-5 mb-1">Laufzeit neu</div>
              <div class="font-semibold text-ink-green-3">{{ tilgungErgebnis.monate_neu }} Mo.</div>
            </div>
          </div>
          <div class="bg-surface-green-1 border border-outline-green-2 rounded-lg p-3 text-center">
            <div class="text-xs text-ink-gray-5 mb-1">Zinsersparnis</div>
            <div class="text-lg font-bold text-ink-green-3">{{ fmtEuro(tilgungErgebnis.zinsersparnis) }}</div>
          </div>
          <div class="bg-surface-gray-1 border border-outline-gray-2 rounded-lg p-3">
            <div class="text-xs text-ink-gray-5 mb-2">Monatliche Belastung bei Sondertilgung</div>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-ink-gray-6">Reguläre Rate</span>
                <span class="font-medium text-ink-gray-9">{{ fmtEuro(finance.darlehen[tilgungDarlehenIdx].monatliche_rate) }}</span>
              </div>
              <div v-if="extraTilgung > 0" class="flex justify-between">
                <span class="text-ink-gray-6">+ Sondertilgung</span>
                <span class="font-medium text-ink-gray-9">{{ fmtEuro(extraTilgung) }}</span>
              </div>
              <div class="h-px bg-outline-gray-2 my-1" />
              <div class="flex justify-between font-bold">
                <span class="text-ink-gray-9">Gesamt</span>
                <span class="text-ink-gray-9">{{ fmtEuro((finance.darlehen[tilgungDarlehenIdx].monatliche_rate || 0) + extraTilgung) }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-between">
            <button @click="saveSondertilgung" class="px-3 py-1.5 bg-white border border-outline-gray-3 rounded-md text-xs font-medium text-ink-gray-7 hover:bg-surface-gray-1 transition-colors">
              Sondertilgung speichern
            </button>
            <span v-if="savedMsg" class="text-xs text-ink-green-3 font-medium">Gespeichert ✓</span>
          </div>
        </div>
      </div>
    </div>

    </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { Chart, BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, BarController, LineController } from 'chart.js'
Chart.register(BarElement, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, BarController, LineController)
import { FeatherIcon, Badge } from 'frappe-ui'
import KachelCard from '../components/KachelCard.vue'
import { useApi } from '../composables/useApi.js'

const stats = ref({
  fahrzeuge: 0, wohnungen: 0, aktive_vertraege: 0,
  bank_saldo: 0, darlehensbetrag: 0,
  restschuld: 0, monatliche_kosten: 0,
})
const finance = ref({ bankkonten: [], darlehen: [], vertragskosten: {} })
const vertraege = ref([])
const vermoegen = ref({
  immobilien_wert: 0, fahrzeuge_wert: 0, bank_saldo: 0,
  restschuld: 0, nettovermoegen: 0, bruttovermoegen: 0,
})
const ampel = ref([])
const ampelLoading = ref(false)
const chartCanvas = ref(null)
let chartInstance = null
const tilgungDarlehenIdx = ref(0)
const extraTilgung = ref(0)
const savedMsg = ref(false)
const savedSondertilgungenTotal = ref(0)

// Trendlinie berechnen (gleitender 3-Monats-Durchschnitt)
function movingAvg(data, window = 3) {
  return data.map((_, i) => {
    const slice = data.slice(Math.max(0, i - window + 1), i + 1)
    return slice.reduce((a, b) => a + b, 0) / slice.length
  })
}

const maxSondertilgungMonatlich = computed(() => {
  const d = finance.value?.darlehen?.[tilgungDarlehenIdx.value]
  if (!d) return 500
  const satz = parseFloat(d.sondertilgungssatz || 5)
  const betrag = parseFloat(d.darlehensbetrag || 0)
  if (!betrag) return 500
  return Math.round(betrag * satz / 100 / 12)
})

function sondertilgungKey(name) {
  return `ktesis_sondertilgung_${name}`
}

function getSavedSondertilgung(name) {
  const v = localStorage.getItem(sondertilgungKey(name))
  return v ? parseFloat(v) : 0
}

function loadSondertilgung(idx) {
  const d = finance.value?.darlehen?.[idx]
  if (!d) return
  extraTilgung.value = getSavedSondertilgung(d.name)
}

function saveSondertilgung() {
  const d = finance.value?.darlehen?.[tilgungDarlehenIdx.value]
  if (!d) return
  localStorage.setItem(sondertilgungKey(d.name), String(extraTilgung.value))
  savedMsg.value = true
  setTimeout(() => { savedMsg.value = false }, 2000)
  computeSavedTotal()
}

function computeSavedTotal() {
  const darlehen = finance.value?.darlehen || []
  savedSondertilgungenTotal.value = darlehen.reduce((sum, d) => sum + getSavedSondertilgung(d.name), 0)
}

watch(tilgungDarlehenIdx, (newVal) => {
  loadSondertilgung(newVal)
})

function zahlungBetrag(v) {
  const km = v.kosten_monatlich || 0
  const kj = v.kosten_jaehrlich || 0
  switch (v.zahlungsrhythmus) {
    case 'Monatlich': return fmtEuro(km)
    case 'Vierteljährlich': return fmtEuro(kj / 4)
    case 'Halbjährlich': return fmtEuro(kj / 2)
    case 'Jährlich': return fmtEuro(kj)
    case 'Einmalig': return fmtEuro(km || kj)
    default: return km ? fmtEuro(km) : fmtEuro(kj)
  }
}

function rhythmusKurz(r) {
  const map = { 'Monatlich': 'monatlich', 'Vierteljährlich': 'vierteljährlich',
                'Halbjährlich': 'halbjährlich', 'Jährlich': 'jährlich', 'Einmalig': 'einmalig' }
  return map[r] || r || ''
}

function faelligLabel(v) {
  if (!v.vertragsbeginn) return v.vertragstyp || ''
  const d = new Date(v.vertragsbeginn)
  const tag = d.getUTCDate()
  const mon = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez']
  const r = v.zahlungsrhythmus || ''
  if (r === 'Monatlich') return `${tag}. jeden Monat`
  if (r === 'Jährlich') return `${tag}. ${mon[d.getUTCMonth()]}`
  if (r === 'Vierteljährlich') {
    const m = d.getUTCMonth()
    return `${tag}. ` + [0,1,2,3].map(i => mon[(m + i * 3) % 12]).join(' · ')
  }
  if (r === 'Halbjährlich') {
    const m = d.getUTCMonth()
    return `${tag}. ${mon[m]} + ${mon[(m + 6) % 12]}`
  }
  if (r === 'Einmalig') return 'Einmalig'
  return v.vertragstyp || ''
}

function fmtEuro(n) {
  if (n == null) return '-'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)
}

function kostenAnzeige(v) {
  const m = v.kosten_monatlich || (v.kosten_jaehrlich ? v.kosten_jaehrlich / 12 : null)
  const j = v.kosten_jaehrlich || (v.kosten_monatlich ? v.kosten_monatlich * 12 : null)
  if (m && j) return `${fmtEuro(m)}/Mo · ${fmtEuro(j)}/J`
  if (m) return `${fmtEuro(m)}/Mo`
  if (j) return `${fmtEuro(j)}/J`
  return '—'
}

function ampelCardClass(color) {
  switch (color) {
    case 'rot': return 'bg-surface-red-1 border-outline-red-1'
    case 'gelb': return 'bg-surface-amber-1 border-outline-amber-1'
    default: return 'bg-surface-gray-1 border-outline-gray-1'
  }
}

function berechneTilgung(restschuld, zinssatz, monatsrate, extra, maxExtra) {
  if (!restschuld || !monatsrate || monatsrate <= 0) return null
  const effektiveSondertilgung = Math.min(extra, maxExtra || Infinity)
  const monatszins = (zinssatz || 0) / 100 / 12
  function calc(rate) {
    let schuld = restschuld, zinsen = 0, monate = 0
    while (schuld > 0.01 && monate < 600) {
      const z = schuld * monatszins; zinsen += z; schuld = schuld + z - rate
      if (schuld < 0) schuld = 0; monate++
    }
    return { monate, zinsen }
  }
  const alt = calc(monatsrate), neu = calc(monatsrate + effektiveSondertilgung)
  return { monate_alt: alt.monate, monate_neu: neu.monate, zinsersparnis: Math.max(0, alt.zinsen - neu.zinsen) }
}

const tilgungErgebnis = computed(() => {
  const d = finance.value.darlehen?.[tilgungDarlehenIdx.value]
  if (!d) return null
  return berechneTilgung(d.restschuld, d.zinssatz, d.monatliche_rate, extraTilgung.value, maxSondertilgungMonatlich.value)
})

onMounted(async () => {
  const { call } = useApi()
  try {
    const [statsData, financeData, vermoegenData] = await Promise.all([
      call('ktesis.api.get_dashboard_stats'),
      call('ktesis.api.dashboard.get_finance_summary'),
      call('ktesis.api.dashboard.get_vermoegensentwicklung'),
    ])
    stats.value = statsData
    finance.value = financeData
    vermoegen.value = vermoegenData
  } catch (e) { console.error('Dashboard load error:', e) }

  // Lade gespeicherte Sondertilgung für das erste Darlehen
  loadSondertilgung(0)
  computeSavedTotal()

  ampelLoading.value = true
  try {
    const ampelData = await call('ktesis.api.dashboard.get_vertrags_ampel')
    ampel.value = ampelData || []
    vertraege.value = ampelData || []
  } catch (e) {
    console.error('Ampel load error:', e)
  } finally {
    ampelLoading.value = false
  }

  try {
    const verlaufData = await call('ktesis.api.dashboard.get_buchungen_verlauf', { monate: 12 })
    await nextTick()
    if (chartCanvas.value) {
      chartInstance = new Chart(chartCanvas.value, {
        type: 'bar',
        data: {
          labels: verlaufData.map(r => r.label),
          datasets: [
            { label: 'Einnahmen', data: verlaufData.map(r => r.einnahmen), backgroundColor: 'rgba(34,197,94,0.6)', borderRadius: 4, order: 1, },
            { label: 'Ausgaben', data: verlaufData.map(r => Math.abs(r.ausgaben)), backgroundColor: 'rgba(239,68,68,0.6)', borderRadius: 4, order: 1, },
            {
              type: 'line',
              label: 'Trend Einnahmen',
              data: movingAvg(verlaufData.map(r => r.einnahmen)),
              borderColor: 'rgba(34,197,94,0.9)',
              backgroundColor: 'transparent',
              borderWidth: 2,
              pointRadius: 3,
              tension: 0.4,
              order: 2,
            },
            {
              type: 'line',
              label: 'Trend Ausgaben',
              data: movingAvg(verlaufData.map(r => Math.abs(r.ausgaben))),
              borderColor: 'rgba(239,68,68,0.9)',
              backgroundColor: 'transparent',
              borderWidth: 2,
              pointRadius: 3,
              tension: 0.4,
              order: 2,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } },
          scales: { y: { beginAtZero: true } }
        },
      })
    }
  } catch (e) { console.error('Chart error:', e) }
})
</script>
