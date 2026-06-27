import { api } from '@/lib/api'
import type { Tag } from '@/types'

export async function listTags(): Promise<Tag[]> {
  return api.get<Tag[]>('/tags')
}

export async function createTag(data: { name: string; slug: string }): Promise<Tag> {
  return api.post<Tag>('/tags', data)
}

export async function deleteTag(id: string): Promise<void> {
  await api.delete<void>(`/tags/${id}`)
}
