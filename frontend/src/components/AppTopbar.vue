<template>
  <header class="kt-topbar">
    <div class="kt-topbar-left">
      <!-- Collapse toggle (hamburger) -->
      <button class="kt-icon-btn kt-topbar-toggle" @click="$emit('toggle-collapse')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </Button>

      <!-- Page title -->
      <h1 class="kt-topbar-title">{{ title }}</h1>
    </div>

    <div class="kt-topbar-right">
      <div class="kt-topbar-divider" />
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { currentPageName } from '../router.js'

defineProps({
  title: String,
  collapsed: Boolean,
})
defineEmits(['toggle-collapse'])

const page = currentPageName
</script>
