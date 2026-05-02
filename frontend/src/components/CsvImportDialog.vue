<template>
  <Dialog
    :options="{ title: `Kontoauszug importieren — ${bankkontoBezeichnung}`, size: '3xl' }"
    :modelValue="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <template #body>
      <div class="p-5 space-y-5">

        <!-- Schritt 1: Datei auswählen -->
        <div v-if="step === 1">
          <!-- Bankkonto auswählen -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-ink-gray-7 mb-2">Bankkonto</label>
            <select
              v-model="selectedBankkonto"
              class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="" disabled>— Konto wählen —</option>
              <option v-for="k in bankkontoList" :key="k.name" :value="k.name">
                {{ k.bezeichnung || k.name }} {{ k.iban ? '· ' + k.iban : '' }}
              </option>
            </select>
          </div>

          <label class="block text-sm font-medium text-ink-gray-7 mb-2">CSV-Datei auswählen</label>
          <div
            class="border-2 border-dashed border-outline-gray-3 rounded-lg p-8 text-center cursor-pointer hover:border-outline-gray-5 transition-colors"
            @click="$refs.fileInput.click()"
            @dragover.prevent
            @drop.prevent="onDrop"
          >
            <FeatherIcon name="upload-cloud" class="w-10 h-10 mx-auto text-ink-gray-4 mb-2" />
            <p class="text-sm text-ink-gray-5">
              CSV hier ablegen oder <span class="text-ink-gray-8 font-medium underline">auswählen</span>
            </p>
            <p class="text-xs text-ink-gray-4 mt-1">
              DKB · Sparkasse · ING · Comdirect · Commerzbank · Deutsche Bank · N26 · Trade Republic
            </p>
          </div>
          <input ref="fileInput" type="file" accept=".csv" class="hidden" @change="onFileSelected" />
          <p v-if="fileError" class="mt-2 text-sm text-ink-red-4">{{ fileError }}</p>
          <div v-if="loading" class="mt-3 text-sm text-ink-gray-5 text-center">Lade Vorschau…</div>
        </div>

        <!-- Schritt 2: Vorschau-Tabelle -->
        <div v-if="step === 2">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-ink-gray-7">Vorschau</span>
              <Badge theme="blue" variant="subtle" size="sm">{{ detectedFormat?.toUpperCase() }}</Badge>
              <span class="text-xs text-ink-gray-4">
                {{ newRows.length }} neu · {{ dupRows.length }} Duplikate
              </span>
            </div>
            <button @click="reset" class="text-xs text-ink-gray-5 hover:text-ink-gray-8">Andere Datei</button>
          </div>

          <div class="border border-outline-gray-2 rounded-lg overflow-auto max-h-96 mb-4">
            <table class="w-full text-xs">
              <thead class="bg-surface-gray-1 sticky top-0">
                <tr>
                  <th class="text-left py-2 px-3 font-medium text-ink-gray-5 whitespace-nowrap">Datum</th>
                  <th class="text-left py-2 px-3 font-medium text-ink-gray-5">Buchungstext</th>
                  <th class="text-right py-2 px-3 font-medium text-ink-gray-5 whitespace-nowrap">Betrag</th>
                  <th class="text-left py-2 px-3 font-medium text-ink-gray-5 whitespace-nowrap">Budgetposten</th>
                  <th class="text-center py-2 px-3 font-medium text-ink-gray-5">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, i) in allRows"
                  :key="i"
                  class="border-t border-outline-gray-1"
                  :class="row.duplicate ? 'opacity-40 bg-surface-gray-1' : ''"
                >
                  <td class="py-1.5 px-3 whitespace-nowrap text-ink-gray-6">{{ formatDate(row.datum) }}</td>
                  <td class="py-1.5 px-3 max-w-xs truncate text-ink-gray-7">{{ row.buchungstext }}</td>
                  <td class="py-1.5 px-3 text-right font-medium whitespace-nowrap"
                    :class="row.betrag >= 0 ? 'text-ink-green-3' : 'text-ink-red-4'">
                    {{ formatCurrency(row.betrag) }}
                  </td>
                  <td class="py-1.5 px-3">
                    <select
                      v-if="!row.duplicate"
                      v-model="row.budgetposten"
                      class="border border-outline-gray-2 rounded px-2 py-0.5 text-xs bg-white w-full max-w-[140px]"
                    >
                      <option value="">— kein —</option>
                      <option v-for="bp in budgetposten" :key="bp.name" :value="bp.name">{{ bp.kategorie }}</option>
                    </select>
                    <span v-else class="text-ink-gray-4">—</span>
                  </td>
                  <td class="py-1.5 px-3 text-center">
                    <Badge v-if="row.duplicate" theme="gray" variant="subtle" size="sm">Duplikat</Badge>
                    <Badge v-else theme="green" variant="subtle" size="sm">Neu</Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex justify-end gap-3">
            <Button variant="outline" theme="gray" @click="reset">Abbrechen</Button>
            <Button variant="solid" theme="gray" :loading="importing" :disabled="!newRows.length || !selectedBankkonto" @click="doImport">
              <span class="flex items-center gap-2 whitespace-nowrap">
                <FeatherIcon name="download" class="w-4 h-4" />
                {{ newRows.length }} Buchungen importieren
              </span>
            </Button>
          </div>
        </div>

        <!-- Schritt 3: Ergebnis -->
        <div v-if="step === 3 && result">
          <div class="rounded-lg p-4 space-y-3"
            :class="result.errors?.length ? 'bg-surface-yellow-1 border border-outline-yellow-2' : 'bg-surface-green-1 border border-outline-green-2'">
            <div class="flex items-center gap-3">
              <FeatherIcon
                :name="result.errors?.length ? 'alert-triangle' : 'check-circle'"
                class="w-6 h-6"
                :class="result.errors?.length ? 'text-ink-yellow-3' : 'text-ink-green-3'"
              />
              <div>
                <p class="font-semibold text-ink-gray-9">Import abgeschlossen</p>
                <p class="text-sm text-ink-gray-6">
                  {{ result.imported }} neu importiert · {{ result.duplicates }} Duplikate übersprungen
                </p>
              </div>
            </div>
            <ul v-if="result.errors?.length" class="text-xs text-ink-yellow-3 space-y-1 pl-9">
              <li v-for="(err, i) in result.errors" :key="i">{{ err }}</li>
            </ul>
          </div>
          <div class="flex justify-end gap-3 mt-4">
            <Button variant="outline" theme="gray" @click="reset">Weiterer Import</Button>
            <Button variant="solid" theme="gray" @click="done">Fertig</Button>
          </div>
        </div>

      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'

