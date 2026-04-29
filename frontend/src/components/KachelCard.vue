<template>
  <div
    class="bg-white border border-outline-gray-2 rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow p-5"
  >
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-ink-gray-4">{{ label }}</p>
        <p class="text-2xl font-semibold mt-1" :class="valueClass">{{ value }}</p>
      </div>
      <FeatherIcon :name="icon" class="w-5 h-5 text-ink-gray-4" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  value: {
    type: [String, Number],
    default: '',
  },
  icon: {
    type: String,
    default: 'bar-chart-2',
  },
  type: {
    type: String,
    default: 'count',
  },
})

const valueClass = computed(() => {
  if (props.type === 'negative') return 'text-ink-red-4'
  return 'text-ink-gray-9'
})
</script>
