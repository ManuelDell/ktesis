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
          <FormControl v-model="form.kontonummer" type="text" label="Kontonummer" />
        </div>
        <div class="space-y-4">
          <FormControl v-model.number="form.kontostand_manuell" type="number" label="Kontostand (manuell)" />
          <div>
            <label class="text-sm font-medium text-ink-gray-7">Kontostand (live)</label>
            <div class="mt-1 flex items-center gap-3">
              <span class="text-sm font-semibold" :class="form.kontostand_live != null ? 'text-ink-green-3' : 'text-ink-gray-4'">
                {{ form.kontostand_live != null ? formatCurrency(form.kontostand_live) : '—' }}
              </span>
              <span v-if="form.kontostand_abgerufen_am" class="text-xs text-ink-gray-4">
                {{ formatDate(form.kontostand_abgerufen_am) }}
              </span>
            </div>
          </div>
          <FormControl v-model="form.kontotyp" type="select" label="Kontotyp"
            :options="['Girokonto','Tagesgeld','Sparbuch','Depot','Kreditkarte']" />
          <FormControl v-model="form.waehrung" type="text" label="Währung" />
          <FormControl v-model="form.fints_aktiv" type="checkbox" label="FinTS aktiv" />
          <FormControl v-model="form.aktiv" type="checkbox" label="Aktiv" />
        </div>
      </div>

      <!-- FinTS Konfiguration -->
      <div v-if="form.fints_aktiv" class="border border-outline-gray-2 rounded-lg p-4 space-y-4 bg-surface-gray-1">
        <h4 class="text-sm font-semibold text-ink-gray-7 flex items-center gap-2">
          <FeatherIcon name="shield" class="w-4 h-4" />
          FinTS / Online-Banking Zugangsdaten
        </h4>

        <!-- Bankauswahl -->
        <div>
          <label class="text-sm font-medium text-ink-gray-7">Bank-Voreinstellung</label>
          <select
            v-model="selectedBankPreset"
            @change="applyBankPreset"
            class="mt-1 w-full rounded-md border border-outline-gray-3 bg-white px-3 py-2 text-sm text-ink-gray-8 focus:outline-none focus:ring-2 focus:ring-outline-gray-4"
          >
            <option value="">— Eigene URL eingeben —</option>
            <option v-for="b in bankPresets" :key="b.name" :value="b.name">{{ b.name }}</option>
          </select>
          <p v-if="selectedPresetNotes" class="mt-1 text-xs text-ink-gray-5">{{ selectedPresetNotes }}</p>
        </div>

        <FormControl v-model="form.fints_url" type="text" label="FinTS-Server URL" placeholder="https://..." />
        <FormControl v-model="form.fints_login" type="text" label="Online-Banking Loginname" placeholder="Kontonummer, Kundennummer oder Alias" />
        <FormControl v-model="form.fints_pin" type="password" label="Online-Banking PIN" placeholder="Wird verschlüsselt gespeichert" />

        <!-- Sync Button -->
        <div v-if="!isNew" class="pt-2">
          <Button
            type="button"
            variant="outline"
            theme="gray"
            :disabled="syncing"
            @click="startSync"
          >
            <span v-if="syncing" class="flex items-center gap-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-outline-gray-4" />
              {{ syncStatusLabel }}
            </span>
            <span v-else class="flex items-center gap-2">
              <FeatherIcon name="refresh-cw" class="w-4 h-4" />
              Kontostand abrufen
            </span>
          </Button>
          <p v-if="syncError" class="mt-2 text-sm text-ink-red-4">{{ syncError }}</p>
          <p v-if="syncSuccess" class="mt-2 text-sm text-ink-green-3">{{ syncSuccess }}</p>
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
            <Button @click="openFileSelector" :loading="uploading" variant="outline" theme="gray" size="md">
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

    <!-- TAN Dialog -->
    <Dialog
      :options="{ title: 'TAN erforderlich', size: 'sm' }"
      v-model="showTanDialog"
    >
      <template #body>
        <div class="p-5 space-y-4">
          <div class="bg-surface-yellow-1 border border-outline-yellow-2 rounded-lg px-4 py-3">
            <p class="text-sm font-medium text-ink-yellow-3">{{ tanChallengeLabel }}</p>
            <p v-if="tanChallenge" class="mt-1 text-base font-mono font-bold text-ink-gray-9">{{ tanChallenge }}</p>
          </div>
          <FormControl
            v-model="tanInput"
            type="text"
            label="TAN eingeben"
            placeholder="Ihre TAN"
            autofocus
            @keydown.enter.prevent="submitTan"
          />
          <p v-if="tanError" class="text-sm text-ink-red-4">{{ tanError }}</p>
          <div class="flex gap-3 justify-end pt-2">
            <Button variant="outline" theme="gray" @click="cancelSync">Abbrechen</Button>
            <Button variant="solid" theme="gray" :disabled="!tanInput || tanSubmitting" @click="submitTan">
              <span v-if="tanSubmitting" class="flex items-center gap-2">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-outline-gray-4" />
                Senden…
              </span>
              <span v-else>TAN bestätigen</span>
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { FileUploader } from 'frappe-ui'
import { useApi } from '../composables/useApi.js'
import AttachmentList from './AttachmentList.vue'

const props = defineProps({
  name: { type: String, default: null },
  modal: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'saved'])

const { get, create, update, call } = useApi()

const isNew = computed(() => !props.name)
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const attachmentList = ref(null)

