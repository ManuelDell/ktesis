<template>
  <!-- Sidebar -->
  <aside class="kt-sidebar" :class="{ 'is-collapsed': collapsed, 'is-open': mobileOpen }">

    <!-- Top: Brand + Collapse -->
    <div class="kt-sb-top">
      <a href="#/" class="kt-sb-brand" @click="$emit('close-mobile')">
        <div class="kt-sb-logo">
          <svg width="26" height="26" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="border-radius:6px;display:block;flex-shrink:0">
            <rect width="200" height="200" rx="44" ry="44" fill="#FAF3EA"/>
            <polygon points="20,200 20,95 100,40 180,95 180,200" fill="#B5451B"/>
            <polygon points="100,40 180,95 180,82 100,28" fill="#C07830"/>
            <rect x="48" y="68" width="20" height="32" fill="#B5451B"/>
            <text x="62" y="175" font-family="Georgia,serif" font-size="110" font-weight="700" fill="#FAF3EA">K</text>
          </svg>
        </div>
       <div v-if="!collapsed" class="kt-sb-brand-text">
          <span class="kt-sb-brand-name">Ktesis</span>
          
       </div>
     </a>

   </div>

   <!-- Navigation -->
   <nav class="kt-sb-nav">
     <div class="kt-sb-section">Ktesis</div>
     <NavItem href="#/" icon="home" label="Dashboard" :active="page === 'Dashboard'" :collapsed="collapsed" />
     <NavItem href="#/fahrzeuge" icon="truck" label="Fahrzeuge" :active="page === 'Fahrzeuge'" :collapsed="collapsed" />
     <NavItem href="#/wohnungen" icon="home" label="Wohnungen" :active="page === 'Wohnungen'" :collapsed="collapsed" />
     <NavItem href="#/vertraege" icon="file-text" label="Verträge" :active="page === 'Vertraege'" :collapsed="collapsed" />
     <NavItem href="#/darlehen" icon="dollar-sign" label="Darlehen" :active="page === 'Darlehen'" :collapsed="collapsed" />
    <NavItem href="#/bankkonten" icon="credit-card" label="Bankkonten" :active="page === 'Bankkonten'" :collapsed="collapsed" />
    <NavItem href="#/budget" icon="bar-chart-2" label="Budget" :active="page === 'Budget'" :collapsed="collapsed" />
    <NavItem href="#/einstellungen" icon="settings" label="Einstellungen" :active="page === 'Einstellungen'" :collapsed="collapsed" />
  </nav>

   <!-- Footer -->
   <div class="kt-sb-foot">
     <!-- Theme Toggle -->
     <button
       class="kt-sb-theme-btn"
       @click="$emit('toggle-theme')"
       :title="theme === 'dark' ? 'Hell-Modus' : 'Dunkel-Modus'"
     >
       <svg v-if="theme === 'dark'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
       <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
       <span v-if="!collapsed" style="margin-left:8px;font-size:12px">{{ theme === 'dark' ? 'Hell-Modus' : 'Dunkel-Modus' }}</span>
     </button>

     <!-- User -->
     <div class="kt-sb-user">
       <div class="kt-avatar kt-avatar-sm" :style="{ background: avatarColor, color: '#fff' }">{{ initials }}</div>
       <div v-if="!collapsed" class="kt-sb-user-text">
         <div class="kt-sb-user-name">{{ userName }}</div>
         <div class="kt-sb-user-role">Angemeldet</div>
       </div>
     </div>

     <!-- Logout -->
     <button
       class="kt-sb-logout"
       @click="$emit('logout')"
       :title="collapsed ? 'Abmelden' : ''"
     >
       <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
       <span v-if="!collapsed">Abmelden</span>
     </button>
   </div>
 </aside>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { currentPageName } from '../router.js'

const props = defineProps({
 collapsed: Boolean,
 mobileOpen: Boolean,
 theme: String,
})
const emit = defineEmits(['toggle-collapse', 'toggle-theme', 'logout', 'close-mobile'])

const page = currentPageName

const userName = computed(() => window.__KtesisBOOT?.user_name || window.__ktesis_user?.fullname || 'Nutzer')

const initials = computed(() => {
 const n = userName.value || ''
 return n.split(' ').map(x => x[0]).join('').toUpperCase().slice(0, 2) || 'N'
})

const AVATAR_COLORS = ['#3e4d78', '#1c2850', '#6e7ca6', '#d4a24c', '#8B5E3C', '#2563eb']
const avatarColor = computed(() => {
 const idx = (userName.value || 'N').charCodeAt(0) % AVATAR_COLORS.length
 return AVATAR_COLORS[idx]
})
  
  // --- NavItem as inline component ---
  const ICONS = {
home: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
truck: 'M1 3h15v13H1z M16 8h4l3 3v5h-2 M5 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0 M15 19a2 2 0 1 0 4 0 2 2 0 0 0-4 0',
'file-text': 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
'dollar-sign': 'M12 1v22 M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
'credit-card': 'M1 10h22 M1 6a2 2 0 0 1 2-2h18a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V6z M1 14h22',
    'bar-chart-2': 'M18 20V10 M12 20V4 M6 20v-6',
    settings: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z',
  }
  
  const NavItem = {
props: ['href', 'icon', 'label', 'active', 'collapsed', 'badge'],
setup(props) {
  return () => h('a', {
    href: props.href,
    class: ['kt-nav-item', props.active ? 'is-active' : ''],
    title: props.collapsed ? props.label : '',
  }, [
    h('svg', {
      width: 16, height: 16,
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      style: 'flex-shrink:0',
    }, [h('path', { d: ICONS[props.icon] || '' })]),
    !props.collapsed && h('span', props.label),
    !props.collapsed && props.badge && h('span', { class: 'kt-nav-badge' }, props.badge),
  ])
}
  }
  </script>
  