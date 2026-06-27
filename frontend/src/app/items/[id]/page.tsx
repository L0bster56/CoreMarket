import { Suspense } from 'react'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Category, ApiItemDetail, RatingInfo, ApiComment } from '@/types'
import GalleryViewer from '@/components/ui/GalleryViewer'
import CommentsSection from '@/components/ui/CommentsSection'
import RatingWidget from '@/components/ui/RatingWidget'
import RecommendedProducts from '@/components/ui/RecommendedProducts'
import RecommendedProductsSkeleton from '@/components/ui/RecommendedProductsSkeleton'

function getYouTubeEmbedUrl(url: string): string | null {
  const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
  return match ? `https://www.youtube.com/embed/${match[1]}` : null
}

interface PageProps {
  params: Promise<{ id: string }>
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params
  try {
    const item = await serverGet<ApiItemDetail>(`/items/${id}`, false)
    return {
      title: item.title,
      description: item.short_description,
      openGraph: {
        title: item.title,
        description: item.short_description,
        type: 'website' as const,
        url: `/items/${id}`,
      },
      twitter: {
        card: 'summary_large_image' as const,
        title: item.title,
        description: item.short_description,
      },
    }
  } catch {
    return { title: 'Товар' }
  }
}

export default async function ItemPage({ params }: PageProps) {
  const { id } = await params

  // Fetch item + rating + categories + comments in parallel.
  const [itemResult, ratingResult, categoriesResult, commentsResult] = await Promise.allSettled([
    serverGet<ApiItemDetail>(`/items/${id}`, false),
    serverGet<RatingInfo>(`/items/${id}/rating`, false),
    serverGet<Category[]>('/categories', false),
    serverGet<ApiComment[]>(`/items/${id}/comments`, false),
  ])

  if (itemResult.status === 'rejected') notFound()

  const item = (itemResult as PromiseFulfilledResult<ApiItemDetail>).value
  const rating = ratingResult.status === 'fulfilled'
    ? ratingResult.value
    : { average: 0, count: 0 } as RatingInfo
  const categories = categoriesResult.status === 'fulfilled' ? categoriesResult.value : []
  const initialComments = commentsResult.status === 'fulfilled' ? commentsResult.value : []

  const category = categories.find((c) => c.id === item.category_id)

  // Presigned URLs are served from Redis cache ('use cache: remote' in storage.ts).
  // On first load: ~50ms backend call. On repeat: instant cache hit.
  const galleryKeys = item.gallery.map((g) => g.image_url).filter(Boolean)
  const presignedUrls = galleryKeys.length > 0
    ? await serverGetPresignedUrls(galleryKeys).catch(() => ({} as Record<string, string>))
    : {} as Record<string, string>

  const resolvedGallery = item.gallery.map((g) => ({
    ...g,
    image_url: presignedUrls[g.image_url] ?? g.image_url,
  }))
  const previewImage = resolvedGallery[0]?.image_url ?? ''

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'

  const productJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: item.title,
    description: item.short_description,
    image: previewImage || undefined,
    url: `${siteUrl}/items/${id}`,
    ...(rating.count > 0 && rating.average !== null
      ? {
          aggregateRating: {
            '@type': 'AggregateRating',
            ratingValue: rating.average,
            reviewCount: rating.count,
            bestRating: 5,
            worstRating: 1,
          },
        }
      : {}),
  }

  const breadcrumbJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Каталог', item: `${siteUrl}/catalog` },
      ...(category
        ? [{ '@type': 'ListItem', position: 2, name: category.name, item: `${siteUrl}/catalog/${category.slug}` }]
        : []),
      { '@type': 'ListItem', position: category ? 3 : 2, name: item.title, item: `${siteUrl}/items/${id}` },
    ],
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(productJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-500 mb-6">
        <Link href="/catalog" className="hover:text-indigo-600">Каталог</Link>
        {category && (
          <>
            <span>/</span>
            <Link href={`/catalog/${category.slug}`} className="hover:text-indigo-600">
              {category.name}
            </Link>
          </>
        )}
        <span>/</span>
        <span className="text-gray-900 font-medium line-clamp-1">{item.title}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Gallery */}
        {previewImage ? (
          <GalleryViewer
            preview={previewImage}
            gallery={resolvedGallery}
            title={item.title}
          />
        ) : (
          <div className="aspect-video rounded-2xl bg-gray-100 flex items-center justify-center text-gray-300">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Info */}
        <div>
          {category && (
            <Link
              href={`/catalog/${category.slug}`}
              className="text-xs text-indigo-600 font-semibold uppercase tracking-wide hover:text-indigo-800"
            >
              {category.name}
            </Link>
          )}
          <h1 className="mt-2 text-3xl font-bold text-gray-900 leading-tight">{item.title}</h1>

          <RatingWidget
            itemId={id}
            initialAverage={rating.average}
            initialCount={rating.count}
          />

          {item.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {item.tags.map((tag) => (
                <Link
                  key={tag.id}
                  href={`/tags/${tag.slug}`}
                  className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full hover:bg-indigo-100 transition-colors"
                >
                  #{tag.name}
                </Link>
              ))}
            </div>
          )}

          <p className="mt-4 text-gray-600 leading-relaxed">{item.short_description}</p>
          <p className="mt-3 text-gray-700 leading-relaxed">{item.description}</p>

          {/* Characteristics */}
          {item.characteristics.length > 0 && (() => {
            const ungrouped = item.characteristics.filter(c => !c.group)
            const groupOrder: string[] = []
            const grouped: Record<string, typeof item.characteristics> = {}
            for (const c of item.characteristics) {
              if (!c.group) continue
              if (!grouped[c.group]) { groupOrder.push(c.group); grouped[c.group] = [] }
              grouped[c.group].push(c)
            }
            return (
              <div className="mt-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Характеристики</h2>

                {ungrouped.length > 0 && (
                  <div className="rounded-xl border border-gray-200 overflow-hidden mb-4">
                    <table className="w-full text-sm">
                      <tbody>
                        {ungrouped.map((c, i) => (
                          <tr key={c.id} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="px-4 py-2.5 text-gray-500 font-medium w-2/5">{c.name}</td>
                            <td className="px-4 py-2.5 text-gray-900">{c.value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {groupOrder.map((groupName) => (
                  <div key={groupName} className="mb-4">
                    <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide px-1 mb-1">
                      {groupName}
                    </h3>
                    <div className="rounded-xl border border-gray-200 overflow-hidden">
                      <table className="w-full text-sm">
                        <tbody>
                          {grouped[groupName].map((c, i) => (
                            <tr key={c.id} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                              <td className="px-4 py-2.5 text-gray-500 font-medium w-2/5">{c.name}</td>
                              <td className="px-4 py-2.5 text-gray-900">{c.value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            )
          })()}

        </div>
      </div>

      {/* Marketplace Links */}
      {item.marketplace_links.length > 0 && (
        <div className="mt-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Где купить</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {item.marketplace_links.map((link, i) => (
              <a
                key={i}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center justify-between gap-4 px-5 py-4 bg-white rounded-2xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all"
              >
                <p className="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors truncate">
                  {link.name}
                </p>
                {link.price && (
                  <p className="shrink-0 text-indigo-600 font-bold text-base">{link.price}</p>
                )}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* YouTube Video */}
      {item.youtube_url && (() => {
        const embedUrl = getYouTubeEmbedUrl(item.youtube_url!)
        if (!embedUrl) return null
        return (
          <div className="mt-14">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Обзор</h2>
              <a
                href={item.youtube_url!}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-xl hover:bg-red-700 transition-colors"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21.543 6.498C22 8.28 22 12 22 12s0 3.72-.457 5.502c-.254.985-.997 1.76-1.938 2.022C17.896 20 12 20 12 20s-5.893 0-7.605-.476c-.945-.266-1.687-1.04-1.938-2.022C2 15.72 2 12 2 12s0-3.72.457-5.502c.254-.985.997-1.76 1.938-2.022C6.107 4 12 4 12 4s5.896 0 7.605.476c.945.266 1.687 1.04 1.938 2.022z"/>
                  <path fill="white" d="M10 15.5l6-3.5-6-3.5v7z"/>
                </svg>
                Смотреть на YouTube
              </a>
            </div>
            <div className="relative w-full aspect-video rounded-2xl overflow-hidden bg-black">
              <iframe
                src={embedUrl}
                title={`Обзор: ${item.title}`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
                className="absolute inset-0 w-full h-full"
              />
            </div>
          </div>
        )
      })()}

      {/* Recommended Products (streamed) */}
      <Suspense fallback={<RecommendedProductsSkeleton />}>
        <RecommendedProducts item={item} categories={categories} />
      </Suspense>

      {/* Comments — client component, fetches on mount (no server-side fetch) */}
      <div className="mt-14">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Комментарии</h2>
        <CommentsSection itemId={id} initialComments={initialComments} />
      </div>
    </div>
  )
}
