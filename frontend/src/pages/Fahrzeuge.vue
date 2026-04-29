<template>
  <div class="kt-screen kt-screen-enter">
    <!-- Listen-Modus -->
    <template v-if="!selectedName">
      <!-- Header with toolbar -->
      <div class="kt-screen-header">
        <div>
          <h1 class="kt-hub-greeting">Fahrzeuge</h1>
          <p class="kt-hub-sub">Verwaltung des Fahrzeugbestands</p>
        </div>
        <div class="kt-screen-actions">
          <button class="kt-btn kt-btn-primary" @click="openNew">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Neu erstellen
          </button>
        </div>
      </div>

      <!-- Filter / Suche -->
      <div class="kt-toolbar">
        <div class="kt-toolbar-left">
          <div class="kt-search-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="search" type="text" placeholder="Suchen..." class="kt-search-input" />
          </div>
          <select v-model="filterStatus" class="kt-select">
            <option value="">Alle Status</option>
            <option value="Aktiv">Aktiv</option>
            <option value="Verkauft">Verkauft</option>
            <option value="Entsorgt">Entsorgt</option>
          </select>
        </div>
      </div>

      <!-- Ladezustand -->
      <div v-if="loading" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Lade Fahrzeuge…</p>
      </div>

      <!-- Leere Liste -->
      <div v-else-if="filteredList.length === 0" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Keine Fahrzeuge gefunden.</p>
      </div>

      <!-- Karten-Liste -->
      <div v-else class="kt-list">
        <div
          v-for="item in filteredList"
          :key="item.name"
          @click="openDetail(item.name)"
          class="kt-list-item"
        >
          <div class="kt-list-item-body">
            <div class="kt-list-item-title">{{ item.kennzeichen || '—' }}</div>
            <div class="kt-list-item-sub">{{ item.marke || '—' }} {{ item.modell || '—' }}</div>
          </div>
          <span class="kt-badge" :class="statusBadgeClass(item.status)">{{ item.status || '—' }}</span>
        </div>
      </div>
    </template>

    <!-- Detail-Modus -->
    <template v-else>
      <button class="kt-btn kt-btn-ghost kt-btn-sm" style="margin-bottom:16px" @click="backToList">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Zurück zur Liste
      </button>
      <FahrzeugDetail
        :name="isNew ? null : selectedName"
        @close="backToList"
        @saved="onSaved"
      />
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import FahrzeugDetail from '../components/FahrzeugDetail.vue'

const { list } = useApi()

const listData = ref([])
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')
const filterStatus = ref('')

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
    if (filterStatus.value && item.status !== filterStatus.value) return false
    if (search.value) {
      const s = search.value.toLowerCase()
      const kennzeichen = (item.kennzeichen || '').toLowerCase()
      const marke = (item.marke || '').toLowerCase()
      const modell = (item.modell || '').toLowerCase()
      if (!kennzeichen.includes(s) && !marke.includes(s) && !modell.includes(s)) return false
    }
    return true
  })
})

function statusBadgeClass(status) {
  switch (status) {
    case 'Aktiv': return 'kt-badge-success'
    case 'Verkauft': return 'kt-badge-warning'
    case 'Entsorgt': return 'kt-badge-danger'
    default: return 'kt-badge-neutral'
  }
}

function openDetail(name) { isNew.value = false; selectedName.value = name }
function openNew() { isNew.value = true; selectedName.value = 'new' }
function backToList() { selectedName.value = null; isNew.value = false }
function onSaved() { loadList(); backToList() }

onMounted(loadList)
</script>
