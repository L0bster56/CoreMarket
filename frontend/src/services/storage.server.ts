import { cacheLife, cacheTag } from 'next/cache'

const INTERNAL_API_BASE = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1'

// Sorted keys ensure cache-key consistency regardless of call order.
// URLs are generated with 2hr expiry so they remain valid for the full
// 55min cache window (presigned profile: revalidate 45min + stale 5min + margin).
async function fetchPresignedUrlsRemote(
  sortedKeys: string[],
): Promise<Record<string, string>> {
  'use cache: remote'
  cacheLife('presigned')
  cacheTag('presigned-urls')

  if (sortedKeys.length === 0) return {}
  const res = await fetch(`${INTERNAL_API_BASE}/storage/presigned-urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keys: sortedKeys, expires_in: 7200 }),
    next: { revalidate: 2700 },
  })
  if (!res.ok) return {}
  const data = await res.json() as { urls: Record<string, string> }
  return data.urls
}

export async function serverGetPresignedUrls(
  keys: string[],
  _expiresIn = 3600,
): Promise<Record<string, string>> {
  if (keys.length === 0) return {}
  const sortedKeys = [...keys].sort()
  return fetchPresignedUrlsRemote(sortedKeys)
}
