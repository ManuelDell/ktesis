<template>
  <div class="fixed inset-0 flex flex-col overflow-hidden bg-surface-white" :data-theme="theme">
    <!-- Content area mit nativem iOS-Scroll -->
    <div class="flex-1 overflow-y-auto overscroll-auto" style="-webkit-overflow-scrolling: touch">
      <slot />
    </div>

    <!-- Bottom Tab Bar -->
    <nav class="shrink-0 bg-surface-white border-t border-outline-gray-2 pb-safe"
         :style="{ gridTemplateColumns: 'repeat(' + tabs.length + ', minmax(0, 1fr))' }"
         style="display: grid">
      <a
        v-for="tab in tabs"
        :key="tab.href"
        :href="tab.href"
        class="flex flex-col items-center justify-center py-3 gap-0.5 transition active:scale-95 active:bg-surface-gray-1"
        :class="tab.active ? 'text-ink-gray-9' : 'text-ink-gray-4'"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path :d="tab.icon" />
        </svg>
        <span class="text-[10px] leading-none font-medium">{{ tab.label }}</span>
      </a>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { currentPageName } from '../router.js'

const props = defineProps({
  theme: String,
})

const page = currentPageName

const ICONS = {
  home: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
  truck: 'M1 3h15v13H1z M16 8h4l3 3v5h-2 M5 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0 M15 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0',
  'file-text': 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
  home2: 'M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z',
  'credit-card': 'M1 10h22 M1 6a2 2 0 0 1 2-2h18a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V6z M1 14h22',
  'dollar-sign': 'M12 1v22 M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
  'bar-chart-2': 'M18 20V10 M12 20V4 M6 20v-6',
}

const tabs = computed(() => [
  { href: '#/', label: 'Home', icon: ICONS.home, active: page.value === 'Dashboard' },
  { href: '#/fahrzeuge', label: 'Fahrzeuge', icon: ICONS.truck, active: page.value === 'Fahrzeuge' },
  { href: '#/wohnungen', label: 'Wohnungen', icon: ICONS.home2, active: page.value === 'Wohnungen' },
  { href: '#/vertraege', label: 'Verträge', icon: ICONS['file-text'], active: page.value === 'Vertraege' },
  { href: '#/bankkonten', label: 'Konten', icon: ICONS['credit-card'], active: page.value === 'Bankkonten' },
])
</script>
