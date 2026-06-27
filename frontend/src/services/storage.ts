import { api } from '@/lib/api'

export async function getPresignedUrls(
  keys: string[],
  expiresIn = 3600,
): Promise<Record<string, string>> {
  const result = await api.post<{ urls: Record<string, string> }>('/storage/presigned-urls', {
    keys,
    expires_in: expiresIn,
  })
  return result.urls
}