// FinTS sync state
const syncing = ref(false)
const syncJobId = ref(null)
const syncStatusLabel = ref('Verbinde…')
const syncError = ref(null)
const syncSuccess = ref(null)
let pollTimer = null
let pollCount = 0
const POLL_TIMEOUT_COUNT = 30  // 30 × 2s = 60s timeout for "pending" state

// TAN dialog state
const showTanDialog = ref(false)
const tanChallenge = ref('')
const tanChallengeLabel = ref('TAN eingeben')
const tanInput = ref('')
const tanError = ref(null)
const tanSubmitting = ref(false)

// Bank presets
const bankPresets = ref([])
const selectedBankPreset = ref('')

const selectedPresetNotes = computed(() => {
  if (!selectedBankPreset.value) return ''
  const b = bankPresets.value.find(p => p.name === selectedBankPreset.value)
  return b?.notes || ''
})

const form = reactive({
  bezeichnung: '',
  bank: '',
  iban: '',
  bic: '',
  blz: '',
  fints_url: '',
  fints_login: '',
  fints_pin: '',
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
  // Load bank presets
  try {
    const presets = await call('ktesis.api.fints.get_bank_list')
    bankPresets.value = presets || []
  } catch (_) {}

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
        fints_login: data.fints_login || '',
        fints_pin: '',  // never echoed back from server
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

onUnmounted(() => {
  clearPoll()
})

function applyBankPreset() {
  const bank = bankPresets.value.find(b => b.name === selectedBankPreset.value)
  if (!bank) return
  if (bank.fints_url) form.fints_url = bank.fints_url
  if (bank.blz_example && !form.blz) form.blz = bank.blz_example
  if (!form.bank) form.bank = bank.name
}

function formatCurrency(value) {
  if (value == null) return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 }).format(value)
}

function formatDate(val) {
  if (!val) return ''
  const d = new Date(val)
  return d.toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function onUploadSuccess() {
  attachmentList.value?.reload()
}

async function handleSave() {
  saving.value = true
  error.value = null
  try {
    const payload = { ...form }
    // only send fints_pin if user typed something
    if (!payload.fints_pin) delete payload.fints_pin
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

// ---- FinTS Sync ----

async function startSync() {
  syncing.value = true
  syncError.value = null
  syncSuccess.value = null
  syncStatusLabel.value = 'Verbinde…'

  try {
    const res = await call('ktesis.api.fints.start_fints_sync', { name: props.name })
    syncJobId.value = res.job_id
    startPoll()
  } catch (e) {
    syncing.value = false
    syncError.value = e.message || 'Fehler beim Starten der Synchronisierung.'
  }
}

function startPoll() {
  pollCount = 0
  pollTimer = setInterval(pollStatus, 2000)
}

function clearPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollStatus() {
  if (!syncJobId.value) return

  pollCount++
  // If still "pending" after timeout, worker likely crashed before writing state
  if (pollCount > POLL_TIMEOUT_COUNT) {
    clearPoll()
    syncing.value = false
    syncError.value = 'Keine Antwort vom Worker. Bitte prüfen ob python-fints installiert ist und der Worker läuft.'
    return
  }

  try {
    const state = await call('ktesis.api.fints.get_fints_sync_status', { job_id: syncJobId.value })

    const statusLabels = {
      pending: 'Warte auf Start…',
      connecting: 'Verbinde mit Bank…',
      connected: 'Verbunden, rufe Konten ab…',
      fetching_transactions: 'Lade Buchungen…',
      tan_submitted: 'TAN gesendet, warte…',
    }

    syncStatusLabel.value = statusLabels[state.status] || state.status

    if (state.status === 'tan_required') {
      tanChallenge.value = state.challenge || ''
      tanChallengeLabel.value = state.challenge_label || 'TAN eingeben'
      tanInput.value = ''
      tanError.value = null
      showTanDialog.value = true
      syncStatusLabel.value = 'TAN erforderlich…'
    }

    if (state.status === 'completed') {
      clearPoll()
      syncing.value = false
      showTanDialog.value = false
      form.kontostand_live = state.balance
      form.kontostand_abgerufen_am = new Date().toISOString()
      syncSuccess.value = `Synchronisiert: ${formatCurrency(state.balance)}${state.transactions_count ? ` · ${state.transactions_count} Buchungen` : ''}`
    }

    if (state.status === 'partial') {
      clearPoll()
      syncing.value = false
      showTanDialog.value = false
      form.kontostand_live = state.balance
      syncSuccess.value = state.message || 'Kontostand gespeichert.'
    }

    if (state.status === 'error') {
      clearPoll()
      syncing.value = false
      showTanDialog.value = false
      syncError.value = state.message || 'Unbekannter Fehler.'
    }

    if (state.status === 'expired') {
      clearPoll()
      syncing.value = false
      syncError.value = 'Sitzung abgelaufen. Bitte erneut starten.'
    }
  } catch (_) {
    // ignore transient poll errors
  }
}

async function submitTan() {
  if (!tanInput.value) return
  tanSubmitting.value = true
  tanError.value = null
  try {
    await call('ktesis.api.fints.submit_tan', { job_id: syncJobId.value, tan: tanInput.value })
    showTanDialog.value = false
    syncStatusLabel.value = 'TAN gesendet, warte…'
  } catch (e) {
    tanError.value = e.message || 'Fehler beim Senden der TAN.'
  } finally {
    tanSubmitting.value = false
  }
}

function cancelSync() {
  clearPoll()
  syncing.value = false
  showTanDialog.value = false
  syncJobId.value = null
  syncStatusLabel.value = 'Verbinde…'
}
</script>
