<template>
  <div :class="modal ? '' : 'bg-surface-white border border-outline-gray-2 rounded-lg overflow-hidden'">
    <!-- Header -->
    <div v-if="!modal" class="flex items-center justify-between px-5 py-4 bg-white border-b border-outline-gray-1">
      <h2 class="text-lg font-semibold text-ink-gray-9">
        {{ isNew ? 'Fahrzeug anlegen' : 'Fahrzeug bearbeiten' }}
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
        <!-- Linke Spalte -->
        <div class="space-y-4">
          <FormControl v-model="form.kennzeichen" type="text" label="Kennzeichen" required />
          <FormControl v-model="form.marke" type="text" label="Marke" required />
          <FormControl v-model="form.modell" type="text" label="Modell" required />
          <FormControl v-model.number="form.baujahr" type="number" label="Baujahr" />
          <FormControl v-model="form.farbe" type="text" label="Farbe" />
          <FormControl v-model="form.fin" type="text" label="FIN / VIN" />
          <FormControl v-model="form.erstzulassung" type="date" label="Erstzulassung" />
          <FormControl v-model.number="form.kaufpreis" type="number" label="Kaufpreis" />
        </div>

        <!-- Rechte Spalte -->
        <div class="space-y-4">
          <FormControl v-model="form.kaufdatum" type="date" label="Kaufdatum" />
          <FormControl v-model.number="form.kilometerstand_kauf" type="number" label="KM-Stand beim Kauf" />
          <FormControl v-model.number="form.aktueller_km_stand" type="number" label="Aktueller KM-Stand" />
          <FormControl v-model="form.kraftstoff" type="select" label="Kraftstoff"
            :options="['Benzin','Diesel','Elektro','Hybrid','Plug-in-Hybrid']" />
          <FormControl v-model.number="form.leistung_ps" type="number" label="Leistung (PS)" />
          <FormControl v-model.number="form.hubraum" type="number" label="Hubraum (ccm)" />
          <FormControl v-model="form.status" type="select" label="Status" required
            :options="['Aktiv','Verkauft','Entsorgt']" />
        </div>
      </div>

      <!-- Notizen (full width) -->
      <FormControl v-model="form.notizen" type="textarea" label="Notizen" />

      <!-- Dokumente -->
      <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5 space-y-4">
        <h4 class="text-sm font-medium text-ink-gray-7">Dokumente</h4>

        <!-- Fahrzeugschein -->
        <div>
          <p class="text-xs text-ink-gray-5 mb-2">Fahrzeugschein (Zulassungsbescheinigung Teil I)</p>
          <FileUploader
            :uploadArgs="{ doctype: 'Fahrzeug', docname: props.name, private: 1 }"
            @success="(f) => onUploadSuccessTyped(f, 'FZI')"
            fileTypes=".pdf,.jpg,.jpeg,.png"
          >
            <template #default="{ openFileSelector, uploading, progress }">
              <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="sm">
                <span class="flex items-center gap-2 whitespace-nowrap">
                  <FeatherIcon name="upload" class="w-4 h-4" />
                  {{ uploading ? `Upload ${progress}%` : 'Fahrzeugschein hochladen' }}
                </span>
              </Button>
            </template>
          </FileUploader>
          <div v-if="uploadSuccess" class="flex items-center gap-1.5 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mt-2 transition-all">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                    Datei erfolgreich hochgeladen
                  </div>
        </div>

        <!-- Fahrzeugbrief -->
        <div>
          <p class="text-xs text-ink-gray-5 mb-2">Fahrzeugbrief (Zulassungsbescheinigung Teil II)</p>
          <FileUploader
            :uploadArgs="{ doctype: 'Fahrzeug', docname: props.name, private: 1 }"
            @success="(f) => onUploadSuccessTyped(f, 'FZII')"
            fileTypes=".pdf,.jpg,.jpeg,.png"
          >
            <template #default="{ openFileSelector, uploading, progress }">
              <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="sm">
                <span class="flex items-center gap-2 whitespace-nowrap">
                  <FeatherIcon name="upload" class="w-4 h-4" />
                  {{ uploading ? `Upload ${progress}%` : 'Fahrzeugbrief hochladen' }}
                </span>
              </Button>
            </template>
          </FileUploader>
          <div v-if="uploadSuccess" class="flex items-center gap-1.5 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2 mt-2 transition-all">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>
                    Datei erfolgreich hochgeladen
                  </div>
        </div>

        <!-- Alle Anhänge -->
        <AttachmentList ref="attachmentList" doctype="Fahrzeug" :docname="docname" />
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

const docname = ref(props.name)
const isNew = computed(() => !docname.value)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const attachmentList = ref(null)
const uploadSuccess = ref(false)

const form = reactive({
  kennzeichen: '',
  marke: '',
  modell: '',
  baujahr: null,
  farbe: '',
  fin: '',
  erstzulassung: '',
  kaufpreis: null,
  kaufdatum: '',
  kilometerstand_kauf: null,
  aktueller_km_stand: null,
  kraftstoff: '',
  leistung_ps: null,
  hubraum: null,
  status: '',
  notizen: '',
})

onMounted(async () => {
  if (props.name) {
    loading.value = true
    try {
      const data = await get('Fahrzeug', props.name)
      Object.assign(form, {
        kennzeichen: data.kennzeichen || '',
        marke: data.marke || '',
        modell: data.modell || '',
        baujahr: data.baujahr ?? null,
        farbe: data.farbe || '',
        fin: data.fin || '',
        erstzulassung: data.erstzulassung || '',
        kaufpreis: data.kaufpreis ?? null,
        kaufdatum: data.kaufdatum || '',
        kilometerstand_kauf: data.kilometerstand_kauf ?? null,
        aktueller_km_stand: data.aktueller_km_stand ?? null,
        kraftstoff: data.kraftstoff || '',
        leistung_ps: data.leistung_ps ?? null,
        hubraum: data.hubraum ?? null,
        status: data.status || '',
        notizen: data.notizen || '',
      })
    } catch (e) {
      error.value = 'Fehler beim Laden der Fahrzeugdaten.'
    } finally {
      loading.value = false
    }
  }
})

async function renameFile(name, baseName) {
  try {
    const res = await fetch('/api/method/ktesis.api.attachments.rename_attachment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': window.frappe?.csrf_token || window.csrf_token || '' },
      body: JSON.stringify({ name, new_name: baseName })
    })
    const data = await res.json()
    return data.message?.file_name || null
  } catch (e) {
    return null
  }
}

async function onUploadSuccessTyped(file, prefix) {
  let displayFile = file ? { ...file } : null
  if (file?.name && prefix) {
    const kennz = (form.kennzeichen || '').replace(/\s+/g, '-').toUpperCase()
    const baseName = `${prefix}-${kennz}`
    const newFileName = await renameFile(file.name, baseName)
    if (newFileName && displayFile) displayFile.file_name = newFileName
  }
  if (displayFile && attachmentList.value?.addFile) {
    attachmentList.value.addFile(displayFile)
  } else {
    await new Promise(r => setTimeout(r, 800))
    attachmentList.value?.reload()
  }
  uploadSuccess.value = true
  setTimeout(() => { uploadSuccess.value = false }, 2500)
  setTimeout(() => attachmentList.value?.reload(), 1500)
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

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    if (isNew.value) {
      const res = await create('Fahrzeug', payload)
      docname.value = res.name
    } else {
      await update('Fahrzeug', docname.value, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>