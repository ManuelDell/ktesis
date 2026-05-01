<template>
  <div class="vertraege-view">
    <div class="header-row">
      <h2>Vertraege</h2>
    </div>

    <div v-if="loading" class="loading">Lade Vertraege...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="vertraege-grid">
      <div v-for="v in vertraege" :key="v.name" class="vertrag-card" :class="'ampel-' + v.ampel">
        <div class="ampel-dot" :class="'dot-' + v.ampel"></div>
        <div class="vertrag-info">
          <div class="vertrag-name">{{ v.vertragspartner }}</div>
          <div class="vertrag-detail">{{ v.vertragstyp }} · {{ formatBetrag(v.kosten_monatlich) }}/Mo</div>
          <div class="vertrag-frist" v-if="v.naechste_kuendigungsfrist">
            Kuendigung bis: <strong>{{ formatDate(v.naechste_kuendigungsfrist) }}</strong>
          </div>
          <div class="vertrag-ende" v-if="v.vertragsende">Ende: {{ formatDate(v.vertragsende) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'

const { loading, error, call } = useApi()
const vertraege = ref([])

onMounted(async () => {
  vertraege.value = await call('ktesis.api.dashboard.get_vertraege_mit_fristen')
})

function formatBetrag(v) {
  if (!v) return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(v)
}

function formatDate(d) {
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}.${m}.${y}`
}
</script>

<style scoped>
.vertraege-view { padding: 1.5rem; }
.header-row { display: flex; justify-content: space-between; margin-bottom: 1.5rem; }
h2 { font-size: 1.4rem; font-weight: 600; }
.vertraege-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.vertrag-card { display: flex; gap: 1rem; padding: 1rem; border-radius: 8px; background: var(--card-bg, #fff); border: 1px solid #e5e7eb; }
.ampel-rot { border-left: 4px solid #ef4444; }
.ampel-gelb { border-left: 4px solid #f59e0b; }
.ampel-gruen { border-left: 4px solid #10b981; }
.ampel-abgelaufen { border-left: 4px solid #6b7280; opacity: 0.7; }
.ampel-dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
.dot-rot { background: #ef4444; }
.dot-gelb { background: #f59e0b; }
.dot-gruen { background: #10b981; }
.dot-abgelaufen { background: #6b7280; }
.vertrag-name { font-weight: 600; margin-bottom: 2px; }
.vertrag-detail { font-size: 0.85rem; color: #6b7280; }
.vertrag-frist { font-size: 0.85rem; margin-top: 4px; }
.vertrag-ende { font-size: 0.8rem; color: #9ca3af; }
</style>
