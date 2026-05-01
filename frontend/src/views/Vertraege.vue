<template>
  <div class="kt-screen kt-screen-enter">
    <template v-if="!selectedName">
      <div class="kt-screen-header">
        <div>
          <h1 class="kt-hub-greeting">Verträge</h1>
          <p class="kt-hub-sub">Vertragsverwaltung und Übersicht</p>
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
          <select v-model="filterTyp" class="kt-select">
            <option value="">Alle Typen</option>
            <option value="Mietvertrag">Mietvertrag</option>
            <option value="Versicherung">Versicherung</option>
            <option value="Wartung">Wartung</option>
            <option value="Sonstiges">Sonstiges</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Lade Verträge…</p>
      </div>

      <div v-else-if="filteredList.length === 0" class="kt-list-empty" style="padding:60px 22px">
        <p style="margin:0;font-size:13px;color:var(--kt-text-muted)">Keine Verträge gefunden.</p>
      </div>

      <div v-else class="kt-list">
        <div
          v-for="item in filteredList"
          :key="item.name"
          @click="openDetail(item.name)"
          class="kt-list-item"
        >
          <div class="kt-list-item-body">
            <div class="kt-list-item-title">
              <span class="kt-ampel-dot" :class="'dot-' + (ampelMap[item.name]?.ampel || 'gruen')"></span>
              {{ item.titel || '—' }}
            </div>
            <div class="kt-list-item-sub">{{ item.vertragstyp || '—' }} · {{ item.vertragspartner || item.partner || '—' }}<span v-if="ampelMap[item.name]?.naechste_kuendigungsfrist" style="margin-left:8px;color:var(--kt-text-muted)">· Frist: {{ ampelMap[item.name].naechste_kuendigungsfrist }}</span></div>
          </div>
          <span class="kt-badge" :class="item.aktiv ? 'kt-badge-success' : 'kt-badge-neutral'">{{ item.aktiv ? 'Aktiv' : 'Inaktiv' }}</span>
        </div>
      </div>
    </template>

    <template v-else>
      <button class="kt-btn kt-btn-ghost kt-btn-sm" style="margin-bottom:16px" @click="backToList">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        Zurück zur Liste
      </button>
      <VertragDetail
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
import VertragDetail from '../components/VertragDetail.vue'

const { list, call } = useApi()

const listData = ref([])
const ampelMap = ref({})
const loading = ref(false)
const selectedName = ref(null)
const isNew = ref(false)
const search = ref('')
const filterTyp = ref('')

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

const filteredList = computed(() => {
  return listData.value.filter((item) => {
    if (filterTyp.value && item.vertragstyp !== filterTyp.value) return false
    if (search.value) {
      const s = search.value.toLowerCase()
      const titel = (item.titel || '').toLowerCase()
      const partner = (item.vertragspartner || item.partner || '').toLowerCase()
      if (!titel.includes(s) && !partner.includes(s)) return false
    }
    return true
  })
})

function openDetail(name) { isNew.value = false; selectedName.value = name }
function openNew() { isNew.value = true; selectedName.value = 'new' }
function backToList() { selectedName.value = null; isNew.value = false }
function onSaved() { loadList(); backToList() }

onMounted(loadList)
</script>

<style scoped>
.kt-ampel-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-rot { background: #ef4444; }
.dot-gelb { background: #f59e0b; }
.dot-gruen { background: #10b981; }
.dot-abgelaufen { background: #9ca3af; }
</style>
