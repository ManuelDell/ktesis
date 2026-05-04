<template>
  <div :class="modal ? '' : 'bg-surface-white border border-outline-gray-2 rounded-lg overflow-hidden'">
    <!-- Header -->
    <div v-if="!modal" class="flex items-center justify-between px-5 py-4 bg-white border-b border-outline-gray-1">
      <h2 class="text-lg font-semibold text-ink-gray-9">
        {{ isNew ? 'Vertrag anlegen' : 'Vertrag bearbeiten' }}
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

    <!-- Form -->
    <form v-else @submit.prevent="handleSave" class="p-5 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
        <div class="space-y-4">
          <FormControl v-model="form.titel" type="text" label="Titel" required />
          <FormControl v-model="form.vertragstyp" type="select" label="Vertragstyp" required
            :options="['Versicherung','Darlehen','Miete','Kaufvertrag','Wartung','Sonstiges']" />
          <FormControl v-model="form.referenz_doctype" type="select" label="Referenz Typ"
            :options="['Fahrzeug','Wohnung']" />
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Referenz</label>
            <select v-model="form.referenz_name" :disabled="!form.referenz_doctype"
              class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm text-ink-gray-9 bg-white focus:outline-none focus:ring-2 focus:ring-outline-gray-4 disabled:bg-surface-gray-2 disabled:text-ink-gray-4">
              <option value="">-- Bitte wählen --</option>
              <option v-for="opt in referenzOptionen" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <FormControl v-model="form.vertragspartner" type="text" label="Vertragspartner" />
          <FormControl v-model="form.vertragsnummer" type="text" label="Vertragsnummer" />
          <FormControl v-model="form.vertragsbeginn" type="date" label="Vertragsbeginn" />
        </div>
        <div class="space-y-4">
          <FormControl v-model="form.vertragsende" type="date" label="Vertragsende" />
          <FormControl v-model="form.kuendigungsfrist" type="text" label="Kündigungsfrist" />
          <FormControl v-model.number="form.kosten_monatlich" type="number" label="Kosten monatlich" />
          <FormControl v-model.number="form.kosten_jaehrlich" type="number" label="Kosten jährlich" />
          <FormControl v-model="form.zahlungsrhythmus" type="select" label="Zahlungsrhythmus"
            :options="['Monatlich','Vierteljährlich','Halbjährlich','Jährlich','Einmalig']" />
          <FormControl v-model="form.aktiv" type="checkbox" label="Aktiv" />
        </div>
      </div>

      <FormControl v-model="form.notizen" type="textarea" label="Notizen" />

      <!-- Anhänge -->
      <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5">
        <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
        <FileUploader
          :uploadArgs="{ doctype: 'Vertrag', docname: docname, private: 1 }"
          @success="onUploadSuccess"
          fileTypes="image/*,application/pdf,.doc,.docx,.xls,.xlsx"
        >
          <template #default="{ openFileSelector, uploading, progress }">
            <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="md" class="touch-manipulation">
              <FeatherIcon name="upload" class="w-4 h-4 mr-2" />
              {{ uploading ? `Upload ${progress}%` : 'Datei hochladen' }}
            </Button>
          </template>
        </FileUploader>
        <div v-if="uploadSuccess" class="flex items-center gap-1.5 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mt-2 transition-all">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                  Datei erfolgreich hochgeladen
                </div>
        <AttachmentList ref="attachmentList" doctype="Vertrag" :docname="docname" />
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { FileUploader } from 'frappe-ui'
import { useApi } from '../composables/useApi.js'
import AttachmentList from './AttachmentList.vue'

const props = defineProps({
  name: { type: String, default: null },
  modal: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'saved'])

const { get, create, update } = useApi()

const docname = ref(props.name)
const isNew = computed(() => !docname.value)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const attachmentList = ref(null)
const uploadSuccess = ref(false)
const referenzOptionen = ref([])

const form = reactive({
  titel: '',
  vertragstyp: '',
  referenz_doctype: '',
  referenz_name: '',
  vertragspartner: '',
  vertragsnummer: '',
  vertragsbeginn: '',
  vertragsende: '',
  kuendigungsfrist: '',
  kosten_monatlich: null,
  kosten_jaehrlich: null,
  zahlungsrhythmus: '',
  notizen: '',
  aktiv: true,
})

async function ladeReferenzOptionen() {
  if (!form.referenz_doctype) {
    referenzOptionen.value = []
    return
  }
  try {
    let url
    if (form.referenz_doctype === 'Fahrzeug') {
      url = '/api/method/ktesis.api.fahrzeug.get_fahrzeuge_liste'
    } else if (form.referenz_doctype === 'Wohnung') {
      url = '/api/method/ktesis.api.wohnung.get_wohnungen_liste'
    } else {
      referenzOptionen.value = []
      return
    }
    const res = await fetch(url, {
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' }
    })
    const data = await res.json()
    if (data.message && data.message.items) {
      referenzOptionen.value = data.message.items
    } else {
      referenzOptionen.value = []
    }
  } catch (e) {
    referenzOptionen.value = []
  }
}

watch(() => form.referenz_doctype, async (neu, alt) => {
  if (neu !== alt) {
    form.referenz_name = ''
    await ladeReferenzOptionen()
  }
})

watch(() => form.kosten_monatlich, (val) => {
  if (val && !form.kosten_jaehrlich) {
    form.kosten_jaehrlich = Math.round(val * 12 * 100) / 100
  }
})

watch(() => form.kosten_jaehrlich, (val) => {
  if (val && !form.kosten_monatlich) {
    form.kosten_monatlich = Math.round(val / 12 * 100) / 100
  }
})

onMounted(async () => {
  if (props.name) {
    loading.value = true
    try {
      const data = await get('Vertrag', props.name)
      Object.assign(form, {
        titel: data.titel || '',
        vertragstyp: data.vertragstyp || '',
        referenz_doctype: data.referenz_doctype || '',
        referenz_name: data.referenz_name || '',
        vertragspartner: data.vertragspartner || '',
        vertragsnummer: data.vertragsnummer || '',
        vertragsbeginn: data.vertragsbeginn || '',
        vertragsende: data.vertragsende || '',
        kuendigungsfrist: data.kuendigungsfrist || '',
        kosten_monatlich: data.kosten_monatlich ?? null,
        kosten_jaehrlich: data.kosten_jaehrlich ?? null,
        zahlungsrhythmus: data.zahlungsrhythmus || '',
        notizen: data.notizen || '',
        aktiv: data.aktiv ?? true,
      })
      if (form.referenz_doctype) {
        await ladeReferenzOptionen()
      }
    } catch (e) {
      error.value = 'Fehler beim Laden der Vertragsdaten.'
    } finally {
      loading.value = false
    }
  }
})

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

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    if (isNew.value) {
      const res = await create('Vertrag', payload)
      docname.value = res.name
    } else {
      await update('Vertrag', docname.value, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>
