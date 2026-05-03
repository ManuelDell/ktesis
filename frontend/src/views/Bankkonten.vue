<template>
  <div class="p-5">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Top-Bereich -->
      <div class="flex items-center justify-between gap-4 mb-6">
        <h2 class="text-3xl font-semibold text-ink-gray-9 truncate">Bankkonten</h2>
        <Button size="md" @click="openCreateDialog"
          variant="solid" theme="gray"
        >
          <span class="flex items-center gap-2 whitespace-nowrap">
            <FeatherIcon name="plus" class="w-4 h-4" />
            Neu
          </span>
        </Button>
      </div>

      <!-- Filter -->
      <div class="flex items-center gap-4 mb-4">
        <div class="relative w-64">
          <FeatherIcon name="search" class="w-4 h-4 text-ink-gray-4 absolute left-3 top-1/2 -translate-y-1/2" />
          <Input v-model="search"
            type="text"
            placeholder="Suchen..." class="pl-10"
           />
        </div>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="text-center py-12 text-[var(--ink-gray-4)]">
        Lade Bankkonten...
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="text-center py-12 text-[var(--ink-gray-4)]">
        Keine Bankkonten gefunden.
      </div>

      <!-- Konten ein-/ausblenden -->
      <template v-else>
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-ink-gray-5">{{ filteredList.length }} Konten</span>
        <button @click="kontenVisible = !kontenVisible" class="flex items-center gap-1 text-xs text-ink-gray-5 hover:text-ink-gray-8 transition-colors">
          <FeatherIcon :name="kontenVisible ? 'chevron-up' : 'chevron-down'" class="w-4 h-4" />
          {{ kontenVisible ? 'Ausblenden' : 'Einblenden' }}
        </button>
      </div>

      <!-- Karten-Liste -->
      <div class="grid gap-4" v-show="kontenVisible">
        <div
          v-for="item in filteredList"
          :key="item.name"
          class="bg-surface-white border border-[var(--outline-gray-2)] rounded-lg p-4 cursor-pointer transition-all hover:border-outline-gray-4 hover:shadow-sm group"
        >
          <div class="flex items-start justify-between">
            <div @click="openDetail(item.name)" class="flex-1 min-w-0">
              <div class="font-semibold text-lg text-gray-800">{{ item.bezeichnung || '—' }}</div>
              <div class="text-sm text-gray-600 mt-1">
                {{ item.bank || '—' }} · {{ item.kontotyp || '—' }}
              </div>
              <div class="mt-2 text-sm">
                <span class="text-gray-500">Kontostand:</span>
                <span class="ml-1 font-medium">
                  {{ formatCurrency(item.kontostand_live ?? item.kontostand_manuell) }}
                </span>
                <span v-if="item.kontostand_live != null" class="ml-1 text-xs text-green-600" title="Live-Kontostand via FinTS">●</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click.stop="openImport(item)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-blue-4 hover:bg-surface-blue-1 transition-all "
                title="Kontoauszug importieren"
              >
                <FeatherIcon name="upload" class="w-4 h-4" />
              </button>
              <button
                @click.stop="openDetail(item.name)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-gray-7 hover:bg-surface-gray-2 transition-all "
                title="Bearbeiten"
              >
                <FeatherIcon name="edit-2" class="w-4 h-4" />
              </button>
              <button
                @click.stop="confirmDelete(item)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-red-4 hover:bg-surface-red-1 transition-all "
                title="Löschen"
              >
                <FeatherIcon name="trash-2" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
      </template>

      <!-- Buchungsliste -->
      <div class="mt-8">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-ink-gray-9 flex items-center gap-2">
            <FeatherIcon name="list" class="w-4 h-4 text-ink-gray-5" />
            Buchungen
          </h3>
          <Button variant="outline" theme="gray" size="md" :loading="autoAssigning" @click="autoAssignBudgetposten">
            <span class="flex items-center gap-2 whitespace-nowrap">
              <FeatherIcon name="zap" class="w-4 h-4" />
              Auto-zuordnen
            </span>
          </Button>
        </div>
        <!-- Filter -->
        <div class="flex items-center gap-3 mb-3 flex-wrap">
          <label class="flex items-center gap-2 text-sm text-ink-gray-6 cursor-pointer select-none">
            <input type="checkbox" v-model="nurUnzugeordnet" @change="onFilterChange" class="rounded" />
            Nur unzugeordnete
          </label>
          <select v-model="filterBankkonto" @change="onFilterChange"
            class="border border-outline-gray-2 rounded px-3 py-1.5 text-sm bg-white">
            <option value="">Alle Konten</option>
            <option v-for="k in listData" :key="k.name" :value="k.name">{{ k.bezeichnung || k.name }}</option>
          </select>
          <span class="text-xs text-ink-gray-4">{{ totalBuchungen }} Buchungen</span>
        </div>
        <div v-if="buchungenLoading" class="text-center py-8 text-ink-gray-4">Lade Buchungen...</div>
        <div v-else-if="buchungen.length === 0" class="text-center py-8 text-ink-gray-4">
          Keine Buchungen vorhanden.
        </div>
        <!-- Bulk-Aktionen -->
        <div v-if="selectedBuchungen.size > 0" class="flex items-center gap-3 mb-3 px-1">
          <span class="text-sm text-ink-gray-6">{{ selectedBuchungen.size }} ausgewählt</span>
          <Button variant="outline" theme="red" size="sm" :loading="bulkDeleting" @click="confirmBulkDelete">
            <span class="flex items-center gap-2 whitespace-nowrap">
              <FeatherIcon name="trash-2" class="w-4 h-4" />
              Löschen
            </span>
          </Button>
          <Button variant="outline" theme="gray" size="sm" @click="openBulkKontoWechsel">
            <span class="flex items-center gap-2 whitespace-nowrap">
              <FeatherIcon name="repeat" class="w-4 h-4" />
              Konto wechseln
            </span>
          </Button>
          <button @click="selectedBuchungen = new Set()" class="text-xs text-ink-gray-4 hover:text-ink-gray-7">Auswahl aufheben</button>
        </div>
        <div v-else class="bg-white border border-outline-gray-2 rounded-lg shadow-sm overflow-hidden">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="border-b border-outline-gray-2">
                <th class="py-3 px-3 w-8">
                  <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" class="rounded" />
                </th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Datum</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Konto</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Buchungstext</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Betrag</th>
                <th class="text-center py-3 px-4 font-medium text-ink-gray-5">Typ</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Budgettopf</th>
                <th class="text-center py-3 px-4 font-medium text-ink-gray-5">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in buchungen" :key="b.name" class="border-b border-outline-gray-1 hover:bg-surface-gray-2">
                <td class="py-2 px-3">
                  <input type="checkbox" :checked="selectedBuchungen.has(b.name)" @change="toggleSelect(b.name)" class="rounded" />
                </td>
                <td class="py-3 px-4 text-sm">{{ formatDate(b.datum) }}</td>
                <td class="py-3 px-4 text-sm">{{ b.bankkonto_bezeichnung || b.bankkonto }}</td>
                <td class="py-3 px-4 text-sm">{{ b.buchungstext }}</td>
                <td class="py-3 px-4 text-sm text-right font-medium" :class="b.kategorie === 'Eingang' ? 'text-ink-green-3' : 'text-ink-red-4'">
                  {{ formatCurrency(b.betrag) }}
                </td>
                <td class="py-3 px-4 text-center">
                  <Badge :theme="b.kategorie === 'Eingang' ? 'green' : 'red'" variant="subtle" size="sm">
                    {{ b.kategorie }}
                  </Badge>
                </td>
                <td class="py-2 px-4">
                  <select
                    :value="b.budgetposten || ''"
                    @change="updateBudgetposten(b.name, $event.target.value)"
                    class="border border-outline-gray-2 rounded px-2 py-1 text-xs bg-white max-w-[130px] w-full"
                  >
                    <option value="">— kein —</option>
                    <option v-for="bp in budgetpostenList" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                  </select>
                </td>
                <td class="py-2 px-4 text-center">
                  <div class="flex items-center gap-1 justify-center">
                    <button
                      @click.stop="openKontoWechsel(b)"
                      class="p-1.5 rounded text-ink-gray-4 hover:text-ink-blue-4 hover:bg-surface-blue-1 transition-all"
                      title="Konto wechseln"
                    >
                      <FeatherIcon name="repeat" class="w-3 h-3" />
                    </button>
                    <button
                      @click.stop="confirmDeleteBuchung(b)"
                      class="p-1.5 rounded text-ink-gray-4 hover:text-ink-red-4 hover:bg-surface-red-1 transition-all"
                      title="Buchung löschen"
                    >
                      <FeatherIcon name="trash-2" class="w-3 h-3" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-outline-gray-1">
            <span class="text-xs text-ink-gray-5">
              Seite {{ currentPage }} von {{ totalPages }} &middot; {{ totalBuchungen }} Buchungen
            </span>
            <div class="flex items-center gap-1">
              <button
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage === 1"
                class="p-1.5 rounded hover:bg-surface-gray-2 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <FeatherIcon name="chevron-left" class="w-4 h-4" />
              </button>
              <span class="text-xs px-2 text-ink-gray-7">{{ currentPage }}</span>
              <button
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="p-1.5 rounded hover:bg-surface-gray-2 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <FeatherIcon name="chevron-right" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Detail-Modus / Neuanlage-Modus -->
    <template v-else>
      <div class="flex items-center gap-3 mb-4">
        <Button variant="outline" theme="gray" size="md" @click="backToList">
          <span class="flex items-center gap-2 whitespace-nowrap">
            <FeatherIcon name="arrow-left" class="w-4 h-4" />
            Zurück
          </span>
        </Button>
        <Button v-if="selectedName && !isNew" variant="outline" theme="gray" size="md" @click="openImport({ name: selectedName })">
          <span class="flex items-center gap-2 whitespace-nowrap">
            <FeatherIcon name="upload" class="w-4 h-4" />
            Buchungen importieren
          </span>
        </Button>
      </div>
      <BankkontoDetail
        :name="isNew ? null : selectedName"
        @close="backToList"
        @saved="onSaved"
      />
    </template>

    <!-- Create Dialog -->
    <Dialog
      :options="{ title: 'Bankkonto anlegen', size: 'xl' }"
      v-model="showCreateDialog"
    >
      <template #body-content>
        <BankkontoDetail
          modal
          :name="null"
          @saved="onCreateSaved"
          @close="showCreateDialog = false"
        />
      </template>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog
      :options="{ title: 'Bankkonto löschen', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showDeleteDialog = false },
        { label: 'Löschen', variant: 'solid', theme: 'red', onClick: doDelete }
      ]}"
      v-model="showDeleteDialog"
    >
      <template #body-content>
        <p class="text-sm text-ink-gray-6">
          Sind Sie sicher, dass Sie <strong>{{ itemToDelete?.bezeichnung }}</strong> löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
      </template>
    </Dialog>

    <!-- Buchung löschen Dialog -->
    <Dialog
      :options="{ title: 'Buchung löschen', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showDeleteBuchungDialog = false },
        { label: 'Löschen', variant: 'solid', theme: 'red', onClick: doDeleteBuchung }
      ]}"
      v-model="showDeleteBuchungDialog"
    >
      <template #body-content>
        <div class="px-5 py-4">
          <p class="text-sm text-ink-gray-6">
            Buchung <strong>{{ buchungToDelete?.buchungstext }}</strong> ({{ formatCurrency(buchungToDelete?.betrag) }}) wirklich löschen?
          </p>
        </div>
      </template>
    </Dialog>

    <!-- Konto wechseln Dialog -->
    <Dialog
      :options="{ title: 'Konto wechseln', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showKontoWechselDialog = false },
        { label: 'Speichern', variant: 'solid', theme: 'gray', onClick: doKontoWechsel }
      ]}"
      v-model="showKontoWechselDialog"
    >
      <template #body-content>
        <div class="px-5 py-4 space-y-3">
          <p class="text-sm text-ink-gray-6">Buchung: <strong>{{ buchungToMove?.buchungstext }}</strong></p>
          <div>
            <label class="block text-xs text-ink-gray-6 mb-1">Zielkonto</label>
            <select v-model="kontoWechselTarget" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
              <option value="">— Konto wählen —</option>
              <option v-for="k in listData" :key="k.name" :value="k.name">{{ k.bezeichnung || k.name }}</option>
            </select>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Bulk Löschen Dialog -->
    <Dialog
      :options="{ title: 'Buchungen löschen', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showBulkDeleteDialog = false },
        { label: selectedBuchungen.size + ' Buchungen löschen', variant: 'solid', theme: 'red', onClick: doBulkDelete }
      ]}"
      v-model="showBulkDeleteDialog"
    >
      <template #body-content>
        <div class="px-5 py-4">
          <p class="text-sm text-ink-gray-6">{{ selectedBuchungen.size }} Buchungen wirklich unwiderruflich löschen?</p>
        </div>
      </template>
    </Dialog>

    <!-- Bulk Konto wechseln Dialog -->
    <Dialog
      :options="{ title: 'Konto wechseln', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showBulkKontoDialog = false },
        { label: 'Speichern', variant: 'solid', theme: 'gray', onClick: doBulkKontoWechsel }
      ]}"
      v-model="showBulkKontoDialog"
    >
      <template #body-content>
        <div class="px-5 py-4">
          <p class="text-sm text-ink-gray-6 mb-3">{{ selectedBuchungen.size }} Buchungen umbuchen auf:</p>
          <select v-model="bulkKontoTarget" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
            <option value="">— Konto wählen —</option>
            <option v-for="k in listData" :key="k.name" :value="k.name">{{ k.bezeichnung || k.name }}</option>
          </select>
        </div>
      </template>
    </Dialog>

        <!-- CSV Import Dialog -->
    <CsvImportDialog
      v-if="showImportDialog"
      v-model="showImportDialog"
      :bankkonto="importBankkonto"
      :bankkontoBezeichnung="importBankkontoBezeichnung"
      @imported="onImported"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'
