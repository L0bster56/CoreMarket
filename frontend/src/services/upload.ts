import { api } from '@/lib/api'

export async function uploadFile(
  file: File,
  section: 'items' | 'categories' | 'users',
): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)
  const result = await api.postMultipart<{ key: string }>(`/upload?section=${section}`, formData)
  return result.key
}
