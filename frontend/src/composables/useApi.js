const API_BASE = ''

function getCsrf() {
  return window.csrf_token || ''
}

async function api(method, url, body = null) {
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': getCsrf(),
    },
    credentials: 'same-origin',
  }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(API_BASE + url, opts)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  const data = await res.json()
  return data.data || data.message || data
}

export function useApi() {
  const list = (doctype, fields = ['*'], filters = [], limit = 100) => {
    const params = new URLSearchParams()
    params.append('fields', JSON.stringify(fields))
    if (filters.length) params.append('filters', JSON.stringify(filters))
    params.append('limit', String(limit))
    return api('GET', `/api/resource/${doctype}?${params.toString()}`)
  }

  const get = (doctype, name) => api('GET', `/api/resource/${doctype}/${name}`)

  const count = (doctype, filters = []) => {
    const params = new URLSearchParams()
    if (filters.length) params.append('filters', JSON.stringify(filters))
    return api('GET', `/api/resource/${doctype}?${params.toString()}`).then(r => r.length)
  }

  const create = (doctype, data) =>
    api('POST', `/api/resource/${doctype}`, data)

  const update = (doctype, name, data) =>
    api('PUT', `/api/resource/${doctype}/${name}`, data)

  const delete_ = (doctype, name) =>
    api('DELETE', `/api/resource/${doctype}/${name}`)

  const call = (method, args = {}) =>
    api('POST', `/api/method/${method}`, args)

  return { list, get, count, create, update, delete_, call }
}
