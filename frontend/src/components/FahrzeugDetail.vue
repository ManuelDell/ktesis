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

      <!-- Anhänge -->
      <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5">
        <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
        <FileUploader
          :uploadArgs="{ doctype: 'Fahrzeug', docname: props.name, is_private: 1 }"
          @success="onUploadSuccess"
          fileTypes=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        >
          <template #default="{ openFileSelector, uploading, progress }">
            <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="md">
              <FeatherIcon name="upload" class="w-4 h-4 mr-2" />
              {{ uploading ? `Upload ${progress}%` : 'Datei hochladen' }}
            </Button>
          </template>
        </FileUploader>
        <AttachmentList ref="attachmentList" doctype="Fahrzeug" :docname="props.name" />
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

const isNew = computed(() => !props.name)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const attachmentList = ref(null)

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

function onUploadSuccess() {
  attachmentList.value?.reload()
}

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    if (isNew.value) {
      await create('Fahrzeug', payload)
    } else {
      await update('Fahrzeug', props.name, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>
