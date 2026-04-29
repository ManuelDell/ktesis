<template>
  <div class="p-5">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Top-Bereich -->
      <div class="flex items-center justify-between gap-4 mb-6">
        <h2 class="text-3xl font-semibold text-ink-gray-9 truncate">Verträge</h2>
        <Button @click="openCreateDialog"
          variant="solid" theme="gray"
        >
          <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
          Neu
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
        <Select v-model="filterTyp" class=""
        >
          <option value="">Alle Typen</option>
          <option value="Miete">Miete</option>
          <option value="Versicherung">Versicherung</option>
          <option value="Wartung">Wartung</option>
          <option value="Sonstiges">Sonstiges</option>
        </Select>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="text-center py-12 text-[var(--ink-gray-4)]">
        Lade Verträge...
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="text-center py-12 text-[var(--ink-gray-4)]">
        Keine Verträge gefunden.
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
              <div class="font-semibold text-lg text-gray-800">{{ item.titel || '—' }}</div>
              <div class="text-sm text-gray-600 mt-1">
                {{ item.vertragstyp || '—' }}
                <span v-if="item.vertragspartner" class="ml-2">· {{ item.vertragspartner }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <!-- Aktiv-Status (grün/rot) -->
              <span
                class="px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap"
                :class="item.aktiv ? 'text-ink-green-3 bg-surface-green-2' : 'text-ink-red-4 bg-surface-red-2'"
              >
                {{ item.aktiv ? 'Aktiv' : 'Inaktiv' }}
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

const { list, delete_ } = useApi()

const listData = ref([])
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
    const res = await list('Vertrag')
    listData.value = res || []
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (filterTyp.value && item.vertragstyp !== filterTyp.value) {
      return false
    }
    if (search.value) {
      const s = search.value.toLowerCase()
      const titel = (item.titel || '').toLowerCase()
      const partner = (item.vertragspartner || '').toLowerCase()
      if (!titel.includes(s) && !partner.includes(s)) {
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
