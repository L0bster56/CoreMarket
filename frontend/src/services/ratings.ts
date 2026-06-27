import { api } from '@/lib/api'
import type { RatingInfo } from '@/types'

export async function getRating(itemId: string): Promise<RatingInfo> {
  return api.get<RatingInfo>(`/items/${itemId}/rating`)
}

export async function createRating(itemId: string, score: number): Promise<void> {
  await api.post<void>(`/items/${itemId}/rating`, { score })
}

export async function updateRating(itemId: string, score: number): Promise<void> {
  await api.patch<void>(`/items/${itemId}/rating`, { score })
}

export async function deleteRating(itemId: string): Promise<void> {
  await api.delete<void>(`/items/${itemId}/rating`)
}
