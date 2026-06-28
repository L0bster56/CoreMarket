const API_BASE = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1'

function parseError(status: number, body: string): Error {
  try {
    const json = JSON.parse(body) as { detail?: string }
    if (json.detail) return new Error(json.detail)
  } catch { /* not JSON */ }
  return new Error(body || `API error ${status}`)
}

export async function serverGet<T>(
  path: string,
  revalidate: number | false = 60,
): Promise<T> {
  const opts: RequestInit = revalidate === false
    ? { cache: 'no-store' }
    : { next: { revalidate } } as RequestInit
  const res = await fetch(`${API_BASE}${path}`, opts)
  if (!res.ok) throw parseError(res.status, await res.text())
  return res.json() as Promise<T>
}
