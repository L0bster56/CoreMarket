const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1'

const STORAGE_KEY = 'cm_auth'

interface StoredTokens {
  access_token: string
  refresh_token: string
}

export function getTokens(): StoredTokens | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw) as StoredTokens
  } catch {
    return null
  }
}

export function setTokens(tokens: StoredTokens): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
}

export function clearTokens(): void {
  localStorage.removeItem(STORAGE_KEY)
}

let refreshPromise: Promise<boolean> | null = null

async function doRefresh(): Promise<boolean> {
  const tokens = getTokens()
  if (!tokens?.refresh_token) return false
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh_token }),
    })
    if (!res.ok) return false
    const data = await res.json() as StoredTokens
    setTokens(data)
    return true
  } catch {
    return false
  } finally {
    refreshPromise = null
  }
}

function parseError(status: number, body: string): Error {
  try {
    const json = JSON.parse(body) as { detail?: string }
    if (json.detail) return new Error(json.detail)
  } catch {
    // not JSON
  }
  return new Error(body || `Ошибка ${status}`)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const tokens = getTokens()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined ?? {}),
  }
  if (tokens?.access_token) headers['Authorization'] = `Bearer ${tokens.access_token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    if (!refreshPromise) refreshPromise = doRefresh()
    const refreshed = await refreshPromise
    if (refreshed) {
      const newTokens = getTokens()
      const retryHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> | undefined ?? {}),
      }
      if (newTokens?.access_token) retryHeaders['Authorization'] = `Bearer ${newTokens.access_token}`
      const retry = await fetch(`${API_BASE}${path}`, { ...options, headers: retryHeaders })
      if (!retry.ok) throw parseError(retry.status, await retry.text())
      if (retry.status === 204) return undefined as T
      return retry.json() as Promise<T>
    }
    clearTokens()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) throw parseError(res.status, await res.text())
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  get:    <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
  post:   <T>(path: string, body: unknown)        => request<T>(path, { method: 'POST',   body: JSON.stringify(body) }),
  patch:  <T>(path: string, body: unknown)        => request<T>(path, { method: 'PATCH',  body: JSON.stringify(body) }),
  delete: <T>(path: string)                       => request<T>(path, { method: 'DELETE' }),

  postMultipart: async <T>(path: string, formData: FormData): Promise<T> => {
    const tokens = getTokens()
    const headers: Record<string, string> = {}
    if (tokens?.access_token) headers['Authorization'] = `Bearer ${tokens.access_token}`
    const res = await fetch(`${API_BASE}${path}`, { method: 'POST', headers, body: formData })
    if (!res.ok) throw parseError(res.status, await res.text())
    if (res.status === 204) return undefined as T
    return res.json() as Promise<T>
  },
}
