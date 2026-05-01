import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  async function call(method, params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/method/' + method, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || window.csrf_token || ''
        },
        body: JSON.stringify(params),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      return data.message
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading, error, call }
}
