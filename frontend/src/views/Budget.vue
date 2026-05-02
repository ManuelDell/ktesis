<template>
  <div class="p-5">
    <div class="flex items-center justify-between gap-4 mb-6">
      <h2 class="text-3xl font-semibold text-ink-gray-9">Budget</h2>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <Button
            :variant="viewMode === 'monat' ? 'solid' : 'outline'"
            theme="gray" size="sm"
            @click="viewMode = 'monat'"
          >Monat</Button>
          <Button
            :variant="viewMode === 'jahr' ? 'solid' : 'outline'"
            theme="gray" size="sm"
            @click="viewMode = 'jahr'"
          >Jahr</Button>
        </div>
        <div v-if="viewMode === 'monat'" class="flex items-center gap-3">
          <select v-model="selectedMonat" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm bg-white">
            <option v-for="m in monate" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
          <select v-model="selectedJahr" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm bg-white">
            <option v-for="j in jahre" :key="j" :value="j">{{ j }}</option>
          </select>
        </div>
        <div v-else class="flex items-center gap-3">
          <select v-model="selectedJahr" class="border border-outline-gray-3 rounded-md px-3 py-2 text-sm bg-white">
            <option v-for="j in jahre" :key="j" :value="j">{{ j }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Monatsübersicht -->
    <div v-if="viewMode === 'monat' && uebersicht" class="grid grid-cols-3 gap-4 mb-8">
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

    <template v-if="viewMode === 'monat'">
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
          <div v-for="item in kategorien" :key="item.kategorie" class="px-4 py-3 cursor-pointer hover:bg-surface-gray-1 transition-colors" @click="toggleKat(item.kategorie)">
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
            <!-- Aufklappbare Buchungsliste -->
            <div v-if="expandedKat === item.kategorie && buchungenByKat[item.kategorie]" class="mt-2 space-y-1">
              <div v-if="!buchungenByKat[item.kategorie].length" class="text-xs text-ink-gray-4 pl-1">Keine Buchungen in diesem Monat</div>
              <div
                v-for="b in buchungenByKat[item.kategorie]"
                :key="b.name"
                class="flex items-center justify-between text-xs px-2 py-1 rounded bg-surface-gray-1"
              >
                <span class="text-ink-gray-5 shrink-0 mr-2">{{ formatDate(b.datum) }}</span>
                <span class="text-ink-gray-7 truncate flex-1">{{ b.buchungstext }}</span>
                <span class="text-ink-red-4 font-medium ml-2 shrink-0">{{ formatCurrency(b.betrag) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Budgettöpfe verwalten -->
      <div v-if="showBudgetForm" class="bg-white border border-outline-gray-2 rounded-lg p-5 mb-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-medium text-ink-gray-8">Budgettöpfe verwalten</h3>
          <Button variant="solid" theme="gray" size="md" @click="addNewBudgettopf">
            <span class="flex items-center gap-2 whitespace-nowrap">
              <FeatherIcon name="plus" class="w-4 h-4" />
              Neuer Budgettopf
            </span>
          </Button>
        </div>

        <div v-if="loadingBudgets" class="text-center py-4 text-ink-gray-4">Lade...</div>
        <div v-else>
          <div v-if="!editableBudgets.length" class="text-center py-6 text-ink-gray-4 text-sm">
            Noch keine Budgettöpfe. Erstelle deinen ersten!
          </div>
          <table v-else class="w-full text-sm">
            <thead>
              <tr class="border-b border-outline-gray-2">
                <th class="text-left py-2 px-3 font-medium text-ink-gray-5">Name</th>
                <th class="text-left py-2 px-3 font-medium text-ink-gray-5">€/Monat</th>
                <th class="text-left py-2 px-3 font-medium text-ink-gray-5 w-32">Notiz</th>
                <th class="py-2 px-3 w-24"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(b, i) in editableBudgets" :key="b._key" class="border-b border-outline-gray-1">
                <td class="py-2 px-3">
                  <input
                    v-model="b.kategorie"
                    type="text"
                    placeholder="z.B. Urlaub"
                    class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-full"
                  />
                </td>
                <td class="py-2 px-3">
                  <input
                    v-model.number="b.betrag_monatlich"
                    type="number"
                    min="0"
                    step="10"
                    placeholder="0"
                    class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-28"
                  />
                </td>
                <td class="py-2 px-3">
                  <input
                    v-model="b.notiz"
                    type="text"
                    placeholder="optional"
                    class="border border-outline-gray-2 rounded px-2 py-1 text-sm w-full"
                  />
                </td>
                <td class="py-2 px-3">
                  <div class="flex items-center gap-2">
                    <Button variant="solid" theme="gray" size="sm" :loading="b._saving" @click="saveBudgettopf(b)">
                      <FeatherIcon name="check" class="w-3 h-3" />
                    </Button>
                    <Button variant="outline" theme="red" size="sm" :loading="b._deleting" @click="deleteBudgettopf(b, i)">
                      <FeatherIcon name="trash-2" class="w-3 h-3" />
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Jahresansicht -->
    <div v-if="viewMode === 'jahr'" class="bg-white border border-outline-gray-2 rounded-lg overflow-hidden mb-8">
      <div class="px-4 py-3 border-b border-outline-gray-1">
        <h3 class="font-medium text-ink-gray-8">Jahresübersicht {{ selectedJahr }}</h3>
      </div>
      <div v-if="!jahresData.length" class="text-center py-8 text-ink-gray-4">Lade...</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="bg-surface-gray-1">
            <tr>
              <th class="text-left py-2 px-3 font-medium text-ink-gray-5 sticky left-0 bg-surface-gray-1">Kategorie</th>
              <th v-for="m in jahresData" :key="m.monat" class="text-right py-2 px-3 font-medium text-ink-gray-5 whitespace-nowrap">
                {{ ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'][m.monat-1] }}
              </th>
              <th class="text-right py-2 px-3 font-medium text-ink-gray-8 whitespace-nowrap">Gesamt</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="kat in jahresKategorien"
              :key="kat"
              class="border-t border-outline-gray-1 hover:bg-surface-gray-1"
            >
              <td class="py-2 px-3 font-medium text-ink-gray-7 sticky left-0 bg-white">{{ kat }}</td>
              <td
                v-for="m in jahresData"
                :key="m.monat"
                class="py-2 px-3 text-right"
                :class="(m.kategorien.find(k => k.kategorie === kat)?.ueberschritten) ? 'text-ink-red-4 font-medium' : 'text-ink-gray-6'"
              >
                {{ formatCurrency(m.kategorien.find(k => k.kategorie === kat)?.ist || 0) }}
              </td>
              <td class="py-2 px-3 text-right font-semibold text-ink-gray-8">
                {{ formatCurrency(jahresData.reduce((sum, m) => sum + (m.kategorien.find(k => k.kategorie === kat)?.ist || 0), 0)) }}
              </td>
            </tr>
            <!-- Gesamt-Zeile -->
            <tr class="border-t-2 border-outline-gray-3 bg-surface-gray-1 font-semibold">
              <td class="py-2 px-3 text-ink-gray-8 sticky left-0 bg-surface-gray-1">Gesamt</td>
              <td
                v-for="m in jahresData"
                :key="m.monat"
                class="py-2 px-3 text-right text-ink-gray-8"
              >
                {{ formatCurrency(m.kategorien.reduce((sum, k) => sum + (k.ist || 0), 0)) }}
              </td>
              <td class="py-2 px-3 text-right text-ink-gray-9">
                {{ formatCurrency(jahresData.reduce((sum, m) => sum + m.kategorien.reduce((s, k) => s + (k.ist || 0), 0), 0)) }}
              </td>
            </tr>
          </tbody>
        </table>
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
const editableBudgets = ref([])
let _keyCounter = 0
const expandedKat = ref(null)
const buchungenByKat = ref({})

const viewMode = ref('monat')
const jahresData = ref([])
const jahresKategorien = computed(() => {
  if (!jahresData.value.length) return []
  const seen = new Set()
  for (const m of jahresData.value) {
    for (const k of m.kategorien) seen.add(k.kategorie)
  }
  return [...seen]
})

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

async function loadJahresData() {
  const monate = []
  for (let m = 1; m <= 12; m++) {
    const res = await call('ktesis.api.dashboard.get_budget_vs_ist', {
      monat: m,
      jahr: selectedJahr.value,
    })
    monate.push({ monat: m, kategorien: res.kategorien || [] })
  }
  jahresData.value = monate
}

async function loadBudgetForm() {
  loadingBudgets.value = true
  try {
    const all = await list('Budgetposten', { fields: ['name', 'kategorie', 'betrag_monatlich', 'notiz'], limit: 100 })
    editableBudgets.value = (all || []).map(b => ({ ...b, _key: b.name, _saving: false, _deleting: false }))
  } finally {
    loadingBudgets.value = false
  }
}

function addNewBudgettopf() {
  editableBudgets.value.push({
    name: null,
    kategorie: '',
    betrag_monatlich: 0,
    notiz: '',
    _key: '__new__' + (++_keyCounter),
    _saving: false,
    _deleting: false,
  })
}

async function saveBudgettopf(b) {
  if (!b.kategorie?.trim()) return
  b._saving = true
  try {
    if (b.name) {
      await update('Budgetposten', b.name, {
        kategorie: b.kategorie.trim(),
        betrag_monatlich: b.betrag_monatlich || 0,
        notiz: b.notiz || '',
      })
    } else {
      const created = await create('Budgetposten', {
        kategorie: b.kategorie.trim(),
        betrag_monatlich: b.betrag_monatlich || 0,
        notiz: b.notiz || '',
      })
      b.name = created.name
      b._key = created.name
    }
    await loadData()
  } finally {
    b._saving = false
  }
}

async function deleteBudgettopf(b, i) {
  if (!window.confirm(`"${b.kategorie || 'Neuer Eintrag'}" wirklich löschen?`)) return
  if (!b.name) {
    editableBudgets.value.splice(i, 1)
    return
  }
  b._deleting = true
  try {
    await delete_('Budgetposten', b.name)
    editableBudgets.value.splice(i, 1)
    await loadData()
  } finally {
    b._deleting = false
  }
}

async function toggleKat(kat) {
  if (expandedKat.value === kat) {
    expandedKat.value = null
    return
  }
  expandedKat.value = kat
  if (buchungenByKat.value[kat]) return
  // Lade Buchungen für diese Kategorie im aktuellen Monat
  const datum_von = `${selectedJahr.value}-${String(selectedMonat.value).padStart(2,'0')}-01`
  const nextM = selectedMonat.value === 12 ? 1 : selectedMonat.value + 1
  const nextY = selectedMonat.value === 12 ? selectedJahr.value + 1 : selectedJahr.value
  const datum_bis = `${nextY}-${String(nextM).padStart(2,'0')}-01`
  const rows = await list('Bankbuchung', {
    filters: [
      ['datum', '>=', datum_von],
      ['datum', '<', datum_bis],
      ['kategorie', '=', 'Ausgang'],
      ['buchungskategorie', '=', kat],
    ],
    fields: ['name', 'datum', 'buchungstext', 'betrag', 'budgetposten'],
    limit: 50,
    orderBy: 'datum desc',
  })
  buchungenByKat.value[kat] = rows || []
}

function formatDate(val) {
  if (!val) return '—'
  return new Date(val).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatCurrency(value) {
  if (value == null) return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

watch([selectedMonat, selectedJahr], loadData)
watch(showBudgetForm, (v) => { if (v) loadBudgetForm() })

watch(viewMode, (v) => {
  if (v === 'jahr') loadJahresData()
})
watch(selectedJahr, () => {
  if (viewMode.value === 'jahr') loadJahresData()
})

onMounted(loadData)
</script>
