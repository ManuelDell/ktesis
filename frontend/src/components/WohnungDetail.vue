<template>
  <div :class="modal ? '' : 'bg-surface-white border border-outline-gray-2 rounded-lg overflow-hidden'">
    <!-- Header -->
    <div v-if="!modal" class="flex items-center justify-between px-5 py-4 bg-white border-b border-outline-gray-1">
      <h2 class="text-lg font-semibold text-ink-gray-9">
        {{ isNew ? 'Wohnung anlegen' : 'Wohnung bearbeiten' }}
      </h2>
      <button
        @click="$emit('close')"
        class="text-ink-gray-4 hover:text-ink-gray-9 transition-colors p-1 rounded-lg hover:bg-surface-gray-2"
      >
        <FeatherIcon name="x" class="h-5 w-5" />
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--outline-gray-4)]" />
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="px-6 pt-4 flex border-b border-outline-gray-1 mb-4">
        <nav class="flex gap-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            class="pb-3 text-sm font-medium border-b-2 transition-colors cursor-pointer bg-transparent"
            :class="activeTab === tab.key ? 'border-surface-gray-9 text-ink-gray-9' : 'border-transparent text-ink-gray-4 hover:text-ink-gray-6'"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab: Stammdaten -->
      <form v-if="activeTab === 'stammdaten'" @submit.prevent="handleSave" class="p-5 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
          <div class="space-y-4">
            <FormControl v-model="form.bezeichnung" type="text" label="Bezeichnung" required />
            <FormControl v-model="form.strasse" type="text" label="Straße" />
            <FormControl v-model="form.hausnummer" type="text" label="Hausnummer" />
            <FormControl v-model="form.plz" type="text" label="PLZ" />
            <FormControl v-model="form.ort" type="text" label="Ort" />
            <FormControl v-model="form.land" type="text" label="Land" />
          </div>
          <div class="space-y-4">
            <FormControl v-model.number="form.wohnflaeche" type="number" label="Wohnfläche (m²)" />
            <FormControl v-model.number="form.zimmer" type="number" label="Zimmeranzahl" />
            <FormControl v-model.number="form.baujahr" type="number" label="Baujahr" />
            <FormControl
              v-model="form.nutzungstyp"
              type="select"
              label="Nutzungstyp"
              :options="['', 'Eigentum', 'Gemietet', 'Vermietet']"
            />
            <FormControl
              v-model="form.wohnungstyp"
              type="select"
              label="Gebäudetyp"
              :options="['', 'Eigentumswohnung', 'Reihenhaus', 'Einfamilienhaus', 'Mehrfamilienhaus', 'Gewerbe']"
            />
            <FormControl
              v-model="form.status"
              type="select"
              label="Status"
              required
              :options="['Bewohnt', 'Vermietet', 'Leerstehend', 'Verkauft']"
            />
          </div>
        </div>

        <!-- Kaufdetails (nur Eigentum) -->
        <template v-if="form.nutzungstyp === 'Eigentum' || !form.nutzungstyp">
          <div class="border-t border-outline-gray-2 pt-4">
            <h4 class="text-sm font-semibold text-ink-gray-7 mb-3">Kaufdetails</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
              <FormControl v-model.number="form.kaufpreis" type="number" label="Kaufpreis (€)" />
              <FormControl v-model="form.kaufdatum" type="date" label="Kaufdatum" />
              <FormControl v-model.number="form.kauf_wert" type="number" label="Kauf-/Einstandswert (€)" />
              <FormControl v-model.number="form.aktueller_wert" type="number" label="Geschätzter aktueller Wert (€)" />
            </div>
          </div>
        </template>

        <!-- Mietdetails (nur Gemietet) -->
        <template v-if="form.nutzungstyp === 'Gemietet'">
          <div class="border-t border-outline-gray-2 pt-4">
            <h4 class="text-sm font-semibold text-ink-gray-7 mb-3">Mietdetails</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
              <FormControl v-model.number="form.monatliche_miete" type="number" label="Monatliche Kaltmiete (€)" />
              <FormControl v-model.number="form.nebenkosten_monatlich" type="number" label="Monatliche Nebenkosten (€)" />
              <div>
                <label class="block text-xs text-ink-gray-6 mb-1">Budget-Zuordnung Miete</label>
                <select v-model="form.mietbudgetposten" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
                  <option value="">— kein —</option>
                  <option v-for="bp in budgetpostenList" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-ink-gray-6 mb-1">Budget-Zuordnung Nebenkosten</label>
                <select v-model="form.nebenkostenbudgetposten" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
                  <option value="">— kein —</option>
                  <option v-for="bp in budgetpostenList" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                </select>
              </div>
              <FormControl v-model="form.vermieter" type="text" label="Vermieter" />
              <FormControl v-model="form.mietbeginn" type="date" label="Mietbeginn" />
            </div>
          </div>
        </template>

        <!-- Vermietungsdetails (nur Vermietet) -->
        <template v-if="form.nutzungstyp === 'Vermietet'">
          <div class="border-t border-outline-gray-2 pt-4">
            <h4 class="text-sm font-semibold text-ink-gray-7 mb-3">Vermietungsdetails</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
              <FormControl v-model.number="form.mieteinnahme_monatlich" type="number" label="Monatliche Mieteinnahme (€)" />
              <FormControl v-model.number="form.nebenkosten_monatlich_verm" type="number" label="Monatliche Nebenkosten (€)" />
              <div>
                <label class="block text-xs text-ink-gray-6 mb-1">Budget-Zuordnung Einnahme</label>
                <select v-model="form.einnahmebudgetposten" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
                  <option value="">— kein —</option>
                  <option v-for="bp in budgetpostenList" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-ink-gray-6 mb-1">Budget-Zuordnung Nebenkosten</label>
                <select v-model="form.nebenkostenbudgetposten_verm" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
                  <option value="">— kein —</option>
                  <option v-for="bp in budgetpostenList" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                </select>
              </div>
              <FormControl v-model="form.mieter" type="text" label="Mieter" />
              <FormControl v-model="form.mietvertrag_beginn" type="date" label="Mietvertragsbeginn" />
            </div>
          </div>
        </template>

        <!-- Soll-Ist Vergleich -->
        <template v-if="!isNew && (form.nutzungstyp === 'Gemietet' || form.nutzungstyp === 'Vermietet')">
          <div class="border-t border-outline-gray-2 pt-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-ink-gray-7">Soll-Ist Vergleich</h4>
              <Button type="button" variant="outline" theme="gray" size="sm" :loading="loadingVergleich" @click="loadVergleich">
                <FeatherIcon name="bar-chart-2" class="w-4 h-4 mr-1" />
                Aktualisieren
              </Button>
            </div>
            <div v-if="vergleich" class="space-y-2">
              <div v-for="p in vergleich.posten" :key="p.label" class="flex items-center justify-between text-sm px-3 py-2 bg-surface-gray-1 rounded">
                <span class="text-ink-gray-7 font-medium">{{ p.label }}</span>
                <span class="text-ink-gray-5">Soll: {{ formatCurrency(p.soll) }}</span>
                <span class="text-ink-gray-5">Ist: {{ formatCurrency(p.ist) }}</span>
                <span :class="p.differenz > 0.01 ? 'text-ink-red-4' : p.differenz < -0.01 ? 'text-ink-green-3' : 'text-ink-gray-5'">
                  {{ p.differenz > 0.01 ? '−' : p.differenz < -0.01 ? '+' : '' }}{{ formatCurrency(Math.abs(p.differenz)) }}
                </span>
              </div>
              <div v-if="!vergleich.posten?.length" class="text-sm text-ink-gray-4 text-center py-2">
                Keine Budgetposten verknüpft.
              </div>
            </div>
          </div>
        </template>

        <FormControl v-model="form.notizen" type="textarea" label="Notizen" />

        <!-- Anhänge -->
        <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5">
          <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
          <FileUploader
            :uploadArgs="{ doctype: 'Wohnung', docname: props.name, is_private: 1 }"
            @success="onUploadSuccess"
            fileTypes=".pdf,.jpg,.jpeg,.png,.doc,.docx"
          >
            <template #default="{ openFileSelector, uploading, progress }">
              <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="md">
                <span class="flex items-center gap-2 whitespace-nowrap">
                  <FeatherIcon name="upload" class="w-4 h-4" />
                  {{ uploading ? `Upload ${progress}%` : 'Datei hochladen' }}
                </span>
              </Button>
            </template>
          </FileUploader>
          <AttachmentList ref="attachmentList" doctype="Wohnung" :docname="props.name" />
        </div>

        <!-- Error -->
        <div v-if="error" class="bg-[var(--surface-red-1)] text-[var(--ink-red-2)] border border-[var(--outline-red-2)] rounded-lg px-4 py-3 text-sm">
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t border-outline-gray-2">
          <Button v-if="!modal" type="button" @click="$emit('close')" variant="outline" theme="gray">
            Abbrechen
          </Button>
          <Button type="submit" :disabled="saving" variant="solid" theme="gray">
            <span v-if="saving" class="flex items-center gap-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-outline-gray-4" />
              Speichern…
            </span>
            <span v-else>Speichern</span>
          </Button>
        </div>
      </form>

      <!-- Tab: Abschreibungen -->
      <div v-else-if="activeTab === 'abschreibungen'" class="p-5 space-y-6">
        <div v-if="!form.abschreibungen || form.abschreibungen.length === 0" class="text-center text-ink-gray-4 py-8 text-sm">
          Keine Abschreibungen vorhanden.
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm border-collapse rounded-lg overflow-hidden border border-[var(--outline-gray-1)]">
            <thead>
              <tr class="border-b border-outline-gray-2">
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Jahr</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Satz</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Betrag</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Restbuchwert</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Bemerkung</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in form.abschreibungen" :key="idx" class="border-b border-outline-gray-1 hover:bg-surface-gray-2">
                <td class="py-3 px-4">{{ item.jahr }}</td>
                <td class="py-3 px-4">{{ item.abschreibungssatz != null ? item.abschreibungssatz + ' %' : '-' }}</td>
                <td class="py-3 px-4 text-right">{{ formatCurrency(item.abschreibungsbetrag) }}</td>
                <td class="py-3 px-4 text-right">{{ formatCurrency(item.restbuchwert) }}</td>
                <td class="py-3 px-4">{{ item.bemerkung || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex items-center justify-end gap-3 pt-4 border-t border-outline-gray-2">
          <Button v-if="!modal" type="button" @click="$emit('close')" variant="outline" theme="gray">Schließen</Button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { FileUploader } from 'frappe-ui'
import { useApi } from '../composables/useApi.js'
import AttachmentList from './AttachmentList.vue'

const props = defineProps({
  name: { type: String, default: null },
  modal: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'saved'])

const { get, create, update, list, call } = useApi()

const isNew = computed(() => !props.name)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const activeTab = ref('stammdaten')
const attachmentList = ref(null)
const budgetpostenList = ref([])
const vergleich = ref(null)
const loadingVergleich = ref(false)

const tabs = [
  { key: 'stammdaten', label: 'Stammdaten' },
  { key: 'abschreibungen', label: 'Abschreibungen' },
]

const form = reactive({
  bezeichnung: '',
  strasse: '',
  hausnummer: '',
  plz: '',
  ort: '',
  land: 'Deutschland',
  wohnflaeche: null,
  zimmer: null,
  baujahr: null,
  nutzungstyp: '',
  wohnungstyp: '',
  status: '',
  kaufpreis: null,
  kaufdatum: '',
  kauf_wert: null,
  aktueller_wert: null,
  monatliche_miete: null,
  mietbudgetposten: '',
  nebenkosten_monatlich: null,
  nebenkostenbudgetposten: '',
  vermieter: '',
  mietbeginn: '',
  mieteinnahme_monatlich: null,
  einnahmebudgetposten: '',
  nebenkosten_monatlich_verm: null,
  nebenkostenbudgetposten_verm: '',
  mieter: '',
  mietvertrag_beginn: '',
  notizen: '',
  abschreibungen: [],
})

onMounted(async () => {
  budgetpostenList.value = await list('Budgetposten', { fields: ['name', 'kategorie'], limit: 50 }) || []
  if (props.name) {
    loading.value = true
    try {
      const data = await get('Wohnung', props.name)
      Object.assign(form, {
        bezeichnung: data.bezeichnung || '',
        strasse: data.strasse || '',
        hausnummer: data.hausnummer || '',
        plz: data.plz || '',
        ort: data.ort || '',
        land: data.land || 'Deutschland',
        wohnflaeche: data.wohnflaeche ?? null,
        zimmer: data.zimmer ?? null,
        baujahr: data.baujahr ?? null,
        nutzungstyp: data.nutzungstyp || '',
        wohnungstyp: data.wohnungstyp || '',
        status: data.status || '',
        kaufpreis: data.kaufpreis ?? null,
        kaufdatum: data.kaufdatum || '',
        kauf_wert: data.kauf_wert ?? null,
        aktueller_wert: data.aktueller_wert ?? null,
        monatliche_miete: data.monatliche_miete ?? null,
        mietbudgetposten: data.mietbudgetposten || '',
        nebenkosten_monatlich: data.nebenkosten_monatlich ?? null,
        nebenkostenbudgetposten: data.nebenkostenbudgetposten || '',
        vermieter: data.vermieter || '',
        mietbeginn: data.mietbeginn || '',
        mieteinnahme_monatlich: data.mieteinnahme_monatlich ?? null,
        einnahmebudgetposten: data.einnahmebudgetposten || '',
        nebenkosten_monatlich_verm: data.nebenkosten_monatlich_verm ?? null,
        nebenkostenbudgetposten_verm: data.nebenkostenbudgetposten_verm || '',
        mieter: data.mieter || '',
        mietvertrag_beginn: data.mietvertrag_beginn || '',
        notizen: data.notizen || '',
        abschreibungen: data.abschreibungen || [],
      })
      if (data.nutzungstyp === 'Gemietet' || data.nutzungstyp === 'Vermietet') {
        loadVergleich()
      }
    } catch (e) {
      error.value = 'Fehler beim Laden der Wohnungsdaten.'
    } finally {
      loading.value = false
    }
  }
})

async function loadVergleich() {
  if (!props.name) return
  loadingVergleich.value = true
  try {
    vergleich.value = await call('ktesis.api.budget.wohnung_budget_vergleich', { wohnung_name: props.name })
  } catch (e) {
    vergleich.value = null
  } finally {
    loadingVergleich.value = false
  }
}

function formatCurrency(val) {
  if (val == null) return '-'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val)
}

function onUploadSuccess() {
  attachmentList.value?.reload()
}

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    if (isNew.value) {
      await create('Wohnung', payload)
    } else {
      await update('Wohnung', props.name, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>