<template>
  <div :class="modal ? '' : 'bg-surface-white border border-outline-gray-2 rounded-lg overflow-hidden'">
    <!-- Header -->
    <div v-if="!modal" class="flex items-center justify-between px-5 py-4 bg-white border-b border-outline-gray-1">
      <h2 class="text-lg font-semibold text-ink-gray-9">
        {{ isNew ? 'Bankkonto anlegen' : 'Bankkonto bearbeiten' }}
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
          <FormControl v-model="form.bezeichnung" type="text" label="Bezeichnung" required />
          <FormControl v-model="form.bank" type="text" label="Bank" />
          <FormControl v-model="form.iban" type="text" label="IBAN" />
          <FormControl v-model="form.bic" type="text" label="BIC" />
          <FormControl v-model="form.blz" type="text" label="Bankleitzahl (BLZ)" />
          <FormControl v-model="form.fints_url" type="text" label="FinTS-Server URL" />
          <FormControl v-model="form.kontonummer" type="text" label="Kontonummer" />
        </div>
        <div class="space-y-4">
          <FormControl v-model.number="form.kontostand_manuell" type="number" label="Kontostand (manuell)" />
          <FormControl :value="form.kontostand_live" type="number" label="Kontostand (live)" readonly />
          <FormControl :value="form.kontostand_abgerufen_am" type="text" label="Zuletzt abgerufen am" readonly />
          <FormControl v-model="form.kontotyp" type="select" label="Kontotyp"
            :options="['Girokonto','Tagesgeld','Sparbuch','Depot','Kreditkarte']" />
          <FormControl v-model="form.waehrung" type="text" label="Währung" />
          <FormControl v-model="form.fints_aktiv" type="checkbox" label="FinTS aktiv" />
          <FormControl v-model="form.aktiv" type="checkbox" label="Aktiv" />
        </div>
      </div>

      <FormControl v-model="form.notizen" type="textarea" label="Notizen" />

      <!-- Anhänge -->
      <div v-if="!isNew" class="border-t border-outline-gray-2 pt-5">
        <h4 class="text-sm font-medium text-ink-gray-7 mb-3">Anhänge</h4>
        <FileUploader
          :uploadArgs="{ doctype: 'Bankkonto', docname: props.name, is_private: 1 }"
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
        <AttachmentList ref="attachmentList" doctype="Bankkonto" :docname="props.name" />
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
  bezeichnung: '',
  bank: '',
  iban: '',
  bic: '',
  blz: '',
  fints_url: '',
  kontonummer: '',
  kontostand_manuell: null,
  kontostand_live: null,
  kontostand_abgerufen_am: '',
  kontotyp: '',
  waehrung: 'EUR',
  fints_aktiv: false,
  notizen: '',
  aktiv: true,
})

onMounted(async () => {
  if (props.name) {
    loading.value = true
    try {
      const data = await get('Bankkonto', props.name)
      Object.assign(form, {
        bezeichnung: data.bezeichnung || '',
        bank: data.bank || '',
        iban: data.iban || '',
        bic: data.bic || '',
        blz: data.blz || '',
        fints_url: data.fints_url || '',
        kontonummer: data.kontonummer || '',
        kontostand_manuell: data.kontostand_manuell ?? null,
        kontostand_live: data.kontostand_live ?? null,
        kontostand_abgerufen_am: data.kontostand_abgerufen_am || '',
        kontotyp: data.kontotyp || '',
        waehrung: data.waehrung || 'EUR',
        fints_aktiv: data.fints_aktiv ?? false,
        notizen: data.notizen || '',
        aktiv: data.aktiv ?? true,
      })
    } catch (e) {
      error.value = 'Fehler beim Laden der Bankkontodaten.'
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
      await create('Bankkonto', payload)
    } else {
      await update('Bankkonto', props.name, payload)
    }
    emit('saved')
  } catch (e) {
    error.value = e.message || 'Fehler beim Speichern.'
  } finally {
    saving.value = false
  }
}
</script>