import BankkontoDetail from '../components/BankkontoDetail.vue'
import CsvImportDialog from '../components/CsvImportDialog.vue'

const { list, delete_, call, update } = useApi()

const listData = ref([])
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const itemToDelete = ref(null)
const showImportDialog = ref(false)
const importBankkonto = ref('')
const importBankkontoBezeichnung = ref('')
const buchungen = ref([])
const buchungenLoading = ref(false)
const budgetpostenList = ref([])
const autoAssigning = ref(false)
const showDeleteBuchungDialog = ref(false)
const buchungToDelete = ref(null)
const showKontoWechselDialog = ref(false)
const buchungToMove = ref(null)
const kontoWechselTarget = ref('')
const selectedBuchungen = ref(new Set())
const bulkDeleting = ref(false)
const showBulkDeleteDialog = ref(false)
const showBulkKontoDialog = ref(false)
const bulkKontoTarget = ref('')

// Karten einklappen
const kontenVisible = ref(true)

// Buchungs-Filter + Pagination
const filterBankkonto = ref('')
const nurUnzugeordnet = ref(false)
const currentPage = ref(1)
const pageSize = 50
const totalBuchungen = ref(0)

const allSelected = computed(() =>
  buchungen.value.length > 0 && buchungen.value.every(b => selectedBuchungen.value.has(b.name))
)

