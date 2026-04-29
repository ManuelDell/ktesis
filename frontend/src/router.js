import { ref, computed, shallowRef } from 'vue'

// Lazy-loaded page components
const pages = {
    Dashboard:     () => import('./views/Dashboard.vue'),
    Fahrzeuge:     () => import('./views/Fahrzeuge.vue'),
    Wohnungen:     () => import('./views/Wohnungen.vue'),
    Vertraege:     () => import('./views/Vertraege.vue'),
    Darlehen:      () => import('./views/Darlehen.vue'),
    Bankkonten:    () => import('./views/Bankkonten.vue'),
}

// Exact routes
const routeMap = {
    '#/':              'Dashboard',
    '#/fahrzeuge':     'Fahrzeuge',
    '#/wohnungen':     'Wohnungen',
    '#/vertraege':     'Vertraege',
    '#/darlehen':      'Darlehen',
    '#/bankkonten':    'Bankkonten',
}

// Dynamic routes: pattern regex → page name
const dynamicRoutes = [
]

const currentHash = ref(window.location.hash || '#/')
const currentPageName = computed(() => {
    const exact = routeMap[currentHash.value]
    if (exact) return exact
    for (const r of dynamicRoutes) {
        if (r.pattern.test(currentHash.value)) return r.page
    }
    return 'Dashboard'
})
const currentComponent = shallowRef(null)
const currentRouteParams = ref({})

// Route guards (simple)
const beforeEachGuards = []

export function onBeforeEach(fn) {
    beforeEachGuards.push(fn)
}

function resolveRoute() {
    const hash = window.location.hash || '#/'
    currentHash.value = hash

    // Extract params from dynamic routes
    let pageName = routeMap[hash]
    let params = {}
    if (!pageName) {
        for (const r of dynamicRoutes) {
            const m = hash.match(r.pattern)
            if (m) {
                pageName = r.page
                params[r.param] = decodeURIComponent(m[1])
                break
            }
        }
    }
    pageName = pageName || 'Dashboard'
    currentRouteParams.value = params

    // Run guards
    for (const guard of beforeEachGuards) {
        const result = guard({ to: hash, name: pageName, params })
        if (result === false) return
        if (typeof result === 'string') {
            navigate(result)
            return
        }
    }

    const loader = pages[pageName] || pages.Dashboard
    loader().then(mod => {
        currentComponent.value = mod.default
    }).catch(() => {
        currentComponent.value = null
    })
}

export function navigate(path) {
    if (typeof path !== 'string') {
        console.warn('[router] navigate expected string, got', typeof path, path)
        path = String(path || '')
    }
    if (!path.startsWith('#')) path = '#' + path
    window.location.hash = path
}

export function getRouteParam(key) {
    return currentRouteParams.value[key]
}

export function getRouteParams() {
    return { ...currentRouteParams.value }
}

// Listen to hash changes
window.addEventListener('hashchange', resolveRoute)

// Initial resolve
resolveRoute()

export { currentHash, currentPageName, currentComponent }
