import { api } from '@/lib/api'
import type { ApiItemListResponse, ApiItemDetail, MarketplaceLink } from '@/types'

export interface ListItemsParams {
  search?: string
  category_id?: string
  tag?: string
  min_rating?: number
  is_published?: boolean
  limit?: number
  offset?: number
}

export async function listItems(params: ListItemsParams = {}): Promise<ApiItemListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.category_id) qs.set('category_id', params.category_id)
  if (params.tag) qs.set('tag', params.tag)
  if (params.min_rating !== undefined) qs.set('min_rating', String(params.min_rating))
  if (params.is_published !== undefined) qs.set('is_published', String(params.is_published))
  if (params.limit !== undefined) qs.set('limit', String(params.limit))
  if (params.offset !== undefined) qs.set('offset', String(params.offset))
  const query = qs.toString()
  return api.get<ApiItemListResponse>(`/items${query ? `?${query}` : ''}`)
}

export async function getItem(id: string): Promise<ApiItemDetail> {
  return api.get<ApiItemDetail>(`/items/${id}`)
}

export async function createItem(data: {
  title: string
  short_description: string
  description: string
  category_id: string
  youtube_url?: string | null
  marketplace_links?: MarketplaceLink[]
}): Promise<ApiItemDetail> {
  return api.post<ApiItemDetail>('/items', data)
}

export async function updateItem(
  id: string,
  data: {
    title?: string
    short_description?: string
    description?: string
    category_id?: string
    youtube_url?: string | null
    is_published?: boolean
    marketplace_links?: MarketplaceLink[]
    view_count?: number
  },
): Promise<void> {
  await api.patch<void>(`/items/${id}`, data)
}

export async function deleteItem(id: string): Promise<void> {
  await api.delete<void>(`/items/${id}`)
}

export async function addGalleryImage(itemId: string, imageUrl: string): Promise<void> {
  await api.post<void>(`/items/${itemId}/gallery`, { image_url: imageUrl })
}

export async function deleteGalleryImage(itemId: string, imageId: string): Promise<void> {
  await api.delete<void>(`/items/${itemId}/gallery/${imageId}`)
}

export async function addCharacteristic(
  itemId: string,
  data: { name: string; value: string; group?: string | null },
): Promise<{ id: string; name: string; value: string; group: string | null }> {
  return api.post(`/items/${itemId}/characteristics`, data)
}

export async function deleteCharacteristic(itemId: string, charId: string): Promise<void> {
  await api.delete<void>(`/items/${itemId}/characteristics/${charId}`)
}

export async function addItemTag(itemId: string, tagId: string): Promise<void> {
  await api.post<void>(`/items/${itemId}/tags`, { tag_id: tagId })
}

export async function removeItemTag(itemId: string, tagId: string): Promise<void> {
  await api.delete<void>(`/items/${itemId}/tags/${tagId}`)
}