function toggleSelect(name) {
  const s = new Set(selectedBuchungen.value)
  if (s.has(name)) s.delete(name)
  else s.add(name)
  selectedBuchungen.value = s
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedBuchungen.value = new Set()
  } else {
    selectedBuchungen.value = new Set(buchungen.value.map(b => b.name))
  }
}

function confirmBulkDelete() {
  showBulkDeleteDialog.value = true
}

async function doBulkDelete() {
  bulkDeleting.value = true
  try {
    for (const name of selectedBuchungen.value) {
      await delete_('Bankbuchung', name)
    }
    selectedBuchungen.value = new Set()
    showBulkDeleteDialog.value = false
    await loadBuchungen()
  } catch (e) {
    alert('Fehler: ' + (e.message || 'Unbekannter Fehler'))
  } finally {
    bulkDeleting.value = false
  }
}

function openBulkKontoWechsel() {
  bulkKontoTarget.value = ''
  showBulkKontoDialog.value = true
}

async function doBulkKontoWechsel() {
  if (!bulkKontoTarget.value) return
  try {
    for (const name of selectedBuchungen.value) {
      await update('Bankbuchung', name, { bankkonto: bulkKontoTarget.value })
    }
    selectedBuchungen.value = new Set()
    showBulkKontoDialog.value = false
    await loadBuchungen()
  } catch (e) {
    alert('Fehler: ' + (e.message || 'Unbekannter Fehler'))
  }
}

