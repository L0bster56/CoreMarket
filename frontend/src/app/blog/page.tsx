import { Suspense } from 'react'
import { cacheLife, cacheTag } from 'next/cache'
import Link from 'next/link'
import { serverGet } from '@/lib/server-fetch'
import { serverGetPresignedUrls } from '@/services/storage.server'
import type { Category, BlogListResponse, BlogTag } from '@/types'
import BlogPostCard from '@/components/blog/BlogPostCard'

interface SearchParams {
  search?: string
  category_id?: string
  tag_slug?: string
  page?: string
}

interface PageProps {
  searchParams: Promise<SearchParams>
}

export const metadata = { title: 'Блог' }

const PAGE_SIZE = 12

// ─── Cached sidebar data (stable key — no filter props) ──────────────────────

async function fetchBlogSidebarData(): Promise<{ categories: Category[]; tags: BlogTag[] }> {
  'use cache'
  cacheLife('hours')
  cacheTag('categories', 'blog-tags')

  const [categories, tags] = await Promise.all([
    serverGet<Category[]>('/categories', 3600),
    serverGet<BlogTag[]>('/blog/tags', 3600),
  ])
  return { categories, tags }
}

// ─── Sidebar renderer (per-request, no cache — depends on filter props) ───────

async function BlogSidebar({
  activeCategoryId,
  activeTagSlug,
  search,
  page,
}: {
  activeCategoryId?: string
  activeTagSlug?: string
  search?: string
  page: number
}) {
  const { categories, tags } = await fetchBlogSidebarData()

  const buildUrl = (overrides: Record<string, string | undefined>) => {
    const p = new URLSearchParams()
    const merged = {
      search,
      category_id: activeCategoryId,
      tag_slug: activeTagSlug,
      page: String(page),
      ...overrides,
    }
    Object.entries(merged).forEach(([k, v]) => { if (v) p.set(k, v) })
    const s = p.toString()
    return `/blog${s ? `?${s}` : ''}`
  }

  return (
    <>
      {/* Category filter */}
      {categories.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <Link
            href={buildUrl({ category_id: undefined, page: '1' })}
            className={`px-3 py-2 rounded-xl text-sm font-medium border transition-colors ${
              !activeCategoryId
                ? 'bg-indigo-600 text-white border-indigo-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
            }`}
          >
            Все
          </Link>
          {categories.map((c) => (
            <Link
              key={c.id}
              href={buildUrl({ category_id: c.id, page: '1' })}
              className={`px-3 py-2 rounded-xl text-sm font-medium border transition-colors ${
                activeCategoryId === c.id
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              {c.name}
            </Link>
          ))}
        </div>
      )}

      {/* Tag filter */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {tags.map((t) => (
            <Link
              key={t.id}
              href={buildUrl({ tag_slug: activeTagSlug === t.slug ? undefined : t.slug, page: '1' })}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                activeTagSlug === t.slug
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-600 border-gray-200 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200'
              }`}
            >
              #{t.name}
            </Link>
          ))}
        </div>
      )}
    </>
  )
}

// ─── Dynamic: blog posts list (depends on searchParams) ──────────────────────

async function BlogPostsList({ params }: { params: SearchParams }) {
  const { search, category_id, tag_slug } = params
  const page = Math.max(1, Number(params.page ?? 1))
  const offset = (page - 1) * PAGE_SIZE

  const qs = new URLSearchParams()
  qs.set('post_status', 'published')
  qs.set('limit', String(PAGE_SIZE))
  qs.set('offset', String(offset))
  if (search) qs.set('search', search)
  if (category_id) qs.set('category_id', category_id)
  if (tag_slug) qs.set('tag_slug', tag_slug)

  const [categories, postsResp] = await Promise.all([
    serverGet<Category[]>('/categories', 3600),
    serverGet<BlogListResponse>(`/blog/posts?${qs.toString()}`, false),
  ])

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))
  const totalPages = Math.ceil(postsResp.total / PAGE_SIZE)

  const coverKeys = postsResp.items
    .map((p) => p.cover_image_url)
    .filter((k): k is string => Boolean(k))
  const coverUrls = coverKeys.length > 0
    ? await serverGetPresignedUrls(coverKeys)
    : {} as Record<string, string>

  const buildUrl = (overrides: Record<string, string | undefined>) => {
    const p = new URLSearchParams()
    const merged = { search, category_id, tag_slug, page: String(page), ...overrides }
    Object.entries(merged).forEach(([k, v]) => { if (v) p.set(k, v) })
    const s = p.toString()
    return `/blog${s ? `?${s}` : ''}`
  }

  if (postsResp.items.length === 0) {
    return (
      <div className="text-center py-20 text-gray-400">
        <svg className="w-12 h-12 mx-auto mb-3 text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="font-medium text-gray-500">Статей пока нет</p>
        {(search || category_id || tag_slug) && (
          <Link href="/blog" className="mt-3 inline-block text-sm text-indigo-600 hover:underline">
            Сбросить фильтры
          </Link>
        )}
      </div>
    )
  }

  return (
    <>
      <p className="text-sm text-gray-500 mb-4">Найдено: {postsResp.total}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {postsResp.items.map((post) => (
          <BlogPostCard
            key={post.id}
            post={post}
            categoryName={post.category_id ? categoryMap[post.category_id]?.name : undefined}
            coverImageUrl={post.cover_image_url ? coverUrls[post.cover_image_url] : undefined}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-10">
          {page > 1 && (
            <Link
              href={buildUrl({ page: String(page - 1) })}
              className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
            >
              ← Назад
            </Link>
          )}
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <Link
              key={p}
              href={buildUrl({ page: String(p) })}
              className={`w-9 h-9 flex items-center justify-center rounded-xl text-sm font-medium border transition-colors ${
                p === page
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              {p}
            </Link>
          ))}
          {page < totalPages && (
            <Link
              href={buildUrl({ page: String(page + 1) })}
              className="px-4 py-2 rounded-xl border border-gray-200 text-sm text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
            >
              Вперёд →
            </Link>
          )}
        </div>
      )}
    </>
  )
}

function PostsListSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="bg-gray-100 rounded-2xl h-56 animate-pulse" />
      ))}
    </div>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────
// Sidebar (categories/tags) is prerendered and cached for 1hr.
// Posts list is dynamic (searchParams) and streams at request time.

export default async function BlogPage({ searchParams }: PageProps) {
  const params = await searchParams
  const { search, category_id, tag_slug } = params
  const page = Math.max(1, Number(params.page ?? 1))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Блог</h1>
      <p className="text-gray-500 mb-8">Статьи и обзоры</p>

      {/* Search form (static UI) */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <form action="/blog" className="flex-1 max-w-sm">
          <input type="hidden" name="category_id" value={category_id ?? ''} />
          <input type="hidden" name="tag_slug" value={tag_slug ?? ''} />
          <div className="relative">
            <input
              name="search"
              defaultValue={search ?? ''}
              placeholder="Поиск по блогу..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 bg-white"
            />
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </form>
      </div>

      {/* Sidebar: cached categories + tags */}
      <Suspense fallback={<div className="h-10 bg-gray-100 rounded-xl mb-6 animate-pulse" />}>
        <BlogSidebar
          activeCategoryId={category_id}
          activeTagSlug={tag_slug}
          search={search}
          page={page}
        />
      </Suspense>

      {/* Posts: dynamic, streams at request time */}
      <div className="mt-8">
        <Suspense fallback={<PostsListSkeleton />}>
          <BlogPostsList params={params} />
        </Suspense>
      </div>
    </div>
  )
}
