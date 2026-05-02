<template>
  <div class="p-5">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Top-Bereich -->
      <div class="flex items-center justify-between gap-4 mb-6">
        <h2 class="text-3xl font-semibold text-ink-gray-9 truncate">Verträge</h2>
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
        <select v-model="filterTyp"
          class="h-9 px-3 rounded-lg border border-outline-gray-2 bg-surface-white text-sm text-ink-gray-7 focus:outline-none focus:border-outline-gray-4"
        >
          <option value="">Alle Typen</option>
          <option value="Mietvertrag">Mietvertrag</option>
          <option value="Versicherung">Versicherung</option>
          <option value="Wartung">Wartung</option>
          <option value="Sonstiges">Sonstiges</option>
        </select>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="text-center py-12 text-ink-gray-4">
        Lade Verträge...
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="text-center py-12 text-ink-gray-4">
        Keine Verträge gefunden.
      </div>

      <!-- Karten-Liste -->
      <div v-else class="grid gap-4">
        <div
          v-for="item in filteredList"
          :key="item.name"
          class="bg-surface-white border border-outline-gray-2 rounded-lg p-4 cursor-pointer transition-all hover:border-outline-gray-4 hover:shadow-sm group"
        >
          <div class="flex items-start justify-between">
            <div @click="openDetail(item.name)" class="flex-1 min-w-0">
              <div class="font-semibold text-lg text-gray-800 flex items-center gap-2">
                <span
                  class="inline-block w-2.5 h-2.5 rounded-full"
                  :class="{
                    'bg-red-500': ampelMap[item.name]?.ampel === 'rot',
                    'bg-yellow-500': ampelMap[item.name]?.ampel === 'gelb',
                    'bg-green-500': ampelMap[item.name]?.ampel === 'gruen' || !ampelMap[item.name]?.ampel,
                    'bg-gray-400': ampelMap[item.name]?.ampel === 'abgelaufen',
                  }"
                />
                {{ item.titel || '—' }}
              </div>
              <div class="text-sm text-gray-600 mt-1">
                {{ item.vertragstyp || '—' }} · {{ item.vertragspartner || '—' }}
              </div>
              <div class="mt-2 text-sm">
                <span class="text-gray-500">Kosten monatlich:</span>
                <span class="ml-1 font-medium">{{ formatCurrency(item.kosten_monatlich) }}</span>
                <span v-if="ampelMap[item.name]?.naechste_kuendigungsfrist" class="ml-3 text-xs text-ink-gray-5">
                  Frist: {{ ampelMap[item.name].naechste_kuendigungsfrist }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <Badge
                :theme="item.aktiv ? 'green' : 'gray'"
                variant="subtle"
                size="sm"
              >
                {{ item.aktiv ? 'Aktiv' : 'Inaktiv' }}
              </Badge>
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
    </template>

    <!-- Detail-Modus / Neuanlage-Modus -->
    <template v-else>
      <Button variant="outline" theme="gray" size="md" @click="backToList">
        <span class="flex items-center gap-2 whitespace-nowrap">
          <FeatherIcon name="arrow-left" class="w-4 h-4" />
          Zurück
        </span>
      </Button>
      <VertragDetail
        :name="isNew ? null : selectedName"
        @close="backToList"
        @saved="onSaved"
      />
    </template>

    <!-- Create Dialog -->
    <Dialog
      :options="{ title: 'Vertrag anlegen', size: 'xl' }"
      v-model="showCreateDialog"
    >
      <template #body>
        <VertragDetail
          modal
          :name="null"
          @saved="onCreateSaved"
          @close="showCreateDialog = false"
        />
      </template>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog
      :options="{ title: 'Vertrag löschen', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showDeleteDialog = false },
        { label: 'Löschen', variant: 'solid', theme: 'red', onClick: doDelete }
      ]}"
      v-model="showDeleteDialog"
    >
      <template #body>
        <p class="text-sm text-ink-gray-6">
          Sind Sie sicher, dass Sie <strong>{{ itemToDelete?.titel }}</strong> löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'
import VertragDetail from '../components/VertragDetail.vue'

const { list, call, delete_ } = useApi()

const listData = ref([])
const ampelMap = ref({})
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')
const filterTyp = ref('')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const itemToDelete = ref(null)

async function loadList() {
  loading.value = true
  try {
    const [res, ampelRes] = await Promise.all([
      list('Vertrag'),
      call('ktesis.api.dashboard.get_vertraege_mit_fristen'),
    ])
    listData.value = res || []
    ampelMap.value = {}
    for (const v of (ampelRes || [])) {
      ampelMap.value[v.name] = v
    }
  } finally {
    loading.value = false
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

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (filterTyp.value && item.vertragstyp !== filterTyp.value) return false
    if (search.value) {
      const s = search.value.toLowerCase()
      const titel = (item.titel || '').toLowerCase()
      const partner = (item.vertragspartner || '').toLowerCase()
      if (!titel.includes(s) && !partner.includes(s)) return false
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
    await delete_('Vertrag', itemToDelete.value.name)
    showDeleteDialog.value = false
    itemToDelete.value = null
    loadList()
  } catch (e) {
    alert('Fehler beim Löschen: ' + (e.message || 'Unbekannter Fehler'))
  }
}

onMounted(loadList)
</script>
