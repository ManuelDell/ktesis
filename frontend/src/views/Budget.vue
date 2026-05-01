<template>
  <div class="p-5">
    <div class="flex items-center justify-between gap-4 mb-6">
      <h2 class="text-3xl font-semibold text-ink-gray-9">Budget</h2>
      <div class="flex items-center gap-3">
        <select v-model="selectedMonat" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm bg-white">
          <option v-for="m in monate" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
        <select v-model="selectedJahr" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm bg-white">
          <option v-for="j in jahre" :key="j" :value="j">{{ j }}</option>
        </select>
      </div>
    </div>

    <!-- Monatsübersicht -->
    <div v-if="uebersicht" class="grid grid-cols-3 gap-4 mb-8">
      <div class="bg-surface-green-1 border border-outline-green-2 rounded-lg p-4 text-center">
        <div class="text-sm text-ink-gray-5 mb-1">Einnahmen</div>
        <div class="text-2xl font-bold text-ink-green-3">{{ formatCurrency(uebersicht.einnahmen) }}</div>
      </div>
      <div class="bg-surface-red-1 border border-outline-red-2 rounded-lg p-4 text-center">
        <div class="text-sm text-ink-gray-5 mb-1">Ausgaben</div>
        <div class="text-2xl font-bold text-ink-red-4">{{ formatCurrency(uebersicht.ausgaben) }}</div>
      </div>
      <div class="rounded-lg p-4 text-center border" :class="uebersicht.saldo >= 0 ? 'bg-surface-green-1 border-outline-green-2' : 'bg-surface-red-1 border-outline-red-2'">
        <div class="text-sm text-ink-gray-5 mb-1">Saldo</div>
        <div class="text-2xl font-bold" :class="uebersicht.saldo >= 0 ? 'text-ink-green-3' : 'text-ink-red-4'">{{ formatCurrency(uebersicht.saldo) }}</div>
      </div>
    </div>

    <!-- Budget-Kategorien -->
    <div class="bg-white border border-outline-gray-2 rounded-lg overflow-hidden mb-8">
      <div class="px-4 py-3 border-b border-outline-gray-1 flex items-center justify-between">
        <h3 class="font-medium text-ink-gray-8">Soll-Ist-Vergleich</h3>
        <Button variant="outline" theme="gray" size="md" @click="showBudgetForm = !showBudgetForm">
          <span class="flex items-center gap-2 whitespace-nowrap">
            <FeatherIcon name="settings" class="w-4 h-4" />
            Budget bearbeiten
          </span>
        </Button>
      </div>
      <div class="divide-y divide-outline-gray-1">
        <div v-for="item in kategorien" :key="item.kategorie" class="px-4 py-3">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-ink-gray-8">{{ item.kategorie }}</span>
            <div class="text-sm">
              <span :class="item.ueberschritten ? 'text-ink-red-4 font-semibold' : 'text-ink-gray-6'">
                {{ formatCurrency(item.ist) }}
              </span>
              <span class="text-ink-gray-4 mx-1">/</span>
              <span class="text-ink-gray-5">{{ item.budget > 0 ? formatCurrency(item.budget) : '—' }}</span>
            </div>
          </div>
          <div v-if="item.budget > 0" class="h-2 bg-surface-gray-2 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all"
              :class="item.ueberschritten ? 'bg-ink-red-4' : 'bg-ink-green-3'"
              :style="{ width: Math.min((item.ist / item.budget) * 100, 100) + '%' }"
            />
          </div>
          <div v-else class="text-xs text-ink-gray-4 mt-1">Kein Budget definiert</div>
        </div>
      </div>
    </div>

    <!-- Budget-Bearbeitung -->
    <div v-if="showBudgetForm" class="bg-white border border-outline-gray-2 rounded-lg p-5">
      <h3 class="font-medium text-ink-gray-8 mb-4">Budget-Posten bearbeiten</h3>
      <div v-if="loadingBudgets" class="text-center py-4 text-ink-gray-4">Lade...</div>
      <div v-else class="space-y-3">
        <div v-for="kat in alleKategorien" :key="kat" class="flex items-center gap-4">
          <span class="w-32 text-sm text-ink-gray-7 shrink-0">{{ kat }}</span>
          <input
            type="number"
            min="0"
            step="10"
            :value="budgetForm[kat] || ''"
            @input="budgetForm[kat] = parseFloat($event.target.value) || 0"
            placeholder="0,00"
            class="border border-outline-gray-3 rounded-md px-3 py-1.5 text-sm w-36"
          />
          <span class="text-xs text-ink-gray-4">€/Monat</span>
        </div>
        <div class="flex justify-end gap-3 pt-3">
          <Button variant="outline" theme="gray" @click="showBudgetForm = false">Abbrechen</Button>
          <Button variant="solid" theme="gray" :loading="savingBudget" @click="saveBudgets">Speichern</Button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'

const { call, list, create, update, delete: delete_ } = useApi()

const alleKategorien = ["Wohnen", "Mobilitaet", "Versicherung", "Lebensmittel", "Freizeit", "Einkommen", "Sonstiges"]

const now = new Date()
const selectedMonat = ref(now.getMonth() + 1)
const selectedJahr = ref(now.getFullYear())
const kategorien = ref([])
const uebersicht = ref(null)
const showBudgetForm = ref(false)
const loadingBudgets = ref(false)
const savingBudget = ref(false)
const budgetForm = ref({})
const existingBudgets = ref([])

const monate = [
  { value: 1, label: 'Januar' }, { value: 2, label: 'Februar' },
  { value: 3, label: 'März' }, { value: 4, label: 'April' },
  { value: 5, label: 'Mai' }, { value: 6, label: 'Juni' },
  { value: 7, label: 'Juli' }, { value: 8, label: 'August' },
  { value: 9, label: 'September' }, { value: 10, label: 'Oktober' },
  { value: 11, label: 'November' }, { value: 12, label: 'Dezember' },
]

const jahre = computed(() => {
  const y = now.getFullYear()
  return [y - 2, y - 1, y, y + 1]
})

async function loadData() {
  const [budgetRes, uebRes] = await Promise.all([
    call('ktesis.api.dashboard.get_budget_vs_ist', { monat: selectedMonat.value, jahr: selectedJahr.value }),
    call('ktesis.api.dashboard.get_monatsuebersicht', { monat: selectedMonat.value, jahr: selectedJahr.value }),
  ])
  kategorien.value = budgetRes.kategorien || []
  uebersicht.value = uebRes
}

async function loadBudgetForm() {
  loadingBudgets.value = true
  try {
    const all = await list('Budgetposten')
    existingBudgets.value = all || []
    const form = {}
    for (const b of all) {
      form[b.kategorie] = b.betrag_monatlich
    }
    budgetForm.value = form
  } finally {
    loadingBudgets.value = false
  }
}

async function saveBudgets() {
  savingBudget.value = true
  try {
    for (const kat of alleKategorien) {
      const betrag = budgetForm.value[kat] || 0
      const existing = existingBudgets.value.find(b => b.kategorie === kat)
      if (existing) {
        await update('Budgetposten', existing.name, { betrag_monatlich: betrag })
      } else if (betrag > 0) {
        await create('Budgetposten', { kategorie: kat, betrag_monatlich: betrag })
      }
    }
    showBudgetForm.value = false
    await loadData()
    await loadBudgetForm()
  } finally {
    savingBudget.value = false
  }
}

function formatCurrency(value) {
  if (value == null) return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

watch([selectedMonat, selectedJahr], loadData)
watch(showBudgetForm, (v) => { if (v) loadBudgetForm() })

onMounted(loadData)
</script>
