<template>
  <div class="fixed inset-0 flex flex-col overflow-hidden bg-surface-white" :data-theme="theme">
    <!-- Content area -->
    <div class="flex-1 overflow-y-auto overscroll-contain" style="-webkit-overflow-scrolling: touch">
      <slot />
    </div>

    <!-- Bottom Tab Bar -->
    <nav class="shrink-0 bg-surface-white border-t border-outline-gray-2"
         style="padding-bottom: max(8px, env(safe-area-inset-bottom))">
      <div class="grid grid-cols-5">
        <a
          v-for="tab in mainTabs"
          :key="tab.href"
          :href="tab.href"
          class="flex flex-col items-center justify-center py-3.5 gap-1 transition-colors active:bg-surface-gray-1"
          :class="isActive(tab) ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path :d="tab.icon" />
          </svg>
          <span class="text-[10px] leading-none font-medium">{{ tab.label }}</span>
        </a>

        <!-- Expand button -->
        <button
          @click="navOpen = true"
          class="flex flex-col items-center justify-center py-3.5 gap-1 transition-colors active:bg-surface-gray-1"
          :class="isMoreActive ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
          </svg>
          <span class="text-[10px] leading-none font-medium">Mehr</span>
        </button>
      </div>
    </nav>

    <!-- Fullscreen Nav Overlay -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      leave-active-class="transition duration-200 ease-in"
    >
      <div v-if="navOpen" class="fixed inset-0 z-50 flex flex-col justify-end">
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/40"
          @click="navOpen = false"
        />

        <!-- Bottom Sheet -->
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="translate-y-full"
          enter-to-class="translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="translate-y-0"
          leave-to-class="translate-y-full"
        >
          <div v-if="navOpen" class="relative bg-surface-white rounded-t-2xl shadow-2xl"
               style="padding-bottom: max(12px, env(safe-area-inset-bottom))">

            <!-- Drag handle + Header -->
            <div class="flex justify-center pt-3 pb-1">
              <div class="w-10 h-1.5 rounded-full bg-surface-gray-3" />
            </div>
            <div class="flex items-center justify-between px-5 py-3">
              <span class="text-sm font-semibold text-ink-gray-7">Navigation</span>
              <button
                @click="navOpen = false"
                class="p-1.5 rounded-lg active:bg-surface-gray-2 text-ink-gray-4"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- All pages grid -->
            <div class="grid grid-cols-4 gap-3 px-5 pb-6">
              <a
                v-for="tab in allTabs"
                :key="tab.href"
                :href="tab.href"
                @click="navOpen = false"
                class="flex flex-col items-center gap-2 py-2"
              >
                <div
                  class="w-14 h-14 rounded-2xl flex items-center justify-center transition-colors active:scale-95"
                  :class="isActive(tab)
                    ? 'bg-ink-gray-9 text-surface-white'
                    : 'bg-surface-gray-1 text-ink-gray-7 active:bg-surface-gray-2'"
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                       stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path :d="tab.icon" />
                  </svg>
                </div>
                <span
                  class="text-xs leading-tight text-center font-medium"
                  :class="isActive(tab) ? 'text-ink-gray-9' : 'text-ink-gray-5'"
                >{{ tab.label }}</span>
              </a>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { currentPageName } from '../router.js'

const props = defineProps({ theme: String })

const navOpen = ref(false)
const page = currentPageName

const ICONS = {
  home:         'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
  truck:        'M1 3h15v13H1z M16 8h4l3 3v5h-2 M5 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0 M15 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0',
  building:     'M3 3h7v18H3z M14 3h7v18h-7z M7 8h.01M7 12h.01M7 16h.01M17 8h.01M17 12h.01M17 16h.01',
  'file-text':  'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
  'dollar-sign':'M12 1v22 M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
  'credit-card':'M1 10h22 M1 6a2 2 0 0 1 2-2h18a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V6z M1 14h22',
  'bar-chart':  'M18 20V10 M12 20V4 M6 20v-6',
  settings:     'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z',
}

const PAGE_MAP = {
  Dashboard:    'Dashboard',
  Fahrzeuge:    'Fahrzeuge',
  Wohnungen:    'Wohnungen',
  Vertraege:    'Vertraege',
  Darlehen:     'Darlehen',
  Bankkonten:   'Bankkonten',
  Budget:       'Budget',
  Einstellungen:'Einstellungen',
}

const allTabs = [
  { href: '#/',             label: 'Dashboard',   icon: ICONS.home,          page: 'Dashboard' },
  { href: '#/fahrzeuge',    label: 'Fahrzeuge',   icon: ICONS.truck,         page: 'Fahrzeuge' },
  { href: '#/wohnungen',    label: 'Wohnungen',   icon: ICONS.building,      page: 'Wohnungen' },
  { href: '#/vertraege',    label: 'Verträge',    icon: ICONS['file-text'],  page: 'Vertraege' },
  { href: '#/darlehen',     label: 'Darlehen',    icon: ICONS['dollar-sign'],page: 'Darlehen' },
  { href: '#/bankkonten',   label: 'Konten',      icon: ICONS['credit-card'],page: 'Bankkonten' },
  { href: '#/budget',       label: 'Budget',      icon: ICONS['bar-chart'],  page: 'Budget' },
  { href: '#/einstellungen',label: 'Einst.',      icon: ICONS.settings,      page: 'Einstellungen' },
]

const mainTabs = allTabs.slice(0, 4)

const isActive = (tab) => page.value === tab.page
const isMoreActive = computed(() =>
  !mainTabs.some(t => t.page === page.value)
)
</script>
