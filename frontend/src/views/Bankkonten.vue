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

      <!-- Karten-Liste -->
      <div v-else class="grid gap-4">
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
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-blue-4 hover:bg-surface-blue-1 transition-all md:opacity-0 md:group-hover:opacity-100"
                title="Kontoauszug importieren"
              >
                <FeatherIcon name="upload" class="w-4 h-4" />
              </button>
              <button
                @click.stop="openDetail(item.name)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-gray-7 hover:bg-surface-gray-2 transition-all md:opacity-0 md:group-hover:opacity-100"
                title="Bearbeiten"
              >
                <FeatherIcon name="edit-2" class="w-4 h-4" />
              </button>
              <button
                @click.stop="confirmDelete(item)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-red-4 hover:bg-surface-red-1 transition-all md:opacity-0 md:group-hover:opacity-100"
                title="Löschen"
              >
                <FeatherIcon name="trash-2" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Buchungsliste -->
      <div class="mt-8">
        <h3 class="text-lg font-semibold text-ink-gray-9 mb-4 flex items-center gap-2">
          <FeatherIcon name="list" class="w-4 h-4 text-ink-gray-5" />
          Buchungen
        </h3>
        <div v-if="buchungenLoading" class="text-center py-8 text-ink-gray-4">Lade Buchungen...</div>
        <div v-else-if="buchungen.length === 0" class="text-center py-8 text-ink-gray-4">
          Keine Buchungen vorhanden.
        </div>
        <div v-else class="bg-white border border-outline-gray-2 rounded-lg shadow-sm overflow-hidden">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="border-b border-outline-gray-2">
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Datum</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Konto</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Buchungstext</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Betrag</th>
                <th class="text-center py-3 px-4 font-medium text-ink-gray-5">Typ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in buchungen" :key="b.name" class="border-b border-outline-gray-1 hover:bg-surface-gray-2">
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
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Detail-Modus / Neuanlage-Modus -->
    <template v-else>
      <Button variant="outline" theme="gray" @click="backToList">
        <FeatherIcon name="arrow-left" class="w-4 h-4" />
        Zurück
      </Button>
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
      <template #body>
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
      <template #body>
        <p class="text-sm text-ink-gray-6">
          Sind Sie sicher, dass Sie <strong>{{ itemToDelete?.bezeichnung }}</strong> löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
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

const { list, delete_, call } = useApi()

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
    const res = await call('ktesis.api.bankkonto.get_buchungen', { limit: 50 })
    buchungen.value = res || []
  } catch (e) {
    buchungen.value = []
  } finally {
    buchungenLoading.value = false
  }
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

onMounted(() => {
  loadList()
  loadBuchungen()
})
</script>
