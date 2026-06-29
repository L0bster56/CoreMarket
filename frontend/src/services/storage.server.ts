import { unstable_cache } from 'next/cache'

const INTERNAL_API_BASE = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1'

const fetchPresignedUrlsRemote = unstable_cache(
  async (sortedKeys: string[]): Promise<Record<string, string>> => {
    if (sortedKeys.length === 0) return {}
    const res = await fetch(`${INTERNAL_API_BASE}/storage/presigned-urls`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keys: sortedKeys, expires_in: 7200 }),
    })
    if (!res.ok) return {}
    const data = await res.json() as { urls: Record<string, string> }
    return data.urls
  },
  ['presigned-urls'],
  { revalidate: 2700, tags: ['presigned-urls'] },
)

export async function serverGetPresignedUrls(
  keys: string[],
  _expiresIn = 3600,
): Promise<Record<string, string>> {
  if (keys.length === 0) return {}
  const sortedKeys = [...keys].sort()
  return fetchPresignedUrlsRemote(sortedKeys)
}
