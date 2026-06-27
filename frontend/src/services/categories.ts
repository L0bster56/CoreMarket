import { api } from '@/lib/api'
import type { Category } from '@/types'

export async function listCategories(): Promise<Category[]> {
  return api.get<Category[]>('/categories')
}

export async function createCategory(data: {
  name: string
  slug: string
  description?: string
  image_url?: string
}): Promise<Category> {
  return api.post<Category>('/categories', data)
}

export async function deleteCategory(id: string): Promise<void> {
  await api.delete<void>(`/categories/${id}`)
}
