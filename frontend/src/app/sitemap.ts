import type { MetadataRoute } from 'next'
import { serverGet } from '@/lib/server-fetch'
import type { Category, Tag, ApiItemListResponse, BlogListResponse } from '@/types'

export const revalidate = 3600

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date()

  const entries: MetadataRoute.Sitemap = [
    { url: SITE_URL, lastModified: now, changeFrequency: 'daily', priority: 1 },
    { url: `${SITE_URL}/catalog`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${SITE_URL}/blog`, lastModified: now, changeFrequency: 'daily', priority: 0.8 },
  ]

  const [categories, tags, itemsResp, blogResp] = await Promise.allSettled([
    serverGet<Category[]>('/categories', 3600),
    serverGet<Tag[]>('/tags', 3600),
    serverGet<ApiItemListResponse>('/items?is_published=true&limit=1000', 3600),
    serverGet<BlogListResponse>('/blog/posts?post_status=published&limit=1000', 3600),
  ])

  if (categories.status === 'fulfilled') {
    for (const cat of categories.value) {
      entries.push({
        url: `${SITE_URL}/catalog/${cat.slug}`,
        lastModified: new Date(cat.created_at),
        changeFrequency: 'weekly',
        priority: 0.7,
      })
    }
  }

  if (tags.status === 'fulfilled') {
    for (const tag of tags.value) {
      entries.push({
        url: `${SITE_URL}/tags/${tag.slug}`,
        lastModified: now,
        changeFrequency: 'weekly',
        priority: 0.5,
      })
    }
  }

  if (itemsResp.status === 'fulfilled') {
    for (const item of itemsResp.value.items) {
      entries.push({
        url: `${SITE_URL}/items/${item.id}`,
        lastModified: new Date(item.updated_at),
        changeFrequency: 'weekly',
        priority: 0.6,
      })
    }
  }

  if (blogResp.status === 'fulfilled') {
    for (const post of blogResp.value.items) {
      entries.push({
        url: `${SITE_URL}/blog/${post.slug}`,
        lastModified: new Date(post.updated_at),
        changeFrequency: 'monthly',
        priority: 0.7,
      })
    }
  }

  return entries
}
