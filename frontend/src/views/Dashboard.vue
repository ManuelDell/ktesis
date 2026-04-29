<template>
  <div class="max-w-5xl w-full mx-auto p-5 pb-16 animate-[fadeIn_0.25s_ease]">
    <h2 class="text-2xl font-semibold text-ink-gray-9 mb-6">Dashboard</h2>

    <!-- KPI-Karten -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <KachelCard label="Fahrzeuge" :value="stats.fahrzeuge" icon="truck" type="count" />
      <KachelCard label="Wohnungen" :value="stats.wohnungen" icon="home" type="count" />
      <KachelCard label="Aktive Verträge" :value="stats.aktive_vertraege" icon="file-text" type="count" />
      <KachelCard label="Bank-Saldo" :value="fmtEuro(stats.bank_saldo)" icon="credit-card" type="money" />
      <KachelCard label="Darlehen" :value="fmtEuro(stats.darlehensbetrag)" icon="dollar-sign" type="money" />
      <KachelCard label="Restschuld" :value="fmtEuro(stats.restschuld)" icon="trending-down" type="negative" />
      <KachelCard label="Monatliche Kosten" :value="fmtEuro(stats.monatliche_kosten)" icon="euro" type="money" />
    </div>

    <!-- Vermögensübersicht -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-8">
      <!-- Nettovermögen Karte -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5 lg:col-span-1">
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
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5 lg:col-span-2">
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
              <p class="text-sm font-medium truncate">{{ v.titel }}</p>
              <p class="text-xs text-ink-gray-5">{{ v.vertragstyp }} · {{ v.vertragspartner || '—' }}</p>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <Badge
                :theme="v.ampel === 'rot' ? 'red' : v.ampel === 'gelb' ? 'amber' : 'green'"
                variant="subtle"
                size="sm"
              >
                {{ v.message }}
              </Badge>
              <span class="text-xs font-medium text-ink-gray-6">{{ fmtEuro(v.kosten_monatlich || v.kosten_jaehrlich) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Finance Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Bankkonten -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5">
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
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5">
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
            </div>
          </div>
        </div>
      </div>

      <!-- Vertragskosten -->
      <div class="bg-white border border-outline-gray-2 rounded-lg shadow-sm p-5">
        <h3 class="text-base font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="file-text" class="w-4 h-4 text-ink-gray-5" />
          Vertragskosten
        </h3>
        <div v-if="finance.vertragskosten" class="mb-3 pb-3 border-b border-outline-gray-1">
          <div class="flex justify-between text-sm">
            <span class="text-ink-gray-5">Monatlich</span>
            <span class="font-medium text-ink-gray-9">{{ fmtEuro(finance.vertragskosten.monatlich) }}</span>
          </div>
          <div class="flex justify-between text-sm mt-1">
            <span class="text-ink-gray-5">Jährlich</span>
            <span class="font-medium text-ink-gray-9">{{ fmtEuro(finance.vertragskosten.jaehrlich) }}</span>
          </div>
        </div>
        <div class="space-y-0">
          <div v-for="v in vertraege.slice(0, 5)" :key="v.name"
            class="flex justify-between items-center py-2 border-b border-outline-gray-1 last:border-0">
            <div class="min-w-0">
              <p class="font-medium text-ink-gray-9 text-sm truncate">{{ v.titel }}</p>
              <p class="text-xs text-ink-gray-5">{{ v.vertragstyp }} · {{ v.vertragspartner || '—' }}</p>
            </div>
            <p class="font-semibold text-ink-gray-9 text-sm flex-shrink-0">{{ fmtEuro(v.kosten_monatlich || v.kosten_jaehrlich) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FeatherIcon, Badge } from 'frappe-ui'
import KachelCard from '../components/KachelCard.vue'

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

function fmtEuro(n) {
  if (n == null) return '-'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)
}

function ampelCardClass(ampel) {
  switch (ampel) {
    case 'rot':
      return 'bg-surface-red-1 border-outline-red-1'
    case 'gelb':
      return 'bg-surface-amber-1 border-outline-amber-1'
    default:
      return 'bg-surface-gray-1 border-outline-gray-1'
  }
}

onMounted(async () => {
  try {
    const [statsData, financeData, vermoegenData] = await Promise.all([
      fetch('/api/method/ktesis.api.__init__.get_dashboard_stats').then(r => r.json()).then(d => d.message),
      fetch('/api/method/ktesis.api.dashboard.get_finance_summary').then(r => r.json()).then(d => d.message),
      fetch('/api/method/ktesis.api.dashboard.get_vermoegensentwicklung').then(r => r.json()).then(d => d.message),
    ])
    stats.value = statsData
    finance.value = financeData
    vermoegen.value = vermoegenData
  } catch (e) { console.error('Dashboard load error:', e) }

  ampelLoading.value = true
  try {
    const ampelData = await fetch('/api/method/ktesis.api.dashboard.get_vertrags_ampel')
      .then(r => r.json()).then(d => d.message)
    ampel.value = ampelData || []
    vertraege.value = ampelData || []
  } catch (e) {
    console.error('Ampel load error:', e)
  } finally {
    ampelLoading.value = false
  }
})
</script>
