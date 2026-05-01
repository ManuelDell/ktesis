<template>
  <Dialog
    :options="{ title: `Kontoauszug importieren — ${bankkontoBezeichnung}`, size: 'xl' }"
    :modelValue="modelValue"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <template #body>
      <div class="p-5 space-y-5">

        <!-- Step 1: File picker -->
        <div v-if="!previewRows.length && !result">
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">CSV-Datei auswählen</label>
          <div
            class="border-2 border-dashed border-outline-gray-3 rounded-lg p-8 text-center cursor-pointer hover:border-outline-gray-5 transition-colors"
            @click="$refs.fileInput.click()"
            @dragover.prevent
            @drop.prevent="onDrop"
          >
            <FeatherIcon name="upload-cloud" class="w-10 h-10 mx-auto text-ink-gray-4 mb-2" />
            <p class="text-sm text-ink-gray-5">CSV hier ablegen oder <span class="text-ink-gray-8 font-medium underline">auswählen</span></p>
            <p class="text-xs text-ink-gray-4 mt-1">DKB, Sparkasse, ING — automatische Erkennung</p>
          </div>
          <input ref="fileInput" type="file" accept=".csv" class="hidden" @change="onFileSelected" />
          <p v-if="fileError" class="mt-2 text-sm text-ink-red-4">{{ fileError }}</p>
        </div>

        <!-- Step 2: Preview -->
        <div v-if="previewRows.length && !result">
          <div class="flex items-center justify-between mb-3">
            <div>
              <span class="text-sm font-medium text-ink-gray-7">Vorschau</span>
              <Badge theme="blue" variant="subtle" size="sm" class="ml-2">{{ detectedFormat?.toUpperCase() }}</Badge>
            </div>
            <button @click="reset" class="text-xs text-ink-gray-5 hover:text-ink-gray-8">Andere Datei wählen</button>
          </div>
          <div class="border border-outline-gray-2 rounded-lg overflow-hidden mb-4">
            <table class="w-full text-sm">
              <thead class="bg-surface-gray-1">
                <tr>
                  <th class="text-left py-2 px-3 font-medium text-ink-gray-5">Datum</th>
                  <th class="text-left py-2 px-3 font-medium text-ink-gray-5">Buchungstext</th>
                  <th class="text-right py-2 px-3 font-medium text-ink-gray-5">Betrag</th>
                  <th class="text-center py-2 px-3 font-medium text-ink-gray-5">Typ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in previewRows" :key="i" class="border-t border-outline-gray-1">
                  <td class="py-2 px-3">{{ formatDate(row.datum) }}</td>
                  <td class="py-2 px-3 max-w-xs truncate">{{ row.buchungstext }}</td>
                  <td class="py-2 px-3 text-right font-medium" :class="row.kategorie === 'Eingang' ? 'text-ink-green-3' : 'text-ink-red-4'">
                    {{ formatCurrency(row.betrag) }}
                  </td>
                  <td class="py-2 px-3 text-center">
                    <Badge :theme="row.kategorie === 'Eingang' ? 'green' : 'red'" variant="subtle" size="sm">
                      {{ row.kategorie }}
                    </Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-xs text-ink-gray-5 mb-4">Zeigt die ersten 5 Zeilen. Der vollständige Import folgt nach Bestätigung.</p>

          <div class="flex justify-end gap-3">
            <Button variant="outline" theme="gray" @click="reset">Abbrechen</Button>
            <Button variant="solid" theme="gray" :loading="importing" @click="doImport">
              <FeatherIcon name="download" class="w-4 h-4 mr-2" />
              Jetzt importieren
            </Button>
          </div>
        </div>

        <!-- Step 3: Result -->
        <div v-if="result">
          <div class="rounded-lg p-4 space-y-3" :class="result.errors?.length ? 'bg-surface-yellow-1 border border-outline-yellow-2' : 'bg-surface-green-1 border border-outline-green-2'">
            <div class="flex items-center gap-3">
              <FeatherIcon :name="result.errors?.length ? 'alert-triangle' : 'check-circle'" class="w-6 h-6" :class="result.errors?.length ? 'text-ink-yellow-3' : 'text-ink-green-3'" />
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
            <Button variant="outline" theme="gray" @click="reset">Weiteren Import</Button>
            <Button variant="solid" theme="gray" @click="done">Fertig</Button>
          </div>
        </div>

      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'

const props = defineProps({
  modelValue: Boolean,
  bankkonto: { type: String, required: true },
  bankkontoBezeichnung: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'imported'])

const { call } = useApi()

const fileInput = ref(null)
const fileError = ref(null)
const previewRows = ref([])
const detectedFormat = ref(null)
const importing = ref(false)
const result = ref(null)
let csvContent = null

function reset() {
  previewRows.value = []
  detectedFormat.value = null
  result.value = null
  fileError.value = null
  csvContent = null
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
  const reader = new FileReader()
  reader.onload = async (e) => {
    csvContent = e.target.result
    try {
      const res = await call('ktesis.api.csv_import.preview_csv', {
        bankkonto: props.bankkonto,
        csv_content: csvContent,
      })
      previewRows.value = res.rows || []
      detectedFormat.value = res.format
      if (!previewRows.value.length) {
        fileError.value = 'Keine gültigen Zeilen gefunden. Format prüfen.'
      }
    } catch (err) {
      fileError.value = err.message || 'Fehler beim Lesen der Datei.'
    }
  }
  reader.readAsText(file)
}

async function doImport() {
  if (!csvContent) return
  importing.value = true
  try {
    const res = await call('ktesis.api.csv_import.import_bankbuchungen', {
      bankkonto: props.bankkonto,
      csv_content: csvContent,
    })
    result.value = res
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
  const d = new Date(val)
  return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>
