'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { createBlogPost } from '@/services/blog'

function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[а-яёА-ЯЁ]/g, (c) => {
      const map: Record<string, string> = {
        а:'a',б:'b',в:'v',г:'g',д:'d',е:'e',ё:'yo',ж:'zh',з:'z',и:'i',й:'j',
        к:'k',л:'l',м:'m',н:'n',о:'o',п:'p',р:'r',с:'s',т:'t',у:'u',ф:'f',
        х:'kh',ц:'ts',ч:'ch',ш:'sh',щ:'sch',ъ:'',ы:'y',ь:'',э:'e',ю:'yu',я:'ya',
      }
      return map[c.toLowerCase()] ?? c
    })
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

export default function NewBlogPostPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  const [title, setTitle] = useState('')
  const [slug, setSlug] = useState('')
  const [shortDesc, setShortDesc] = useState('')
  const [slugEdited, setSlugEdited] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
  }, [user, isLoading, router])

  const handleTitleChange = (v: string) => {
    setTitle(v)
    if (!slugEdited) setSlug(slugify(v))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !slug.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const post = await createBlogPost({ title: title.trim(), slug: slug.trim(), short_description: shortDesc.trim() || null })
      router.push(`/admin/blog/${post.slug}/edit`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/admin/blog" className="text-gray-400 hover:text-gray-600 transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Новая статья</h1>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-5">
        {error && (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Заголовок *</label>
          <input
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="Заголовок статьи"
            required
            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Slug *
            <span className="ml-1.5 text-xs text-gray-400 font-normal">URL: /blog/{slug || '…'}</span>
          </label>
          <input
            value={slug}
            onChange={(e) => { setSlug(e.target.value); setSlugEdited(true) }}
            placeholder="my-article-slug"
            required
            pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$"
            title="Только латиница, цифры и дефисы"
            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm font-mono focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">Краткое описание</label>
          <textarea
            value={shortDesc}
            onChange={(e) => setShortDesc(e.target.value)}
            placeholder="Краткое описание для карточки и SEO"
            rows={3}
            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Link
            href="/admin/blog"
            className="px-5 py-2.5 text-sm text-gray-600 border border-gray-200 rounded-xl hover:border-gray-300 transition-colors"
          >
            Отмена
          </Link>
          <button
            type="submit"
            disabled={submitting || !title.trim() || !slug.trim()}
            className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Создание…' : 'Создать и редактировать →'}
          </button>
        </div>
      </form>
    </div>
  )
}
