<template>
  <div class="p-5 max-w-2xl">
    <h2 class="text-3xl font-semibold text-ink-gray-9 mb-6">Einstellungen</h2>

    <!-- KI-Kategorisierung -->
    <div class="bg-surface-white border border-outline-gray-2 rounded-lg p-5 mb-5">
      <h3 class="text-lg font-semibold text-ink-gray-8 mb-1 flex items-center gap-2">
        <FeatherIcon name="cpu" class="w-5 h-5 text-ink-gray-5" />
        KI-Kategorisierung
      </h3>
      <p class="text-sm text-ink-gray-5 mb-4">
        Buchungstexte werden per KI-API kategorisiert. Es werden <strong>nur Buchungstexte</strong> uebertragen — keine Betraege, Kontonummern oder persoenliche Daten.
      </p>

      <div class="space-y-4">
        <div class="flex items-center gap-3">
          <input
            id="ki_aktiv"
            v-model="form.ki_aktiv"
            type="checkbox"
            class="w-4 h-4 rounded border-outline-gray-3 text-blue-600"
          />
          <label for="ki_aktiv" class="text-sm font-medium text-ink-gray-7">KI-Kategorisierung aktivieren</label>
        </div>

        <template v-if="form.ki_aktiv">
          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Anbieter</label>
            <select
              v-model="form.ki_anbieter"
              class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="onAnbieterChange"
            >
              <option value="opencode">OpenCode (Hermes)</option>
              <option value="openai">OpenAI</option>
              <option value="openrouter">OpenRouter</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">API URL</label>
            <input
              v-model="form.ki_api_url"
              type="text"
              class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://opencode.ai/zen/go/v1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">API Key</label>
            <input
              v-model="form.ki_api_key"
              type="password"
              class="w-full border border-outline-gray-2 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sk-..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-ink-gray-7 mb-1">Modell</label>
            <div class="flex gap-2">
              <select
                v-if="availableModels.length"
                v-model="form.ki_modell"
                class="flex-1 border border-outline-gray-2 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">— Modell wählen —</option>
                <option v-for="m in availableModels" :key="m" :value="m">{{ m }}</option>
              </select>
              <input
                v-else
                v-model="form.ki_modell"
                type="text"
                class="flex-1 border border-outline-gray-2 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                :placeholder="modelPlaceholder"
              />
              <Button variant="outline" theme="gray" :loading="loadingModels" @click="loadModels" title="Modelle von API laden">
                <FeatherIcon name="refresh-cw" class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </template>
      </div>

      <div class="flex items-center gap-3 mt-5">
        <Button variant="outline" theme="gray" :loading="testing" @click="testConnection">
          <span class="flex items-center gap-2">
            <FeatherIcon name="zap" class="w-4 h-4" />
            Verbindung testen
          </span>
        </Button>
        <Button variant="solid" theme="gray" :loading="saving" @click="save">
          <span class="flex items-center gap-2">
            <FeatherIcon name="save" class="w-4 h-4" />
            Speichern
          </span>
        </Button>
        <span v-if="saved" class="text-sm text-ink-green-4 flex items-center gap-1">
          <FeatherIcon name="check" class="w-4 h-4" />
          Gespeichert
        </span>
        <span v-if="testResult" class="text-sm" :class="testResult.startsWith('✓') ? 'text-ink-green-4' : 'text-ink-red-4'">{{ testResult }}</span>
        <span v-if="saveError" class="text-sm text-ink-red-4">{{ saveError }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { useApi } from '../composables/useApi'

const { call } = useApi()

const form = ref({
  ki_aktiv: false,
  ki_anbieter: 'opencode',
  ki_api_url: 'https://opencode.ai/zen/go/v1',
  ki_api_key: '',
  ki_modell: 'kimi-k2.6',
})

const saving = ref(false)
const saved = ref(false)
const saveError = ref(null)
const availableModels = ref([])
const loadingModels = ref(false)
const testing = ref(false)
const testResult = ref(null)

const ANBIETER_DEFAULTS = {
  opencode: { url: 'https://opencode.ai/zen/go/v1', modell: 'kimi-k2.6' },
  openai: { url: 'https://api.openai.com/v1', modell: 'gpt-4o-mini' },
  openrouter: { url: 'https://openrouter.ai/api/v1', modell: 'openai/gpt-4o-mini' },
}

const modelPlaceholder = computed(() => ANBIETER_DEFAULTS[form.value.ki_anbieter]?.modell || 'Modell-ID')

function onAnbieterChange() {
  const defaults = ANBIETER_DEFAULTS[form.value.ki_anbieter]
  if (defaults) {
    form.value.ki_api_url = defaults.url
    if (!form.value.ki_modell) form.value.ki_modell = defaults.modell
  }
}

onMounted(async () => {
  try {
    const doc = await call('ktesis.api.ai_assign.get_einstellungen')
    if (doc) {
      form.value.ki_aktiv = !!doc.ki_aktiv
      form.value.ki_anbieter = doc.ki_anbieter || 'opencode'
      form.value.ki_api_url = doc.ki_api_url || ANBIETER_DEFAULTS[doc.ki_anbieter || 'opencode']?.url || ''
      form.value.ki_modell = doc.ki_modell || ''
    }
  } catch (e) {
    // Doc doesn't exist yet, use defaults
  }
})

async function loadModels() {
  loadingModels.value = true
  availableModels.value = []
  try {
    const models = await call('ktesis.api.ai_assign.get_ki_models', {
      api_url: form.value.ki_api_url,
      api_key: form.value.ki_api_key,
    })
    availableModels.value = models || []
  } catch (e) {
    saveError.value = 'Modelle laden fehlgeschlagen: ' + (e.message || e)
  } finally {
    loadingModels.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  saveError.value = null
  try {
    const models = await call('ktesis.api.ai_assign.get_ki_models', {
      api_url: form.value.ki_api_url,
      api_key: form.value.ki_api_key,
    })
    testResult.value = `✓ Verbindung OK — ${(models || []).length} Modelle verfügbar`
    availableModels.value = models || []
  } catch (e) {
    testResult.value = '✗ ' + (e.message || 'Verbindung fehlgeschlagen')
  } finally {
    testing.value = false
  }
}

async function save() {
  saving.value = true
  saved.value = false
  saveError.value = null
  try {
    await call('ktesis.api.ai_assign.save_einstellungen', {
      ki_aktiv: form.value.ki_aktiv ? 1 : 0,
      ki_anbieter: form.value.ki_anbieter,
      ki_api_url: form.value.ki_api_url,
      ki_api_key: form.value.ki_api_key,
      ki_modell: form.value.ki_modell,
    })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) {
    saveError.value = e.message || 'Fehler beim Speichern'
  } finally {
    saving.value = false
  }
}
</script>
