import { cacheLife, cacheTag } from 'next/cache'
import { notFound } from 'next/navigation'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Category, ApiItemListResponse, Item } from '@/types'
import ItemCard from '@/components/ui/ItemCard'
import Link from 'next/link'

interface PageProps {
  params: Promise<{ category: string }>
}

// ─── Cached data fetchers ────────────────────────────────────────────────────

async function getAllCategories(): Promise<Category[]> {
  'use cache'
  cacheLife('hours')
  cacheTag('categories')
  return serverGet<Category[]>('/categories', false)
}

async function getCategoryItems(categoryId: string): Promise<ApiItemListResponse> {
  'use cache'
  cacheLife('catalog')
  cacheTag('items', `category-${categoryId}`)
  return serverGet<ApiItemListResponse>(
    `/items?category_id=${categoryId}&is_published=true`,
    false,
  )
}

// ─── SEO ─────────────────────────────────────────────────────────────────────

export async function generateMetadata({ params }: PageProps) {
  const { category: slug } = await params
  try {
    const categories = await getAllCategories()
    const category = categories.find((c) => c.slug === slug)
    return { title: category?.name ?? 'Категория' }
  } catch {
    return { title: 'Категория' }
  }
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default async function CategoryPage({ params }: PageProps) {
  const { category: slug } = await params

  const categories = await getAllCategories()
  const category = categories.find((c) => c.slug === slug)
  if (!category) notFound()

  const itemsResp = await getCategoryItems(category.id)

  const items: Item[] = itemsResp.items.map((e) => ({
    ...e,
    youtube_url: e.youtube_url ?? undefined,
    preview_image: e.preview_image ?? undefined,
    category,
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
        <span className="text-gray-900 font-medium">{category.name}</span>
      </nav>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">{category.name}</h1>
      {category.description && (
        <p className="text-gray-500 mb-8">{category.description}</p>
      )}

      {items.length === 0 ? (
        <p className="text-gray-500 py-10 text-center">В этой категории пока нет объектов.</p>
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
