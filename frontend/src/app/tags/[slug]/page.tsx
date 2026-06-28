import { cacheLife, cacheTag } from 'next/cache'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Tag, ApiItemListResponse, Item } from '@/types'
import ItemCard from '@/components/ui/ItemCard'

interface PageProps {
  params: Promise<{ slug: string }>
}

// ─── Cached data fetchers ────────────────────────────────────────────────────

async function getAllTags(): Promise<Tag[]> {
  'use cache'
  cacheLife('hours')
  cacheTag('tags')
  return serverGet<Tag[]>('/tags', false)
}

async function getItemsByTag(tagSlug: string): Promise<ApiItemListResponse> {
  'use cache'
  cacheLife('catalog')
  cacheTag('items', `tag-${tagSlug}`)
  return serverGet<ApiItemListResponse>(`/items?tag=${tagSlug}&is_published=true`, false)
}

// ─── SEO ─────────────────────────────────────────────────────────────────────

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params
  try {
    const tags = await getAllTags()
    const tag = tags.find((t) => t.slug === slug)
    return { title: tag ? `Тег: ${tag.name}` : 'Тег' }
  } catch {
    return { title: 'Тег' }
  }
}

// Pre-build all tag pages at deployment time.
export async function generateStaticParams() {
  try {
    const tags = await serverGet<Tag[]>('/tags', false)
    return tags.map((t) => ({ slug: t.slug }))
  } catch {
    return []
  }
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default async function TagPage({ params }: PageProps) {
  const { slug } = await params

  const [tags, itemsResp] = await Promise.all([
    getAllTags(),
    getItemsByTag(slug),
  ])

  const tag = tags.find((t) => t.slug === slug)
  if (!tag) notFound()

  const items: Item[] = itemsResp.items.map((e) => ({
    ...e,
    youtube_url: e.youtube_url ?? undefined,
    preview_image: e.preview_image ?? undefined,
  }))

  const previewKeys = items
    .map((item) => item.preview_image)
    .filter((k): k is string => Boolean(k))

  const previewUrls = previewKeys.length > 0
    ? await serverGetPresignedUrls(previewKeys)
    : {} as Record<string, string>

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <nav className="flex items-center gap-2 text-sm text-gray-500 mb-6">
        <Link href="/catalog" className="hover:text-indigo-600">Каталог</Link>
        <span>/</span>
        <span className="text-gray-900 font-medium">#{tag.name}</span>
      </nav>

      <div className="flex items-center gap-3 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{tag.name}</h1>
        <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm font-medium rounded-full">
          #{tag.slug}
        </span>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p className="font-medium">По этому тегу объектов не найдено</p>
          <Link href="/catalog" className="mt-3 inline-block text-indigo-600 hover:underline text-sm">
            Вернуться в каталог
          </Link>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">Найдено: {itemsResp.total}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => (
              <ItemCard
                key={item.id}
                item={item}
                imageUrl={item.preview_image ? previewUrls[item.preview_image] : undefined}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
