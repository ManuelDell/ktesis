<template>
  <div :class="modal ? '' : 'bg-surface-white border border-outline-gray-2 rounded-lg overflow-hidden'">
    <!-- Header -->
    <div v-if="!modal" class="flex items-center justify-between px-5 py-4 bg-white border-b border-outline-gray-1">
      <h2 class="text-lg font-semibold text-ink-gray-9">
        {{ isNew ? 'Darlehen anlegen' : 'Darlehen bearbeiten' }}
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
            <div>
            <label class="block text-xs text-ink-gray-6 mb-1">Referenz-Objekt (Wohnung)</label>
            <select v-model="form.wohnung" class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm bg-white">
              <option value="">— keine —</option>
              <option v-for="w in wohnungList" :key="w.name" :value="w.name">{{ w.bezeichnung || w.name }}</option>
            </select>
          </div>
            <FormControl v-model="form.darlehensgeber" type="text" label="Darlehensgeber" />
            <FormControl v-model="form.darlehensnummer" type="text" label="Darlehensnummer" />
            <FormControl v-model.number="form.darlehensbetrag" type="number" label="Darlehensbetrag" />
            <FormControl v-model.number="form.zinssatz" type="number" label="Zinssatz (%)" />
            <FormControl v-model.number="form.tilgungssatz" type="number" label="Tilgungssatz (%)" />
            <FormControl v-model.number="form.sondertilgungssatz" type="number" label="Sondertilgung erlaubt (% p.a.)" min="0" max="100" step="0.5" />
            <FormControl v-model.number="form.monatliche_rate" type="number" label="Monatliche Rate" />
          </div>
          <div class="space-y-4">
            <FormControl v-model="form.rate_inkl_zins_tilgung" type="checkbox" label="Rate inkl. Zins + Tilgung" />
            <FormControl v-model.number="form.laufzeit_jahre" type="number" label="Laufzeit (Jahre)" />
            <FormControl v-model="form.beginn" type="date" label="Beginn" />
            <FormControl v-model="form.ende" type="date" label="Geplantes Ende" />
            <FormControl v-model.number="form.restschuld" type="number" label="Aktuelle Restschuld" />
            <FormControl v-model.number="form.tilgungsfreie_jahre" type="number" label="Tilgungsfreie Jahre" />
            <FormControl v-model="form.sollzinsbindung_bis" type="date" label="Sollzinsbindung bis" />
            <FormControl v-model="form.aktiv" type="checkbox" label="Aktiv" />
          </div>
        </div>

        <FormControl v-model="form.notizen" type="textarea" label="Notizen" />

        <!-- Anhänge -->
        <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5">
          <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
          <FileUploader
            :uploadArgs="{ doctype: 'Darlehen', docname: docname, private: 1 }"
            @success="onUploadSuccess"
            fileTypes="image/*,application/pdf,.doc,.docx,.xls,.xlsx"
          >
            <template #default="{ openFileSelector, uploading, progress }">
              <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="md" class="touch-manipulation">
                <span class="flex items-center gap-2 whitespace-nowrap">
                  <FeatherIcon name="upload" class="w-4 h-4" />
                  {{ uploading ? `Upload ${progress}%` : 'Datei hochladen' }}
                </span>
              </Button>
            </template>
          </FileUploader>
          <div v-if="uploadSuccess" class="flex items-center gap-1.5 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mt-2 transition-all">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                    Datei erfolgreich hochgeladen
                  </div>
          <AttachmentList ref="attachmentList" doctype="Darlehen" :docname="docname" />
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

      <!-- Tab: Tilgungsplan -->
      <div v-else-if="activeTab === 'tilgungsplan'" class="p-5 space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-medium text-ink-gray-9">Tilgungsplan</h3>
          <Button v-if="!isNew"
            @click="loadAmortizationSchedule"
            variant="ghost" theme="gray"
            :disabled="tilgungsplanLoading"
          >
            <span v-if="tilgungsplanLoading" class="flex items-center gap-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600" />
              Berechne…
            </span>
            <span v-else>Tilgungsplan berechnen</span>
          </Button>
        </div>

        <div v-if="tilgungsplanError" class="bg-[var(--surface-red-1)] text-[var(--ink-red-2)] border border-[var(--outline-red-2)] rounded-lg px-4 py-3 text-sm">
          {{ tilgungsplanError }}
        </div>

        <div v-if="tilgungsplanSummary" class="bg-[var(--surface-gray-1)] rounded-lg p-4 text-sm grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span class="text-ink-gray-5">Darlehensbetrag:</span>
            <span class="ml-2 font-medium">{{ formatCurrency(tilgungsplanSummary.darlehensbetrag) }}</span>
          </div>
          <div>
            <span class="text-ink-gray-5">Zinssatz:</span>
            <span class="ml-2 font-medium">{{ tilgungsplanSummary.zinssatz }} %</span>
          </div>
          <div>
            <span class="text-ink-gray-5">Monatliche Rate:</span>
            <span class="ml-2 font-medium">{{ formatCurrency(tilgungsplanSummary.monatliche_rate) }}</span>
          </div>
        </div>

        <div v-if="!tilgungsplan || tilgungsplan.length === 0" class="text-center text-ink-gray-4 py-8 text-sm">
          Klicken Sie auf "Tilgungsplan berechnen", um den Tilgungsplan anzuzeigen.
        </div>

        <div v-else class="overflow-x-auto max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
          <table class="w-full text-sm border-collapse rounded-lg overflow-hidden border border-[var(--outline-gray-1)]">
            <thead class="bg-surface-gray-1 sticky top-0">
              <tr class="border-b border-outline-gray-2">
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Monat</th>
                <th class="text-left py-3 px-4 font-medium text-ink-gray-5">Datum</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Rate</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Zins</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Tilgung</th>
                <th class="text-right py-3 px-4 font-medium text-ink-gray-5">Restschuld</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in tilgungsplan" :key="idx" class="border-b border-outline-gray-1 hover:bg-surface-gray-2"
                :class="{ 'font-semibold bg-gray-50': idx === tilgungsplan.length - 1 }">
                <td class="py-2 px-4">{{ row.monat }}</td>
                <td class="py-2 px-4">{{ formatDate(row.datum) }}</td>
                <td class="py-2 px-4 text-right">{{ formatCurrency(row.rate) }}</td>
                <td class="py-2 px-4 text-right">{{ formatCurrency(row.zins) }}</td>
                <td class="py-2 px-4 text-right">{{ formatCurrency(row.tilgung) }}</td>
                <td class="py-2 px-4 text-right">{{ formatCurrency(row.restschuld) }}</td>
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