const props = defineProps({
  modelValue: Boolean,
  bankkonto: { type: String, required: true },
  bankkontoBezeichnung: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'imported'])

const { call, list } = useApi()

const fileInput = ref(null)
const fileError = ref(null)
const step = ref(1)
const allRows = ref([])
const detectedFormat = ref(null)
const importing = ref(false)
const loading = ref(false)
const result = ref(null)
const budgetposten = ref([])
const bankkontoList = ref([])
const selectedBankkonto = ref(props.bankkonto || '')
const effectiveBankkonto = computed(() => selectedBankkonto.value || props.bankkonto || '')

const newRows = computed(() => allRows.value.filter(r => !r.duplicate))
const dupRows = computed(() => allRows.value.filter(r => r.duplicate))

onMounted(async () => {
  bankkontoList.value = await list('Bankkonto', { fields: ['name', 'bezeichnung', 'iban'], limit: 50 }) || []
  if (!selectedBankkonto.value && bankkontoList.value.length === 1) {
    selectedBankkonto.value = bankkontoList.value[0].name
  }
  budgetposten.value = await list('Budgetposten', { fields: ['name', 'kategorie'], limit: 50 }) || []
})

function reset() {
  step.value = 1
  allRows.value = []
  detectedFormat.value = null
  result.value = null
  fileError.value = null
  selectedBankkonto.value = props.bankkonto || ''
  if (fileInput.value) fileInput.value.value = ''
}

function done() {
  emit('imported')
  emit('update:modelValue', false)
  reset()
}

function onDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) processFile(file)
}

function onFileSelected(e) {
  const file = e.target.files[0]
  if (file) processFile(file)
}

function processFile(file) {
  fileError.value = null
  loading.value = true

  const tryRead = (encoding) => new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = reject
    reader.readAsText(file, encoding)
  })

  ;(async () => {
    try {
      let content = await tryRead('UTF-8')
      if (content.includes('\uFFFD')) {
        content = await tryRead('ISO-8859-1')
      }
      const res = await call('ktesis.api.csv_import.preview_csv', {
        bankkonto: effectiveBankkonto.value,
        csv_content: content,
      })
      allRows.value = res.rows || []
      detectedFormat.value = res.format
      if (!allRows.value.length) {
        fileError.value = 'Keine gültigen Zeilen gefunden.'
      } else {
        step.value = 2
      }
    } catch (err) {
      fileError.value = err.message || 'Fehler beim Lesen der Datei.'
    } finally {
      loading.value = false
    }
  })()
}

async function doImport() {
  importing.value = true
  try {
    const res = await call('ktesis.api.csv_import.import_bankbuchungen_rows', {
      bankkonto: effectiveBankkonto.value,
      rows: JSON.stringify(allRows.value),
    })
    result.value = res
    step.value = 3
  } catch (err) {
    fileError.value = err.message || 'Importfehler.'
  } finally {
    importing.value = false
  }
}

function formatCurrency(value) {
  if (value == null) return '—'
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(val) {
  if (!val) return '—'
  return new Date(val).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>