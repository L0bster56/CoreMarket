import { api } from '@/lib/api'
import { serverGet } from '@/lib/server-fetch'
import type { BlogListResponse, BlogPost, BlogTag } from '@/types'

// ── Posts ─────────────────────────────────────────────────────────────────────

export interface ListBlogPostsParams {
  search?: string
  category_id?: string
  tag_slug?: string
  post_status?: string
  limit?: number
  offset?: number
}

export async function listBlogPosts(params: ListBlogPostsParams = {}): Promise<BlogListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.category_id) qs.set('category_id', params.category_id)
  if (params.tag_slug) qs.set('tag_slug', params.tag_slug)
  if (params.post_status) qs.set('post_status', params.post_status)
  if (params.limit !== undefined) qs.set('limit', String(params.limit))
  if (params.offset !== undefined) qs.set('offset', String(params.offset))
  const q = qs.toString()
  return api.get<BlogListResponse>(`/blog/posts${q ? `?${q}` : ''}`)
}

export async function serverListBlogPosts(params: ListBlogPostsParams = {}): Promise<BlogListResponse> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.category_id) qs.set('category_id', params.category_id)
  if (params.tag_slug) qs.set('tag_slug', params.tag_slug)
  if (params.post_status) qs.set('post_status', params.post_status)
  if (params.limit !== undefined) qs.set('limit', String(params.limit))
  if (params.offset !== undefined) qs.set('offset', String(params.offset))
  const q = qs.toString()
  return serverGet<BlogListResponse>(`/blog/posts${q ? `?${q}` : ''}`, false)
}

export async function getBlogPost(slug: string): Promise<BlogPost> {
  return serverGet<BlogPost>(`/blog/posts/${slug}`, false)
}

export async function createBlogPost(data: {
  title: string
  slug: string
  short_description?: string | null
}): Promise<BlogPost> {
  return api.post<BlogPost>('/blog/posts', data)
}

export async function updateBlogPost(
  slug: string,
  data: {
    title?: string
    new_slug?: string
    short_description?: string | null
    content?: string | null
    cover_image_url?: string | null
    category_id?: string | null
    seo_title?: string | null
    seo_description?: string | null
  },
): Promise<void> {
  await api.patch<void>(`/blog/posts/${slug}`, data)
}

export async function deleteBlogPost(slug: string): Promise<void> {
  await api.delete<void>(`/blog/posts/${slug}`)
}

export async function publishBlogPost(slug: string): Promise<void> {
  await api.post<void>(`/blog/posts/${slug}/publish`, {})
}

export async function unpublishBlogPost(slug: string): Promise<void> {
  await api.post<void>(`/blog/posts/${slug}/unpublish`, {})
}

export async function archiveBlogPost(slug: string): Promise<void> {
  await api.post<void>(`/blog/posts/${slug}/archive`, {})
}

export async function addBlogPostTag(slug: string, tagId: string): Promise<void> {
  await api.post<void>(`/blog/posts/${slug}/tags`, { tag_id: tagId })
}

export async function removeBlogPostTag(slug: string, tagId: string): Promise<void> {
  await api.delete<void>(`/blog/posts/${slug}/tags/${tagId}`)
}

export async function linkProduct(
  slug: string,
  data: { product_id: string; display_order?: number },
): Promise<{ id: string; product_id: string; display_order: number }> {
  return api.post(`/blog/posts/${slug}/products`, data)
}

export async function unlinkProduct(slug: string, linkId: string): Promise<void> {
  await api.delete<void>(`/blog/posts/${slug}/products/${linkId}`)
}

export async function uploadBlogCover(slug: string, file: File): Promise<{ key: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return api.postMultipart<{ key: string }>(`/blog/posts/${slug}/cover`, formData)
}

// ── Tags ──────────────────────────────────────────────────────────────────────

export async function listBlogTags(): Promise<BlogTag[]> {
  return api.get<BlogTag[]>('/blog/tags')
}

export async function serverListBlogTags(): Promise<BlogTag[]> {
  return serverGet<BlogTag[]>('/blog/tags', 300)
}

export async function createBlogTag(data: { name: string; slug: string }): Promise<BlogTag> {
  return api.post<BlogTag>('/blog/tags', data)
}

export async function updateBlogTag(
  id: string,
  data: { name?: string; slug?: string },
): Promise<void> {
  await api.patch<void>(`/blog/tags/${id}`, data)
}

export async function deleteBlogTag(id: string): Promise<void> {
  await api.delete<void>(`/blog/tags/${id}`)
}
