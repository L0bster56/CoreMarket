'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import {
  updateBlogPost,
  publishBlogPost,
  unpublishBlogPost,
  addBlogPostTag,
  removeBlogPostTag,
  linkProduct,
  unlinkProduct,
  uploadBlogCover,
  listBlogTags,
  createBlogTag,
} from '@/services/blog'
import { getPresignedUrls } from '@/services/storage'
import { listItems } from '@/services/items'
import { listCategories } from '@/services/categories'
import { api } from '@/lib/api'
import MarkdownContent from '@/components/ui/MarkdownContent'
import type { BlogPost, Category, BlogTag, ApiItemListEntry } from '@/types'

// Lazy-load marked только на клиенте
async function renderMarkdown(md: string): Promise<string> {
  const { marked } = await import('marked')
  return marked(md) as string
}

function Spinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

type EditorTab = 'editor' | 'preview'

export default function EditBlogPostPage() {
  const router = useRouter()
  const { slug: urlSlug } = useParams<{ slug: string }>()
  const { user, isLoading } = useAuth()

  const [post, setPost] = useState<BlogPost | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [allTags, setAllTags] = useState<BlogTag[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Основные поля
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [shortDesc, setShortDesc] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [seoTitle, setSeoTitle] = useState('')
  const [seoDesc, setSeoDesc] = useState('')

  // Превью markdown
  const [editorTab, setEditorTab] = useState<EditorTab>('editor')
  const [preview, setPreview] = useState('')

  // Обложка: coverUrl — storage key, coverPresignedUrl — для отображения
  const [coverUrl, setCoverUrl] = useState<string | null>(null)
  const [coverPresignedUrl, setCoverPresignedUrl] = useState<string | null>(null)
  const [coverUploading, setCoverUploading] = useState(false)
  const coverInputRef = useRef<HTMLInputElement>(null)

  // Товары modal
  const [showProductsModal, setShowProductsModal] = useState(false)
  const [productSearch, setProductSearch] = useState('')
  const [productResults, setProductResults] = useState<ApiItemListEntry[]>([])
  const [productSearching, setProductSearching] = useState(false)

  // Новый тег
  const [newTagName, setNewTagName] = useState('')
  const [newTagSlug, setNewTagSlug] = useState('')
  const [creatingTag, setCreatingTag] = useState(false)

  const showSuccess = (msg: string) => {
    setSuccess(msg)
    setTimeout(() => setSuccess(null), 2500)
  }

  const load = useCallback(async () => {
    try {
      const [p, cats, tags] = await Promise.all([
        api.get<BlogPost>(`/blog/posts/${urlSlug}`),
        listCategories(),
        api.get<BlogTag[]>('/blog/tags'),
      ])
      setPost(p)
      setTitle(p.title)
      setContent(p.content ?? '')
      setShortDesc(p.short_description ?? '')
      setCategoryId(p.category_id ?? '')
      setSeoTitle(p.seo_title ?? '')
      setSeoDesc(p.seo_description ?? '')
      setCoverUrl(p.cover_image_url)
      setCategories(cats)
      setAllTags(tags)
    } catch {
      router.replace('/admin/blog')
    } finally {
      setLoading(false)
    }
  }, [urlSlug, router])

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
    load()
  }, [user, isLoading, router, load])

  // Превью markdown
  useEffect(() => {
    if (editorTab !== 'preview' || !content) { setPreview(''); return }
    renderMarkdown(content).then(setPreview)
  }, [editorTab, content])

  // Резолв presigned URL для превью обложки
  useEffect(() => {
    if (!coverUrl) { setCoverPresignedUrl(null); return }
    getPresignedUrls([coverUrl])
      .then((urls) => setCoverPresignedUrl(urls[coverUrl] ?? null))
      .catch(() => {})
  }, [coverUrl])

  // Поиск товаров в модалке
  useEffect(() => {
    if (!showProductsModal) return
    setProductSearching(true)
    listItems({ search: productSearch || undefined, category_id: categoryId || undefined, is_published: true, limit: 20 })
      .then((r) => setProductResults(r.items))
      .catch(() => setProductResults([]))
      .finally(() => setProductSearching(false))
  }, [showProductsModal, productSearch, categoryId])

  const handleSave = async () => {
    if (!post) return
    setSaving(true)
    setError(null)
    try {
      await updateBlogPost(urlSlug, {
        title: title.trim(),
        short_description: shortDesc.trim() || null,
        content: content || null,
        cover_image_url: coverUrl,
        category_id: categoryId || null,
        seo_title: seoTitle.trim() || null,
        seo_description: seoDesc.trim() || null,
      })
      showSuccess('Сохранено')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  const handleTogglePublish = async () => {
    if (!post) return
    setSaving(true)
    setError(null)
    try {
      if (post.status === 'published') {
        await unpublishBlogPost(urlSlug)
        showSuccess('Снято с публикации')
      } else {
        await publishBlogPost(urlSlug)
        showSuccess('Опубликовано!')
      }
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  const handleCoverUpload = async (file: File) => {
    setCoverUploading(true)
    try {
      const result = await uploadBlogCover(urlSlug, file)
      setCoverUrl(result.key)
      showSuccess('Обложка загружена')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setCoverUploading(false)
    }
  }

  const handleAddTag = async (tagId: string) => {
    if (!post) return
    if (post.tags.some((t) => t.id === tagId)) return
    try {
      await addBlogPostTag(urlSlug, tagId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка добавления тега')
    }
  }

  const handleRemoveTag = async (tagId: string) => {
    try {
      await removeBlogPostTag(urlSlug, tagId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка удаления тега')
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim() || !newTagSlug.trim()) return
    setCreatingTag(true)
    try {
      const tag = await createBlogTag({ name: newTagName.trim(), slug: newTagSlug.trim() })
      setAllTags((prev) => [...prev, tag])
      await handleAddTag(tag.id)
      setNewTagName('')
      setNewTagSlug('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка создания тега')
    } finally {
      setCreatingTag(false)
    }
  }

  const handleLinkProduct = async (productId: string) => {
    if (!post) return
    if (post.product_links.some((l) => l.product_id === productId)) return
    try {
      await linkProduct(urlSlug, { product_id: productId, display_order: post.product_links.length })
      await load()
      showSuccess('Товар добавлен')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка')
    }
  }

  const handleUnlinkProduct = async (linkId: string) => {
    try {
      await unlinkProduct(urlSlug, linkId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка')
    }
  }

  if (isLoading || loading) return <Spinner />
  if (!post) return null

  const linkedProductIds = new Set(post.product_links.map((l) => l.product_id))
  const availableTags = allTags.filter((t) => !post.tags.some((pt) => pt.id === t.id))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <Link href="/admin/blog" className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <h1 className="text-xl font-bold text-gray-900 truncate max-w-lg">{post.title}</h1>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${
            post.status === 'published' ? 'bg-green-50 text-green-700 border-green-200'
            : post.status === 'archived' ? 'bg-gray-100 text-gray-500 border-gray-200'
            : 'bg-yellow-50 text-yellow-700 border-yellow-200'
          }`}>
            {post.status === 'published' ? 'Опубликован' : post.status === 'archived' ? 'Архив' : 'Черновик'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {post.status === 'published' && (
            <Link href={`/blog/${post.slug}`} target="_blank" className="px-3 py-2 text-xs text-gray-500 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
              Открыть →
            </Link>
          )}
          <button
            onClick={handleTogglePublish}
            disabled={saving}
            className={`px-4 py-2 text-sm font-medium rounded-xl border transition-colors disabled:opacity-50 ${
              post.status === 'published'
                ? 'border-yellow-200 text-yellow-700 hover:bg-yellow-50'
                : 'border-green-200 text-green-700 hover:bg-green-50'
            }`}
          >
            {post.status === 'published' ? 'Снять с публикации' : 'Опубликовать'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {saving ? 'Сохранение…' : 'Сохранить'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>
      )}
      {success && (
        <div className="mb-4 px-4 py-3 bg-green-50 border border-green-200 rounded-xl text-sm text-green-700">{success}</div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* ── Левая колонка: основной контент ── */}
        <div className="xl:col-span-2 space-y-5">

          {/* Заголовок */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Заголовок</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
            />
          </div>

          {/* Краткое описание */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Краткое описание</label>
            <textarea
              value={shortDesc}
              onChange={(e) => setShortDesc(e.target.value)}
              rows={3}
              className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm resize-none focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
            />
          </div>

          {/* Markdown редактор */}
          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
            <div className="flex border-b border-gray-100">
              {(['editor', 'preview'] as EditorTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setEditorTab(tab)}
                  className={`px-5 py-3 text-sm font-medium transition-colors ${
                    editorTab === tab
                      ? 'text-indigo-700 border-b-2 border-indigo-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab === 'editor' ? 'Редактор' : 'Превью'}
                </button>
              ))}
            </div>
            {editorTab === 'editor' ? (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="# Заголовок статьи&#10;&#10;Начните писать markdown…"
                className="w-full h-96 px-5 py-4 font-mono text-sm resize-none focus:outline-none"
              />
            ) : preview ? (
              <MarkdownContent
                html={preview}
                className="min-h-96 px-5 py-4 prose prose-sm max-w-none"
              />
            ) : (
              <div className="min-h-96 px-5 py-4 flex items-start">
                <p className="text-gray-400 italic text-sm">Нет контента для превью</p>
              </div>
            )}
          </div>
        </div>

        {/* ── Правая колонка: мета, теги, товары ── */}
        <div className="space-y-5">

          {/* Обложка */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Обложка</h3>
            {coverUrl ? (
              <div className="relative">
                <img src={coverPresignedUrl ?? undefined} alt="cover" className="w-full h-40 object-cover rounded-xl" />
                <button
                  onClick={() => coverInputRef.current?.click()}
                  className="mt-2 w-full text-xs text-center text-indigo-600 hover:text-indigo-800"
                >
                  Заменить
                </button>
              </div>
            ) : (
              <button
                onClick={() => coverInputRef.current?.click()}
                disabled={coverUploading}
                className="w-full h-32 flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 text-gray-400 hover:border-indigo-300 hover:text-indigo-500 transition-colors disabled:opacity-50"
              >
                {coverUploading ? (
                  <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <>
                    <svg className="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-xs">Загрузить обложку</span>
                  </>
                )}
              </button>
            )}
            <input
              ref={coverInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleCoverUpload(f) }}
            />
          </div>

          {/* Категория */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Категория</h3>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400 bg-white"
            >
              <option value="">— Без категории —</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          {/* Теги */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Теги</h3>

            {/* Текущие теги */}
            {post.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {post.tags.map((t) => (
                  <span key={t.id} className="flex items-center gap-1 px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs rounded-full">
                    #{t.name}
                    <button onClick={() => handleRemoveTag(t.id)} className="ml-0.5 text-indigo-400 hover:text-indigo-700">×</button>
                  </span>
                ))}
              </div>
            )}

            {/* Добавить существующий тег */}
            {availableTags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {availableTags.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => handleAddTag(t.id)}
                    className="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs rounded-full hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                  >
                    + #{t.name}
                  </button>
                ))}
              </div>
            )}

            {/* Создать новый тег */}
            <div className="border-t border-gray-100 pt-3 mt-2">
              <p className="text-xs text-gray-400 mb-2">Создать новый тег</p>
              <div className="flex gap-2">
                <input
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="Название"
                  className="flex-1 min-w-0 px-3 py-1.5 rounded-lg border border-gray-200 text-xs focus:outline-none focus:border-indigo-400"
                />
                <input
                  value={newTagSlug}
                  onChange={(e) => setNewTagSlug(e.target.value)}
                  placeholder="slug"
                  className="w-24 px-3 py-1.5 rounded-lg border border-gray-200 text-xs font-mono focus:outline-none focus:border-indigo-400"
                />
                <button
                  onClick={handleCreateTag}
                  disabled={creatingTag || !newTagName.trim() || !newTagSlug.trim()}
                  className="px-3 py-1.5 bg-indigo-600 text-white text-xs rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  +
                </button>
              </div>
            </div>
          </div>

          {/* SEO */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">SEO</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs text-gray-500">Title</label>
                  <span className={`text-xs ${seoTitle.length > 60 ? 'text-red-500' : 'text-gray-400'}`}>{seoTitle.length}/60</span>
                </div>
                <input
                  value={seoTitle}
                  onChange={(e) => setSeoTitle(e.target.value)}
                  placeholder={title}
                  className="w-full px-3 py-2 rounded-xl border border-gray-200 text-xs focus:outline-none focus:border-indigo-400"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs text-gray-500">Description</label>
                  <span className={`text-xs ${seoDesc.length > 160 ? 'text-red-500' : 'text-gray-400'}`}>{seoDesc.length}/160</span>
                </div>
                <textarea
                  value={seoDesc}
                  onChange={(e) => setSeoDesc(e.target.value)}
                  placeholder={shortDesc}
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl border border-gray-200 text-xs resize-none focus:outline-none focus:border-indigo-400"
                />
              </div>
            </div>
          </div>

          {/* Товары */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-700">Товары из статьи</h3>
              <button
                onClick={() => setShowProductsModal(true)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
              >
                + Добавить
              </button>
            </div>
            {post.product_links.length === 0 ? (
              <p className="text-xs text-gray-400">Нет связанных товаров</p>
            ) : (
              <ul className="space-y-2">
                {post.product_links
                  .sort((a, b) => a.display_order - b.display_order)
                  .map((link) => (
                    <li key={link.id} className="flex items-center justify-between gap-2 text-xs text-gray-600">
                      <span className="font-mono truncate text-gray-400">{link.product_id.slice(0, 8)}…</span>
                      <button
                        onClick={() => handleUnlinkProduct(link.id)}
                        className="text-red-400 hover:text-red-600 shrink-0"
                      >
                        Удалить
                      </button>
                    </li>
                  ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* ── Modal: добавление товаров ── */}
      {showProductsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
              <h2 className="font-semibold text-gray-900">Добавить товар</h2>
              <button onClick={() => setShowProductsModal(false)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
            </div>
            <div className="p-4">
              <input
                value={productSearch}
                onChange={(e) => setProductSearch(e.target.value)}
                placeholder="Поиск товара…"
                className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-indigo-400"
              />
            </div>
            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
              {productSearching ? (
                <p className="text-center text-sm text-gray-400 py-6">Поиск…</p>
              ) : productResults.length === 0 ? (
                <p className="text-center text-sm text-gray-400 py-6">Ничего не найдено</p>
              ) : (
                productResults.map((item) => {
                  const already = linkedProductIds.has(item.id)
                  return (
                    <div
                      key={item.id}
                      className={`flex items-center justify-between gap-3 px-4 py-3 rounded-xl border transition-colors ${
                        already ? 'border-green-200 bg-green-50' : 'border-gray-200 hover:border-indigo-200'
                      }`}
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                        <p className="text-xs text-gray-400 truncate">{item.short_description}</p>
                      </div>
                      {already ? (
                        <span className="text-xs text-green-600 shrink-0">Добавлен</span>
                      ) : (
                        <button
                          onClick={() => handleLinkProduct(item.id)}
                          className="px-3 py-1.5 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 shrink-0 transition-colors"
                        >
                          + Добавить
                        </button>
                      )}
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
