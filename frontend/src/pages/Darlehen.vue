<template>
  <div class="kt-screen kt-screen-enter">
    <template v-if="!selectedName">
      <div class="kt-screen-header">
        <div>
          <h1 class="kt-hub-greeting">Darlehen</h1>
          <p class="kt-hub-sub">Verwaltung von Darlehen und Verbindlichkeiten</p>
        </div>
        <div class="kt-screen-actions">
          <button class="kt-btn kt-btn-primary" @click="openNew">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Neu erstellen
          </button>
        </div>
      </div>

      <div class="kt-toolbar">
        <div class="kt-toolbar-left">
          <div class="kt-search-wrap">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="search" type="text" placeholder="Suchen..." class="kt-search-input" />
          </div>
        </div>
      </div>

      <div v-if="loading" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Lade Darlehen…</p>
      </div>

      <div v-else-if="filteredList.length === 0" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Keine Darlehen gefunden.</p>
      </div>

      <div v-else class="kt-list">
        <div
          v-for="item in filteredList"
          :key="item.name"
          @click="openDetail(item.name)"
          class="kt-list-item"
        >
          <div class="kt-list-item-body">
            <div class="kt-list-item-title">{{ item.bezeichnung || '—' }}</div>
            <div class="kt-list-item-sub">{{ item.darlehensgeber || '—' }}</div>
            <div class="kt-list-item-meta">
              <span>Darlehen: {{ formatCurrency(item.darlehensbetrag) }}</span>
              <span>Restschuld: {{ formatCurrency(item.restschuld) }}</span>
            </div>
          </div>
          <span class="kt-badge" :class="statusBadgeClass(item.status)">{{ item.status || '—' }}</span>
        </div>
      </div>
    </template>

    <template v-else>
      <button class="kt-btn kt-btn-ghost kt-btn-sm" style="margin-bottom:16px" @click="backToList">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Zurück zur Liste
      </button>
      <DarlehenDetail
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
import DarlehenDetail from '../components/DarlehenDetail.vue'

const { list } = useApi()

const listData = ref([])
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')

async function loadList() {
  loading.value = true
  try {
    const res = await list('Darlehen')
    listData.value = res || []
  } finally {
    loading.value = false
  }
}

function formatCurrency(value) {
  if (value == null || value === '') return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 }).format(value)
}

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (search.value) {
      const s = search.value.toLowerCase()
      const bezeichnung = (item.bezeichnung || '').toLowerCase()
      const darlehensgeber = (item.darlehensgeber || '').toLowerCase()
      if (!bezeichnung.includes(s) && !darlehensgeber.includes(s)) return false
    }
    return true
  })
})

function statusBadgeClass(status) {
  switch (status) {
    case 'Aktiv': return 'kt-badge-success'
    case 'Abbezahlt': return 'kt-badge-info'
    case 'Gekündigt': return 'kt-badge-danger'
    default: return 'kt-badge-neutral'
  }
}

function openDetail(name) { isNew.value = false; selectedName.value = name }
function openNew() { isNew.value = true; selectedName.value = 'new' }
function backToList() { selectedName.value = null; isNew.value = false }
function onSaved() { loadList(); backToList() }

onMounted(loadList)
</script>
