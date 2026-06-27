'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { listCategories, createCategory, deleteCategory } from '@/services/categories'
import { listTags, createTag, deleteTag } from '@/services/tags'
import { listItems, updateItem, deleteItem } from '@/services/items'
import type { Category, Tag, ApiItemListEntry } from '@/types'

type Tab = 'items' | 'categories' | 'tags'

function Spinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

// ─────────────────────────── Items Tab ───────────────────────────

interface ItemsTabProps {
  items: ApiItemListEntry[]
  categories: Category[]
  onRefresh: () => Promise<void>
}

function ItemsTab({ items, categories, onRefresh }: ItemsTabProps) {
  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c.name]))
  const handleTogglePublish = async (item: ApiItemListEntry) => {
    try {
      await updateItem(item.id, { is_published: !item.is_published })
      await onRefresh()
    } catch {
      // silent
    }
  }

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Удалить «${title}»?`)) return
    try {
      await deleteItem(id)
      await onRefresh()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка удаления')
    }
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Объекты ({items.length})</h2>
        <Link
          href="/admin/items/new"
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Добавить объект
        </Link>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Объект</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Категория</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Статус</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Действия</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center py-8 text-gray-400 text-sm">
                    Объектов нет
                  </td>
                </tr>
              )}
              {items.map((item) => (
                  <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <Link
                          href={`/items/${item.id}`}
                          className="font-medium text-gray-900 hover:text-indigo-600 line-clamp-1"
                        >
                          {item.title}
                        </Link>
                        <p className="text-xs text-gray-400 line-clamp-1 mt-0.5">{item.short_description}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">{categoryMap[item.category_id] ?? item.category_id.slice(0, 8) + '…'}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleTogglePublish(item)}
                        className={`px-2 py-0.5 rounded-full text-xs font-medium transition-colors ${
                          item.is_published
                            ? 'bg-green-100 text-green-700 hover:bg-green-200'
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                        }`}
                      >
                        {item.is_published ? 'Опубликован' : 'Черновик'}
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <Link
                          href={`/admin/items/${item.id}/edit`}
                          className="text-xs text-indigo-600 hover:underline"
                        >
                          Изменить
                        </Link>
                        <button
                          onClick={() => handleDelete(item.id, item.title)}
                          className="text-xs text-red-500 hover:underline"
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
    </section>
  )
}

// ─────────────────────────── Categories Tab ───────────────────────────

interface CategoriesTabProps {
  categories: Category[]
  onRefresh: () => Promise<void>
}

function CategoriesTab({ categories, onRefresh }: CategoriesTabProps) {
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCreate = async () => {
    if (!name.trim() || !slug.trim()) {
      setError('Название и slug обязательны')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await createCategory({ name: name.trim(), slug: slug.trim(), description: description.trim() || undefined })
      setName('')
      setSlug('')
      setDescription('')
      setShowCreate(false)
      await onRefresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка создания')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string, catName: string) => {
    if (!confirm(`Удалить категорию «${catName}»?`)) return
    try {
      await deleteCategory(id)
      await onRefresh()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка удаления')
    }
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Категории ({categories.length})</h2>
        <button
          onClick={() => { setShowCreate(!showCreate); setError(null) }}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Добавить категорию
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Новая категория</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Название <span className="text-red-500">*</span>
              </label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Электроника"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Slug <span className="text-red-500">*</span>
              </label>
              <input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 font-mono"
                placeholder="electronics"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-gray-600 mb-1">Описание</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Необязательно"
              />
            </div>
          </div>
          {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleCreate}
              disabled={submitting}
              className="px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? 'Создание…' : 'Создать'}
            </button>
            <button
              onClick={() => { setShowCreate(false); setError(null) }}
              className="px-5 py-2 border border-gray-200 text-sm rounded-xl hover:bg-gray-50 transition-colors"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Название</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Slug</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Действия</th>
            </tr>
          </thead>
          <tbody>
            {categories.length === 0 && (
              <tr>
                <td colSpan={3} className="text-center py-8 text-gray-400 text-sm">Категорий нет</td>
              </tr>
            )}
            {categories.map((cat) => (
              <tr key={cat.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3 font-medium text-gray-900">{cat.name}</td>
                <td className="px-4 py-3 text-gray-500 font-mono text-xs">{cat.slug}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleDelete(cat.id, cat.name)}
                    className="text-xs text-red-500 hover:underline"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

// ─────────────────────────── Tags Tab ───────────────────────────

interface TagsTabProps {
  tags: Tag[]
  onRefresh: () => Promise<void>
}

function TagsTab({ tags, onRefresh }: TagsTabProps) {
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCreate = async () => {
    if (!name.trim() || !slug.trim()) {
      setError('Название и slug обязательны')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await createTag({ name: name.trim(), slug: slug.trim() })
      setName('')
      setSlug('')
      setShowCreate(false)
      await onRefresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка создания')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string, tagName: string) => {
    if (!confirm(`Удалить тег «${tagName}»?`)) return
    try {
      await deleteTag(id)
      await onRefresh()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Ошибка удаления')
    }
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Теги ({tags.length})</h2>
        <button
          onClick={() => { setShowCreate(!showCreate); setError(null) }}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Добавить тег
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">Новый тег</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Название <span className="text-red-500">*</span>
              </label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Смартфон"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Slug <span className="text-red-500">*</span>
              </label>
              <input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 font-mono"
                placeholder="smartphone"
              />
            </div>
          </div>
          {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleCreate}
              disabled={submitting}
              className="px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {submitting ? 'Создание…' : 'Создать'}
            </button>
            <button
              onClick={() => { setShowCreate(false); setError(null) }}
              className="px-5 py-2 border border-gray-200 text-sm rounded-xl hover:bg-gray-50 transition-colors"
            >
              Отмена
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        {tags.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-4">Тегов нет</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <div
                key={tag.id}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-full"
              >
                <Link
                  href={`/tags/${tag.slug}`}
                  className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
                >
                  #{tag.name}
                </Link>
                <button
                  onClick={() => handleDelete(tag.id, tag.name)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                  aria-label={`Удалить тег ${tag.name}`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

// ─────────────────────────── Page ───────────────────────────

export default function AdminPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const [activeTab, setActiveTab] = useState<Tab>('items')
  const [items, setItems] = useState<ApiItemListEntry[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
  }, [user, isLoading, router])

  const loadData = useCallback(async () => {
    setDataLoading(true)
    setLoadError(null)
    try {
      const [itemsRes, catsRes, tagsRes] = await Promise.all([
        listItems({ limit: 100 }),
        listCategories(),
        listTags(),
      ])
      setItems(itemsRes.items)
      setCategories(catsRes)
      setTags(tagsRes)
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : 'Ошибка загрузки данных')
    } finally {
      setDataLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!isLoading && user?.role === 'admin') {
      loadData()
    }
  }, [isLoading, user])

  const tabs = useMemo<{ id: Tab; label: string }[]>(() => [
    { id: 'items', label: 'Объекты' },
    { id: 'categories', label: 'Категории' },
    { id: 'tags', label: 'Теги' },
  ], [])

  if (isLoading || (!user && !isLoading)) return null
  if (user?.role !== 'admin') return null

  if (dataLoading) return <Spinner />

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Админ-панель</h1>
        <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full">
          Администратор
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Объектов', value: items.length, color: 'text-indigo-600' },
          { label: 'Категорий', value: categories.length, color: 'text-green-600' },
          { label: 'Тегов', value: tags.length, color: 'text-amber-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-gray-200 p-5 text-center">
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
        <Link
          href="/admin/blog"
          className="bg-white rounded-2xl border border-gray-200 p-5 text-center hover:border-purple-300 hover:shadow-sm transition-all group"
        >
          <p className="text-3xl font-bold text-purple-600 group-hover:scale-110 transition-transform inline-block">✍</p>
          <p className="text-sm text-gray-500 mt-1">Блог</p>
        </Link>
      </div>

      {loadError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {loadError}
          <button onClick={loadData} className="ml-3 underline hover:no-underline">Повторить</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'items' && (
        <ItemsTab items={items} categories={categories} onRefresh={loadData} />
      )}
      {activeTab === 'categories' && (
        <CategoriesTab categories={categories} onRefresh={loadData} />
      )}
      {activeTab === 'tags' && (
        <TagsTab tags={tags} onRefresh={loadData} />
      )}
    </div>
  )
}