const { get, create, update, call, list } = useApi()

const docname = ref(props.name)
const isNew = computed(() => !docname.value)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const activeTab = ref('stammdaten')
const attachmentList = ref(null)
const uploadSuccess = ref(false)

const tilgungsplan = ref([])
const tilgungsplanSummary = ref(null)
const tilgungsplanLoading = ref(false)
const tilgungsplanError = ref(null)
const wohnungList = ref([])

const tabs = [
  { key: 'stammdaten', label: 'Stammdaten' },
  { key: 'tilgungsplan', label: 'Tilgungsplan' },
]

const form = reactive({
  bezeichnung: '',
  wohnung: '',
  darlehensgeber: '',
  darlehensnummer: '',
  darlehensbetrag: null,
  zinssatz: null,
  tilgungssatz: null,
  sondertilgungssatz: null,
  monatliche_rate: null,
  rate_inkl_zins_tilgung: true,
  laufzeit_jahre: null,
  beginn: '',
  ende: '',
  restschuld: null,
  tilgungsfreie_jahre: null,
  sollzinsbindung_bis: '',
  notizen: '',
  aktiv: true,
})

onMounted(async () => {
  wohnungList.value = await list('Wohnung', { fields: ['name', 'bezeichnung'], limit: 50 }) || []
  if (props.name) {
    loading.value = true
    try {
      const data = await get('Darlehen', props.name)
      Object.assign(form, {
        bezeichnung: data.bezeichnung || '',
        wohnung: data.wohnung || '',
        darlehensgeber: data.darlehensgeber || '',
        darlehensnummer: data.darlehensnummer || '',
        darlehensbetrag: data.darlehensbetrag ?? null,
        zinssatz: data.zinssatz ?? null,
        tilgungssatz: data.tilgungssatz ?? null,
        sondertilgungssatz: data.sondertilgungssatz ?? null,
        monatliche_rate: data.monatliche_rate ?? null,
        rate_inkl_zins_tilgung: data.rate_inkl_zins_tilgung ?? true,
        laufzeit_jahre: data.laufzeit_jahre ?? null,
        beginn: data.beginn || '',
        ende: data.ende || '',
        restschuld: data.restschuld ?? null,
        tilgungsfreie_jahre: data.tilgungsfreie_jahre ?? null,
        sollzinsbindung_bis: data.sollzinsbindung_bis || '',
        notizen: data.notizen || '',
        aktiv: data.aktiv ?? true,
      })
    } catch (e) {
      error.value = 'Fehler beim Laden der Darlehensdaten.'
    } finally {
      loading.value = false
    }
  }
})

function formatCurrency(val) {
  if (val == null) return '-'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val)
}

function formatDate(val) {
  if (!val) return '-'
  const d = new Date(val)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

async function onUploadSuccess(file) {
  if (file && attachmentList.value?.addFile) {
    attachmentList.value.addFile(file)
  } else {
    await new Promise(r => setTimeout(r, 800))
    attachmentList.value?.reload()
  }
  uploadSuccess.value = true
  setTimeout(() => { uploadSuccess.value = false }, 2500)
  setTimeout(() => attachmentList.value?.reload(), 1500)
}

async function loadAmortizationSchedule() {
  tilgungsplanLoading.value = true
  tilgungsplanError.value = null
  try {
    const result = await call('ktesis.api.darlehen.calculate_amortization_schedule', { name: props.name })
    tilgungsplan.value = result.tilgungsplan || []
    tilgungsplanSummary.value = {
      darlehensbetrag: result.darlehensbetrag,
      zinssatz: result.zinssatz,
      monatliche_rate: result.monatliche_rate,
    }
  } catch (e) {
    tilgungsplanError.value = e.message || 'Fehler bei der Berechnung des Tilgungsplans.'
  } finally {
    tilgungsplanLoading.value = false
  }
}

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    if (isNew.value) {
      const res = await create('Darlehen', payload)
      docname.value = res.name
    } else {
      await update('Darlehen', docname.value, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>
