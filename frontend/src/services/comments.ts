import { api } from '@/lib/api'
import type { ApiComment } from '@/types'

export async function listComments(itemId: string): Promise<ApiComment[]> {
  return api.get<ApiComment[]>(`/items/${itemId}/comments`)
}

export async function createComment(
  itemId: string,
  body: string,
  parent_id?: string | null,
): Promise<ApiComment> {
  return api.post<ApiComment>(`/items/${itemId}/comments`, {
    body,
    parent_id: parent_id ?? null,
  })
}

export async function updateComment(
  itemId: string,
  commentId: string,
  body: string,
): Promise<void> {
  await api.patch<void>(`/items/${itemId}/comments/${commentId}`, { body })
}

export async function deleteComment(itemId: string, commentId: string): Promise<void> {
  await api.delete<void>(`/items/${itemId}/comments/${commentId}`)
}
