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
            <FormControl v-model.number="form.wohnflaeche" type="number" label="Wohnfläche (m²)" />
            <FormControl v-model.number="form.zimmer" type="number" label="Zimmeranzahl" />
          </div>
          <div class="space-y-4">
            <FormControl v-model.number="form.baujahr" type="number" label="Baujahr" />
            <FormControl v-model.number="form.kaufpreis" type="number" label="Kaufpreis" />
            <FormControl v-model="form.kaufdatum" type="date" label="Kaufdatum" />
            <FormControl v-model.number="form.kauf_wert" type="number" label="Kauf-/Einstandswert" />
            <FormControl v-model.number="form.aktueller_wert" type="number" label="Geschätzter aktueller Wert" />
            <FormControl v-model="form.wohnungstyp" type="select" label="Wohnungstyp"
              :options="['Eigentumswohnung','Reihenhaus','Einfamilienhaus','Mehrfamilienhaus','Gewerbe']" />
            <FormControl v-model="form.status" type="select" label="Status" required
              :options="['Bewohnt','Vermietet','Leerstehend','Verkauft']" />
          </div>
        </div>

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
              <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="sm">
                <FeatherIcon name="upload" class="w-4 h-4 mr-2" />
                {{ uploading ? `Upload ${progress}%` : 'Datei hochladen' }}
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
          <Button v-if="!modal" type="button" @click="$emit('close')"
            variant="outline" theme="gray">
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
        <div class="flex items-center justify-between">
          <h3 class="text-base font-medium text-ink-gray-9">Abschreibungen</h3>
        </div>

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

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3 pt-4 border-t border-outline-gray-2">
          <Button v-if="!modal" type="button" @click="$emit('close')"
            variant="outline" theme="gray">
            Schließen
          </Button>
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

const { get, create, update } = useApi()

const isNew = computed(() => !props.name)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const activeTab = ref('stammdaten')
const attachmentList = ref(null)

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
  kaufpreis: null,
  kaufdatum: '',
  kauf_wert: null,
  aktueller_wert: null,
  wohnungstyp: '',
  status: '',
  notizen: '',
  abschreibungen: [],
})

onMounted(async () => {
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
        kaufpreis: data.kaufpreis ?? null,
        kaufdatum: data.kaufdatum || '',
        kauf_wert: data.kauf_wert ?? null,
        aktueller_wert: data.aktueller_wert ?? null,
        wohnungstyp: data.wohnungstyp || '',
        status: data.status || '',
        notizen: data.notizen || '',
        abschreibungen: data.abschreibungen || [],
      })
    } catch (e) {
      error.value = 'Fehler beim Laden der Wohnungsdaten.'
    } finally {
      loading.value = false
    }
  }
})

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
