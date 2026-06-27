'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import {
  listBlogPosts,
  deleteBlogPost,
  publishBlogPost,
  unpublishBlogPost,
} from '@/services/blog'
import { listCategories } from '@/services/categories'
import type { BlogPostListEntry, Category } from '@/types'

const STATUS_LABELS: Record<string, string> = {
  draft: 'Черновик',
  published: 'Опубликован',
  archived: 'Архив',
}
const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  published: 'bg-green-50 text-green-700 border-green-200',
  archived: 'bg-gray-100 text-gray-500 border-gray-200',
}

function Spinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

export default function AdminBlogPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  const [posts, setPosts] = useState<BlogPostListEntry[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [actionSlug, setActionSlug] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const [postsResp, cats] = await Promise.all([
        listBlogPosts({ limit: 100 }),
        listCategories(),
      ])
      setPosts(postsResp.items)
      setCategories(cats)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
    load()
  }, [user, isLoading, router, load])

  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]))

  const handleDelete = async (post: BlogPostListEntry) => {
    if (!confirm(`Удалить «${post.title}»?`)) return
    setActionSlug(post.slug)
    try {
      await deleteBlogPost(post.slug)
      await load()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка удаления')
    } finally {
      setActionSlug(null)
    }
  }

  const handleTogglePublish = async (post: BlogPostListEntry) => {
    setActionSlug(post.slug)
    try {
      if (post.status === 'published') {
        await unpublishBlogPost(post.slug)
      } else {
        await publishBlogPost(post.slug)
      }
      await load()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка изменения статуса')
    } finally {
      setActionSlug(null)
    }
  }

  if (isLoading || loading) return <Spinner />

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Блог</h1>
          <p className="text-sm text-gray-500 mt-1">{posts.length} статей</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/admin"
            className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-xl hover:border-gray-300 transition-colors"
          >
            ← Панель
          </Link>
          <Link
            href="/admin/blog/new"
            className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 transition-colors"
          >
            + Новая статья
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Статья</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Категория</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Статус</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Дата</th>
                <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {posts.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-gray-400">
                    Статей нет.{' '}
                    <Link href="/admin/blog/new" className="text-indigo-600 hover:underline">Создать первую</Link>
                  </td>
                </tr>
              )}
              {posts.map((post) => (
                <tr key={post.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {post.cover_image_url && (
                        <img
                          src={post.cover_image_url}
                          alt=""
                          className="w-10 h-10 rounded-lg object-cover shrink-0"
                        />
                      )}
                      <div className="min-w-0">
                        <p className="font-medium text-gray-900 truncate max-w-xs">{post.title}</p>
                        <p className="text-xs text-gray-400 truncate">/blog/{post.slug}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {post.category_id ? (categoryMap[post.category_id]?.name ?? '—') : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${STATUS_COLORS[post.status]}`}>
                      {STATUS_LABELS[post.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{formatDate(post.created_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleTogglePublish(post)}
                        disabled={actionSlug === post.slug}
                        className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors disabled:opacity-50 ${
                          post.status === 'published'
                            ? 'border-yellow-200 text-yellow-700 hover:bg-yellow-50'
                            : 'border-green-200 text-green-700 hover:bg-green-50'
                        }`}
                      >
                        {post.status === 'published' ? 'Снять' : 'Опубл.'}
                      </button>
                      <Link
                        href={`/admin/blog/${post.slug}/edit`}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg border border-indigo-200 text-indigo-700 hover:bg-indigo-50 transition-colors"
                      >
                        Редакт.
                      </Link>
                      <button
                        onClick={() => handleDelete(post)}
                        disabled={actionSlug === post.slug}
                        className="px-3 py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                      >
                        Удалить
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
