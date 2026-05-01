<template>
  <div v-if="files.length > 0" class="space-y-2 mt-4">
    <h4 class="text-sm font-medium text-ink-gray-7 mb-2">Anhänge ({{ files.length }})</h4>
    <ul class="divide-y divide-outline-gray-1 border border-outline-gray-2 rounded-lg">
      <li
        v-for="file in files"
        :key="file.name"
        class="flex items-center justify-between px-4 py-3 hover:bg-surface-gray-1"
      >
        <div class="flex items-center gap-3 min-w-0">
          <FeatherIcon :name="getFileIcon(file.file_name)" class="w-5 h-5 text-ink-gray-4 shrink-0" />
          <div class="min-w-0">
            <p class="text-sm font-medium text-ink-gray-9 truncate">{{ file.file_name }}</p>
            <p class="text-xs text-ink-gray-4">
              {{ formatFileSize(file.file_size) }} · {{ formatDate(file.creation) }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2 shrink-0 ml-3">
          <a
            :href="file.file_url"
            target="_blank"
            class="text-ink-gray-5 hover:text-ink-gray-8 transition-colors p-1 rounded hover:bg-surface-gray-2"
            title="Öffnen"
          >
            <FeatherIcon name="external-link" class="w-4 h-4" />
          </a>
          <button
            @click="deleteFile(file.name)"
            class="text-ink-gray-5 hover:text-ink-red-4 transition-colors p-1 rounded hover:bg-surface-red-1"
            title="Löschen"
          >
            <FeatherIcon name="trash-2" class="w-4 h-4" />
          </button>
        </div>
      </li>
    </ul>
  </div>
  <div v-else-if="!loading" class="mt-4 text-sm text-ink-gray-4">
    Keine Anhänge vorhanden.
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  doctype: { type: String, required: true },
  docname: { type: String, required: true },
})

const files = ref([])
const loading = ref(false)

function getFileIcon(filename) {
  const ext = filename.split('.').pop()?.toLowerCase()
  const icons = {
    pdf: 'file-text',
    jpg: 'image',
    jpeg: 'image',
    png: 'image',
    gif: 'image',
    doc: 'file',
    docx: 'file',
    xls: 'grid',
    xlsx: 'grid',
    zip: 'archive',
    txt: 'file',
  }
  return icons[ext] || 'paperclip'
}

function formatFileSize(bytes) {
  if (!bytes) return ''
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('de-DE')
}

async function loadAttachments() {
  loading.value = true
  try {
    const res = await fetch(`/api/method/ktesis.api.attachments.get_attachments?doctype=${encodeURIComponent(props.doctype)}&docname=${encodeURIComponent(props.docname)}`)
    const data = await res.json()
    files.value = data.message || []
  } catch (e) {
    console.error('Fehler beim Laden der Anhänge:', e)
    files.value = []
  } finally {
    loading.value = false
  }
}

async function deleteFile(name) {
  if (!confirm('Anhang wirklich löschen?')) return
  try {
    const res = await fetch('/api/method/ktesis.api.attachments.delete_attachment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.frappe?.csrf_token || window.csrf_token || ''
      },
      body: JSON.stringify({ name }),
    })
    const data = await res.json()
    if (data.message?.status === 'ok') {
      await loadAttachments()
    } else {
      alert('Fehler beim Löschen')
    }
  } catch (e) {
    console.error('Fehler beim Löschen:', e)
    alert('Fehler beim Löschen')
  }
}

onMounted(loadAttachments)

watch(() => props.docname, loadAttachments)

defineExpose({ reload: loadAttachments })
</script>
