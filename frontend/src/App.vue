<template>
  <!-- Mobile Layout (< 640px) -->
  <MobileLayout v-if="isMobile" :theme="theme">
    <div v-if="sessionLoading" class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
      <div>
        <div class="w-8 h-8 rounded-full border-2 border-outline-gray-2 border-t-outline-gray-9 animate-spin mx-auto mb-3"></div>
        <p style="font-size:13px;margin:0">Sitzung wird geprüft…</p>
      </div>
    </div>
    <div v-else-if="!isLoggedIn" class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
      <div>
        <p style="font-size:15px;margin:0 0 12px">Sie sind nicht angemeldet.</p>
        <button class="kt-btn kt-btn-primary" @click="goToLogin">Zum Login</button>
      </div>
    </div>
    <component :is="currentComponent" v-else-if="currentComponent" />
    <div v-else class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
      <div>
        <div class="w-8 h-8 rounded-full border-2 border-outline-gray-2 border-t-outline-gray-9 animate-spin mx-auto mb-3"></div>
        <p style="font-size:13px;margin:0">Wird geladen…</p>
      </div>
    </div>
  </MobileLayout>

  <!-- Desktop Layout (>= 640px) -->
  <div v-else class="kt-app" :class="{ 'is-collapsed': sidebarCollapsed }" :data-theme="theme">
    <!-- Mobile backdrop (für Tablets 640-768px) -->
    <div v-if="mobileOpen" class="fixed inset-0 z-40 bg-black/50 md:hidden" @click="mobileOpen = false" />
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :mobileOpen="mobileOpen"
      :theme="theme"
      @toggle-collapse="handleToggleCollapse"
      @toggle-theme="toggleTheme"
      @logout="handleLogout"
      @close-mobile="mobileOpen = false"
    />
    <div class="kt-main-wrap">
      <AppTopbar :title="pageTitle" :collapsed="sidebarCollapsed" @toggle-collapse="handleToggleCollapse" />
      <div class="kt-content">
        <div v-if="sessionLoading" class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
          <div>
            <div class="w-8 h-8 rounded-full border-2 border-outline-gray-2 border-t-outline-gray-9 animate-spin mx-auto mb-3"></div>
            <p style="font-size:13px;margin:0">Sitzung wird geprüft…</p>
          </div>
        </div>
        <div v-else-if="!isLoggedIn" class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
          <div>
            <p style="font-size:15px;margin:0 0 12px">Sie sind nicht angemeldet.</p>
            <button class="kt-btn kt-btn-primary" @click="goToLogin">Zum Login</button>
          </div>
        </div>
        <component :is="currentComponent" v-else-if="currentComponent" />
        <div v-else class="kt-screen kt-screen-enter text-center text-ink-gray-4" style="display:flex;align-items:center;justify-content:center;min-height:300px;">
          <div>
            <div class="w-8 h-8 rounded-full border-2 border-outline-gray-2 border-t-outline-gray-9 animate-spin mx-auto mb-3"></div>
            <p style="font-size:13px;margin:0">Wird geladen…</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import AppTopbar from './components/AppTopbar.vue'
import MobileLayout from './components/MobileLayout.vue'
import { currentComponent, currentPageName } from './router.js'
import { useSession } from './composables/useSession.js'

const { user, loading: sessionLoading, isLoggedIn, fetchSession, logout } = useSession()

const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const theme = ref(localStorage.getItem('kt-theme') || 'light')
const isMobile = ref(window.innerWidth < 640)

const pageTitle = computed(() => {
  const map = {
    Dashboard: 'Dashboard',
    Fahrzeuge: 'Fahrzeuge',
    Wohnungen: 'Wohnungen',
    Vertraege: 'Verträge',
    Darlehen: 'Darlehen',
    Bankkonten: 'Bankkonten',
  }
  return map[currentPageName.value] || 'Ktesis'
})

function handleToggleCollapse() {
  if (window.innerWidth < 768) {
    mobileOpen.value = !mobileOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('kt-theme', theme.value)
}

function handleLogout() {
  logout()
}

function goToLogin() {
  window.location.href = '/login?redirect-to=/ktesis'
}

onMounted(() => {
  fetchSession()
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 640
  })
})

watch(currentPageName, () => { mobileOpen.value = false })
</script>

<style>
@keyframes spin { to { transform: rotate(360deg); } }
</style>
