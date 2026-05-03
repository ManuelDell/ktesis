<template>
  <div class="px-3 sm:px-5 py-5">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Top-Bereich -->
      <div class="flex items-center justify-between gap-4 mb-6">
        <h2 class="text-3xl font-semibold text-ink-gray-9 truncate">Fahrzeuge</h2>
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
        <Select v-model="filterStatus" class=""
        >
          <option value="">Alle Status</option>
          <option value="Aktiv">Aktiv</option>
          <option value="Verkauft">Verkauft</option>
          <option value="Entsorgt">Entsorgt</option>
        </Select>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="text-center py-12 text-[var(--ink-gray-4)]">
        Lade Fahrzeuge...
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="text-center py-12 text-[var(--ink-gray-4)]">
        Keine Fahrzeuge gefunden.
      </div>

      <!-- Karten-Liste -->
      <div v-else class="grid gap-4">
        <div
          v-for="item in filteredList"
          :key="item.name"
          class="bg-surface-white border border-[var(--outline-gray-2)] rounded-lg p-4 cursor-pointer transition-all sm:hover:border-outline-gray-4 sm:hover:shadow-sm active:border-outline-gray-4 active:shadow-sm group"
        >
          <div class="flex items-start justify-between">
            <div @click="openDetail(item.name)" class="flex-1 min-w-0">
              <div class="font-semibold text-lg text-gray-800">{{ item.kennzeichen || '—' }}</div>
              <div class="text-sm text-gray-600 mt-1">
                {{ item.marke || '—' }} {{ item.modell || '—' }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="statusClass(item.status)"
              >
                {{ item.status || '—' }}
              </span>
              <button
                @click.stop="openDetail(item.name)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-gray-7 sm:hover:bg-surface-gray-2 active:bg-surface-gray-2 transition-all "
                title="Bearbeiten"
              >
                <FeatherIcon name="edit-2" class="w-4 h-4" />
              </button>
              <button
                @click.stop="confirmDelete(item)"
                class="p-1.5 rounded-lg text-ink-gray-4 hover:text-ink-red-4 sm:hover:bg-surface-red-1 active:bg-surface-red-1 transition-all "
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
      <FahrzeugDetail
        :name="isNew ? null : selectedName"
        @close="backToList"
        @saved="onSaved"
      />
    </template>

    <!-- Create Dialog -->
    <Dialog
      :options="{ title: 'Fahrzeug anlegen', size: 'xl' }"
      v-model="showCreateDialog"
    >
      <template #body>
        <FahrzeugDetail
          modal
          :name="null"
          @saved="onCreateSaved"
          @close="showCreateDialog = false"
        />
      </template>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog
      :options="{ title: 'Fahrzeug löschen', size: 'sm', actions: [
        { label: 'Abbrechen', variant: 'outline', theme: 'gray', onClick: () => showDeleteDialog = false },
        { label: 'Löschen', variant: 'solid', theme: 'red', onClick: doDelete }
      ]}"
      v-model="showDeleteDialog"
    >
      <template #body>
        <p class="text-sm text-ink-gray-6">
          Sind Sie sicher, dass Sie <strong>{{ itemToDelete?.kennzeichen }}</strong> löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'
import FahrzeugDetail from '../components/FahrzeugDetail.vue'

const { list, delete_ } = useApi()

const listData = ref([])
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')
const filterStatus = ref('')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const itemToDelete = ref(null)

async function loadList() {
  loading.value = true
  try {
    const res = await list('Fahrzeug')
    listData.value = res || []
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    // Status-Filter
    if (filterStatus.value && item.status !== filterStatus.value) {
      return false
    }
    // Such-Filter
    if (search.value) {
      const s = search.value.toLowerCase()
      const kennzeichen = (item.kennzeichen || '').toLowerCase()
      const marke = (item.marke || '').toLowerCase()
      const modell = (item.modell || '').toLowerCase()
      if (
        !kennzeichen.includes(s) &&
        !marke.includes(s) &&
        !modell.includes(s)
      ) {
        return false
      }
    }
    return true
  })
})

function statusClass(status) {
  switch (status) {
    case 'Aktiv':
      return 'text-ink-green-3 bg-surface-green-2'
    case 'Verkauft':
      return 'text-ink-amber-3 bg-surface-amber-1'
    case 'Entsorgt':
      return 'text-ink-red-4 bg-surface-red-2'
    default:
      return 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-surface-gray-1 text-ink-gray-7 border border-[var(--outline-gray-2)]'
  }
}

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
    await delete_('Fahrzeug', itemToDelete.value.name)
    showDeleteDialog.value = false
    itemToDelete.value = null
    loadList()
  } catch (e) {
    alert('Fehler beim Löschen: ' + (e.message || 'Unbekannter Fehler'))
  }
}

onMounted(loadList)
</script>
