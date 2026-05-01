<template>
  <div class="p-5">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Top-Bereich -->
      <div class="flex items-center justify-between gap-4 mb-6">
        <h2 class="text-3xl font-semibold text-ink-gray-9 truncate">Wohnungen</h2>
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
          <Input
            v-model="search"
            type="text"
            placeholder="Suchen..." class="pl-10"
           />
        </div>
        <Select v-model="filterStatus">
          <option value="">Alle Status</option>
          <option value="Bewohnt">Bewohnt</option>
          <option value="Vermietet">Vermietet</option>
          <option value="Leerstehend">Leerstehend</option>
          <option value="Verkauft">Verkauft</option>
        </Select>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="text-center py-12 text-[var(--ink-gray-4)]">
        Lade Wohnungen...
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="text-center py-12 text-[var(--ink-gray-4)]">
        Keine Wohnungen gefunden.
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
                {{ item.ort || '—' }} · {{ item.wohnflaeche ? item.wohnflaeche + ' m²' : '—' }}
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap"
                :class="statusClass(item.status)"
              >
                {{ item.status || '—' }}
              </span>
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
      <Button variant="outline" theme="gray" @click="backToList">
        <FeatherIcon name="arrow-left" class="w-4 h-4" />
        Zurück
      </Button>
      <WohnungDetail
        :name="isNew ? null : selectedName"
        @close="backToList"
        @saved="onSaved"
      />
    </template>

    <!-- Create Dialog -->
    <Dialog
      :options="{ title: 'Wohnung anlegen', size: 'xl' }"
      v-model="showCreateDialog"
    >
      <template #body>
        <WohnungDetail
          modal
          :name="null"
          @saved="onCreateSaved"
          @close="showCreateDialog = false"
        />
      </template>
    </Dialog>

    <!-- Delete Dialog -->
    <Dialog
      :options="{ title: 'Wohnung löschen', size: 'sm', actions: [
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'
import WohnungDetail from '../components/WohnungDetail.vue'

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
    const res = await list('Wohnung')
    listData.value = res || []
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (filterStatus.value && item.status !== filterStatus.value) {
      return false
    }
    if (search.value) {
      const s = search.value.toLowerCase()
      const bezeichnung = (item.bezeichnung || '').toLowerCase()
      const ort = (item.ort || '').toLowerCase()
      if (!bezeichnung.includes(s) && !ort.includes(s)) {
        return false
      }
    }
    return true
  })
})

function statusClass(status) {
  switch (status) {
    case 'Aktiv':
    case 'Vermietet':
      return 'text-ink-green-3 bg-surface-green-2'
    case 'Inaktiv':
      return 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-surface-gray-1 text-ink-gray-7 border border-[var(--outline-gray-2)]'
    case 'Leerstehend':
      return 'text-ink-amber-3 bg-surface-amber-1'
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
    await delete_('Wohnung', itemToDelete.value.name)
    showDeleteDialog.value = false
    itemToDelete.value = null
    loadList()
  } catch (e) {
    alert('Fehler beim Löschen: ' + (e.message || 'Unbekannter Fehler'))
  }
}

onMounted(loadList)
</script>