function confirmDeleteBuchung(b) {
  buchungToDelete.value = b
  showDeleteBuchungDialog.value = true
}

async function doDeleteBuchung() {
  if (!buchungToDelete.value) return
  try {
    await delete_('Bankbuchung', buchungToDelete.value.name)
    showDeleteBuchungDialog.value = false
    buchungToDelete.value = null
    loadBuchungen()
  } catch (e) {
    alert('Fehler: ' + (e.message || 'Unbekannter Fehler'))
  }
}

function openKontoWechsel(b) {
  buchungToMove.value = b
  kontoWechselTarget.value = b.bankkonto || ''
  showKontoWechselDialog.value = true
}

async function doKontoWechsel() {
  if (!buchungToMove.value || !kontoWechselTarget.value) return
  try {
    await update('Bankbuchung', buchungToMove.value.name, { bankkonto: kontoWechselTarget.value })
    showKontoWechselDialog.value = false
    buchungToMove.value = null
    kontoWechselTarget.value = ''
    loadBuchungen()
  } catch (e) {
    alert('Fehler: ' + (e.message || 'Unbekannter Fehler'))
  }
}

async function loadList() {
  loading.value = true
  try {
    const res = await list('Bankkonto')
    listData.value = res || []
  } finally {
    loading.value = false
  }
}

