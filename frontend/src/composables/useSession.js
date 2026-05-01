import { ref, computed } from 'vue'

const user = ref(null)
const loading = ref(true)

function getCsrf() {
  return window.frappe?.csrf_token || window.csrf_token || window['csrf_token'] || '' 
}

/**
 * Composable for Frappe session management.
 * Provides current user info, login state, logout capability.
 */
export function useSession() {
  async function fetchSession() {
    loading.value = true
    try {
      const res = await fetch('/api/method/frappe.auth.get_logged_user', {
        credentials: 'same-origin',
        headers: { 'X-Frappe-CSRF-Token': getCsrf() },
      })
      const data = await res.json()
      if (data.message && data.message !== 'Guest') {
        user.value = data.message
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * Log the current user out and redirect to Frappe login.
   */
  async function logout() {
    try {
      await fetch('/api/method/logout', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-Frappe-CSRF-Token': getCsrf() },
      })
    } catch {
      // ignore — navigation happens anyway
    }
    window.location.href = '/login?redirect-to=/ktesis'
  }

  const isLoggedIn = computed(() => !!user.value)

  return {
    user,
    loading,
    isLoggedIn,
    fetchSession,
    logout,
  }
}
