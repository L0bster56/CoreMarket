import { cacheLife, cacheTag } from 'next/cache'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import MarkdownContent from '@/components/ui/MarkdownContent'
import type { BlogPost, ApiItemDetail, ApiItemListEntry, ApiItemListResponse, Category } from '@/types'

interface CompactItem {
  id: string
  title: string
  preview_image?: string
}

function CompactItemCard({ item }: { item: CompactItem }) {
  return (
    <Link href={`/items/${item.id}`} className="group flex flex-col">
      <div className="relative aspect-square rounded-xl overflow-hidden bg-gray-100 mb-2">
        {item.preview_image ? (
          <Image
            src={item.preview_image}
            alt={item.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-200"
            sizes="(max-width: 640px) 40vw, (max-width: 1024px) 20vw, 160px"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>
      <p className="text-xs font-medium text-gray-800 line-clamp-2 group-hover:text-indigo-600 transition-colors leading-snug">
        {item.title}
      </p>
    </Link>
  )
}

// ─── Cached data fetchers ────────────────────────────────────────────────────
// Blog post content is editorial content that rarely changes.
// 'days' profile: stale 5min, revalidate 1 day, expire 1 week.

async function getBlogPost(slug: string): Promise<BlogPost> {
  'use cache'
  cacheLife('days')
  cacheTag('blog-posts', `blog-post-${slug}`)
  return serverGet<BlogPost>(`/blog/posts/${slug}`, false)
}

async function getBlogPostProducts(
  post: BlogPost,
): Promise<{ productItems: ApiItemDetail[]; categoryItems: ApiItemListEntry[] }> {
  'use cache'
  cacheLife('hours')
  cacheTag('items', `blog-post-products-${post.slug}`)

  const linkedProductIds = new Set(post.product_links.map((l) => l.product_id))

  const [productItems, categoryItems] = await Promise.all([
    post.product_links.length > 0
      ? Promise.all(
          post.product_links
            .sort((a, b) => a.display_order - b.display_order)
            .map((l) => serverGet<ApiItemDetail>(`/items/${l.product_id}`, false).catch(() => null)),
        ).then((results) => results.filter(Boolean) as ApiItemDetail[])
      : Promise.resolve([] as ApiItemDetail[]),

    post.category?.id
      ? serverGet<ApiItemListResponse>(
          `/items?category_id=${post.category.id}&is_published=true&limit=20`,
          false,
        )
          .then((res) =>
            res.items
              .filter((item) => !linkedProductIds.has(item.id))
              .sort((a, b) => b.view_count - a.view_count)
              .slice(0, 5),
          )
          .catch(() => [] as ApiItemListEntry[])
      : Promise.resolve([] as ApiItemListEntry[]),
  ])

  return { productItems, categoryItems }
}

// ─── Metadata ────────────────────────────────────────────────────────────────

interface PageProps {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params
  try {
    const post = await getBlogPost(slug)
    const title = post.seo_title ?? post.title
    const description = post.seo_description ?? post.short_description ?? undefined
    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: 'article' as const,
        url: `/blog/${slug}`,
        publishedTime: post.created_at,
        modifiedTime: post.updated_at,
        ...(post.category ? { section: post.category.name } : {}),
        ...(post.tags.length > 0 ? { tags: post.tags.map((t) => t.name) } : {}),
      },
      twitter: {
        card: 'summary_large_image' as const,
        title,
        description,
      },
      alternates: {
        canonical: `/blog/${slug}`,
      },
    }
  } catch {
    return { title: 'Статья' }
  }
}

// Pre-build all published blog posts at deployment time.
export async function generateStaticParams() {
  try {
    const resp = await serverGet<{ items: { slug: string }[] }>(
      '/blog/posts?post_status=published&limit=200',
      false,
    )
    const params = resp.items.map((p) => ({ slug: p.slug }))
    return params.length > 0 ? params : [{ slug: '_' }]
  } catch {
    return [{ slug: '_' }]
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params

  let post: BlogPost
  try {
    post = await getBlogPost(slug)
  } catch {
    notFound()
  }

  if (post.status !== 'published') notFound()

  const { productItems, categoryItems } = await getBlogPostProducts(post)

  // Batch-resolve presigned URLs (cached via 'use cache: remote')
  const imageKeys: string[] = []
  if (post.cover_image_url) imageKeys.push(post.cover_image_url)
  for (const item of productItems) {
    if (item.gallery[0]?.image_url) imageKeys.push(item.gallery[0].image_url)
  }
  const presignedUrls = imageKeys.length > 0 ? await serverGetPresignedUrls(imageKeys) : {}
  const resolvedCover = post.cover_image_url ? presignedUrls[post.cover_image_url] : undefined

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'

  const articleJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.seo_title ?? post.title,
    description: post.seo_description ?? post.short_description ?? undefined,
    image: resolvedCover || undefined,
    datePublished: post.created_at,
    dateModified: post.updated_at,
    url: `${siteUrl}/blog/${post.slug}`,
    publisher: {
      '@type': 'Organization',
      name: 'CoreMarket',
      url: siteUrl,
    },
    ...(post.category ? { articleSection: post.category.name } : {}),
    ...(post.tags.length > 0 ? { keywords: post.tags.map((t) => t.name).join(', ') } : {}),
  }

  const breadcrumbJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Главная', item: siteUrl },
      { '@type': 'ListItem', position: 2, name: 'Блог', item: `${siteUrl}/blog` },
      ...(post.category
        ? [{ '@type': 'ListItem', position: 3, name: post.category.name, item: `${siteUrl}/blog?category_id=${post.category.id}` }]
        : []),
      {
        '@type': 'ListItem',
        position: post.category ? 4 : 3,
        name: post.title,
        item: `${siteUrl}/blog/${post.slug}`,
      },
    ],
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleJsonLd) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />

      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-gray-400 mb-8">
        <Link href="/" className="hover:text-indigo-600 transition-colors">Главная</Link>
        <span>/</span>
        <Link href="/blog" className="hover:text-indigo-600 transition-colors">Блог</Link>
        {post.category && (
          <>
            <span>/</span>
            <Link
              href={`/blog?category_id=${post.category.id}`}
              className="hover:text-indigo-600 transition-colors"
            >
              {post.category.name}
            </Link>
          </>
        )}
        <span>/</span>
        <span className="text-gray-600 truncate max-w-xs">{post.title}</span>
      </nav>

      {/* Заголовок */}
      <header className="mb-8">
        {post.category && (
          <Link
            href={`/blog?category_id=${post.category.id}`}
            className="inline-block mb-3 px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full hover:bg-indigo-100 transition-colors"
          >
            {post.category.name}
          </Link>
        )}
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 leading-tight">{post.title}</h1>
        {post.short_description && (
          <p className="mt-3 text-lg text-gray-500">{post.short_description}</p>
        )}
        <div className="mt-4 flex items-center gap-4 text-sm text-gray-400">
          <span>{formatDate(post.created_at)}</span>
          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {post.tags.map((t) => (
                <Link
                  key={t.id}
                  href={`/blog?tag_slug=${t.slug}`}
                  className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                >
                  #{t.name}
                </Link>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Обложка */}
      {resolvedCover && (
        <div className="mb-10 rounded-2xl overflow-hidden relative w-full aspect-[2.5/1]">
          <Image
            src={resolvedCover}
            alt={post.title}
            fill
            className="object-cover"
            priority
            sizes="(max-width: 640px) 100vw, (max-width: 1280px) 90vw, 1100px"
          />
        </div>
      )}

      {/* Контент */}
      {post.content_html ? (
        <MarkdownContent
          html={post.content_html}
          className="prose max-w-none mb-12"
        />
      ) : (
        <p className="text-gray-400 italic mb-12">Контент статьи пока не добавлен.</p>
      )}

      {/* Товары из статьи */}
      {productItems.length > 0 && (
        <section className="mt-12 border-t border-gray-100 pt-10">
          <h2 className="text-base font-semibold text-gray-700 mb-4">Товары из статьи</h2>
          <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-3">
            {productItems.slice(0, 5).map((item) => (
              <CompactItemCard
                key={item.id}
                item={{
                  id: item.id,
                  title: item.title,
                  preview_image: item.gallery[0]?.image_url
                    ? presignedUrls[item.gallery[0].image_url]
                    : undefined,
                }}
              />
            ))}
          </div>
        </section>
      )}

      {/* Популярное в категории */}
      {categoryItems.length > 0 && (
        <section className={`border-t border-gray-100 pt-10 ${productItems.length > 0 ? 'mt-8' : 'mt-12'}`}>
          <div className="flex items-baseline gap-3 mb-4">
            <h2 className="text-base font-semibold text-gray-700">Популярное в категории</h2>
            {post.category && (
              <Link
                href={`/catalog/${post.category.slug}`}
                className="text-sm text-indigo-600 hover:text-indigo-800 transition-colors"
              >
                {post.category.name} →
              </Link>
            )}
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-3">
            {categoryItems.map((item) => (
              <CompactItemCard
                key={item.id}
                item={{ id: item.id, title: item.title }}
              />
            ))}
          </div>
        </section>
      )}

      {/* Назад */}
      <div className="mt-12 pt-8 border-t border-gray-100">
        <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800 transition-colors">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Все статьи
        </Link>
      </div>
    </div>
  )
}
