import { ref } from 'vue'

function getHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-Frappe-CSRF-Token': window.frappe?.csrf_token || window.csrf_token || '',
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try { const d = await res.json(); msg = d.exception || d.message || msg } catch {}
    throw new Error(msg)
  }
  const data = await res.json()
  return data
}

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  // Frappe whitelist method call (POST /api/method/...)
  async function call(method, params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/method/' + method, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(params),
      })
      const data = await handleResponse(res)
      return data.message
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // GET /api/resource/{doctype} — Liste holen
  async function list(doctype, { fields = ['*'], filters = [], limit = 100, orderBy = 'modified desc' } = {}) {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams({
        fields: JSON.stringify(fields),
        filters: JSON.stringify(filters),
        limit_page_length: limit,
        order_by: orderBy,
      })
      const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}?${params}`, {
        headers: getHeaders(),
      })
      const data = await handleResponse(res)
      return data.data || []
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // GET /api/resource/{doctype}/{name} — einzelnes Dokument
  async function get(doctype, name) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`, {
        headers: getHeaders(),
      })
      const data = await handleResponse(res)
      return data.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // POST /api/resource/{doctype} — neues Dokument anlegen
  async function create(doctype, doc) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ ...doc, doctype }),
      })
      const data = await handleResponse(res)
      return data.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // PUT /api/resource/{doctype}/{name} — Dokument aktualisieren
  async function update(doctype, name, doc) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(doc),
      })
      const data = await handleResponse(res)
      return data.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // DELETE /api/resource/{doctype}/{name}
  async function delete_(doctype, name) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`, {
        method: 'DELETE',
        headers: getHeaders(),
      })
      await handleResponse(res)
      return true
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return { loading, error, call, list, get, create, update, delete_ }
}