async function loadBuchungen() {
  buchungenLoading.value = true
  try {
    const offset = (currentPage.value - 1) * pageSize
    const [res, count] = await Promise.all([
      call('ktesis.api.bankkonto.get_buchungen', {
        limit: pageSize,
        offset,
        nur_unzugeordnet: nurUnzugeordnet.value ? 1 : 0,
        bankkonto: filterBankkonto.value || null,
      }),
      call('ktesis.api.bankkonto.get_buchungen_count', {
        nur_unzugeordnet: nurUnzugeordnet.value ? 1 : 0,
        bankkonto: filterBankkonto.value || null,
      }),
    ])
    buchungen.value = res || []
    totalBuchungen.value = count || 0
    selectedBuchungen.value = new Set()
  } catch (e) {
    buchungen.value = []
  } finally {
    buchungenLoading.value = false
  }
}

const totalPages = computed(() => Math.ceil(totalBuchungen.value / pageSize))

function goToPage(p) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  loadBuchungen()
}

function onFilterChange() {
  currentPage.value = 1
  loadBuchungen()
}

function formatCurrency(value) {
  if (value == null || value === '') return '—'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
  }).format(value)
}

function formatDate(val) {
  if (!val) return '—'
  const d = new Date(val)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (search.value) {
      const s = search.value.toLowerCase()
      const bezeichnung = (item.bezeichnung || '').toLowerCase()
      const bank = (item.bank || '').toLowerCase()
      if (!bezeichnung.includes(s) && !bank.includes(s)) {
        return false
      }
    }
    return true
  })
})

function openDetail(name) {
  isNew.value = false
  selectedName.value = name
}

function openCreateDialog() {
  showCreateDialog.value = true
}

function onCreateSaved() {
  showCreateDialog.value = false
  loadList()
}

function backToList() {
  selectedName.value = null
  isNew.value = false
}

function onSaved() {
  loadList()
  backToList()
}

function confirmDelete(item) {
  itemToDelete.value = item
  showDeleteDialog.value = true
}

async function doDelete() {
  if (!itemToDelete.value) return
  try {
    await delete_('Bankkonto', itemToDelete.value.name)
    showDeleteDialog.value = false
    itemToDelete.value = null
    loadList()
  } catch (e) {
    alert('Fehler beim Löschen: ' + (e.message || 'Unbekannter Fehler'))
  }
}

function openImport(item) {
  importBankkonto.value = item.name
  importBankkontoBezeichnung.value = item.bezeichnung || item.name
  showImportDialog.value = true
}

function onImported() {
  loadBuchungen()
  loadList()
}

async function autoAssignBudgetposten() {
  autoAssigning.value = true
  try {
    await call('ktesis.api.ai_assign.ai_assign_budgetposten', { bankkonto: selectedName.value })
    await loadBuchungen()
  } finally {
    autoAssigning.value = false
  }
}

async function updateBudgetposten(buchungName, value) {
  const b = buchungen.value.find(x => x.name === buchungName)
  if (b) b.budgetposten = value
  await update('Bankbuchung', buchungName, { budgetposten: value || null })
}

onMounted(async () => {
  await loadList()
  budgetpostenList.value = await list('Budgetposten', { fields: ['name', 'kategorie'], limit: 50 }) || []
  loadBuchungen()
})
</script>