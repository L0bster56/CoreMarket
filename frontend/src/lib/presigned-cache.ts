import { getPresignedUrls } from '@/services/storage'

interface CacheEntry {
  url: string
  expiresAt: number
}

const _cache = new Map<string, CacheEntry>()
const EXPIRY_BUFFER_MS = 5 * 60 * 1000

export async function getCachedOrFetch(
  keys: string[],
  expiresIn = 3600,
): Promise<Record<string, string>> {
  if (keys.length === 0) return {}

  const now = Date.now()
  const result: Record<string, string> = {}
  const stale: string[] = []

  for (const key of keys) {
    const entry = _cache.get(key)
    if (entry && entry.expiresAt - now > EXPIRY_BUFFER_MS) {
      result[key] = entry.url
    } else {
      stale.push(key)
    }
  }

  if (stale.length > 0) {
    const fresh = await getPresignedUrls(stale, expiresIn)
    const expiresAt = now + expiresIn * 1000
    for (const [k, url] of Object.entries(fresh)) {
      _cache.set(k, { url, expiresAt })
      result[k] = url
    }
  }

  return result
}

export function resolveImageUrl(key: string | null | undefined): string | undefined {
  if (!key) return undefined
  return _cache.get(key)?.url
}
