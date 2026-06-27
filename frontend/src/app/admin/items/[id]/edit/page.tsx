'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { listCategories } from '@/services/categories'
import { listTags } from '@/services/tags'
import {
  getItem,
  updateItem,
  addCharacteristic,
  deleteCharacteristic,
  addGalleryImage,
  deleteGalleryImage,
  addItemTag,
  removeItemTag,
} from '@/services/items'
import { uploadFile } from '@/services/upload'
import { getPresignedUrls } from '@/services/storage'
import type { ApiItemDetail, Category, Tag } from '@/types'

interface LinkRow {
  key: number
  name: string
  url: string
  price: string
}

function Spinner() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

export default function EditItemPage() {
  const router = useRouter()
  const { id: itemId } = useParams<{ id: string }>()
  const { user, isLoading } = useAuth()

  const [item, setItem] = useState<ApiItemDetail | null>(null)
  const [categories, setCategories] = useState<Category[]>([])
  const [allTags, setAllTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Basic fields
  const [title, setTitle] = useState('')
  const [shortDesc, setShortDesc] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const [viewCount, setViewCount] = useState<number>(0)
  const [viewCountError, setViewCountError] = useState<string | null>(null)

  // Marketplace links
  const linkKeyRef = useRef(0)
  const [links, setLinks] = useState<LinkRow[]>([])

  // Gallery
  const galleryInputRef = useRef<HTMLInputElement>(null)
  const [uploadingImages, setUploadingImages] = useState(false)
  const [resolvedUrls, setResolvedUrls] = useState<Record<string, string>>({})

  // New characteristic inline form
  const [newCharGroup, setNewCharGroup] = useState('')
  const [newCharName, setNewCharName] = useState('')
  const [newCharValue, setNewCharValue] = useState('')
  const [addingChar, setAddingChar] = useState(false)

  const showSuccess = (msg: string) => {
    setSuccess(msg)
    setTimeout(() => setSuccess(null), 2500)
  }

  const load = useCallback(async () => {
    try {
      const [itemData, cats, tags] = await Promise.all([
        getItem(itemId),
        listCategories(),
        listTags(),
      ])
      setItem(itemData)
      setTitle(itemData.title)
      setShortDesc(itemData.short_description)
      setDescription(itemData.description)
      setCategoryId(itemData.category_id)
      setYoutubeUrl(itemData.youtube_url ?? '')
      setIsPublished(itemData.is_published)
      setViewCount(itemData.view_count)
      setLinks(
        itemData.marketplace_links.map((l) => ({
          key: linkKeyRef.current++,
          name: l.name,
          url: l.url,
          price: l.price ?? '',
        })),
      )
      setCategories(cats)
      setAllTags(tags)
    } catch {
      router.replace('/admin')
    } finally {
      setLoading(false)
    }
  }, [itemId, router])

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
    load()
  }, [user, isLoading, router, load])

  // Resolve gallery presigned URLs whenever gallery changes
  const galleryKeys = item?.gallery.map((g) => g.image_url).join(',') ?? ''
  useEffect(() => {
    if (!galleryKeys) { setResolvedUrls({}); return }
    getPresignedUrls(galleryKeys.split(',')).then(setResolvedUrls).catch(() => {})
  }, [galleryKeys])

  // ── Save basic fields + marketplace links + publish status ──

  const handleSave = async () => {
    if (!item) return
    if (!title.trim() || !shortDesc.trim() || !description.trim() || !categoryId) {
      setError('Заполните обязательные поля: название, краткое описание, описание, категория')
      return
    }
    const parsedViewCount = Number(viewCount)
    if (!Number.isInteger(parsedViewCount) || parsedViewCount < 1) {
      setViewCountError('Количество просмотров должно быть целым числом ≥ 1')
      return
    }
    setViewCountError(null)
    setSaving(true)
    setError(null)
    try {
      await updateItem(item.id, {
        title: title.trim(),
        short_description: shortDesc.trim(),
        description: description.trim(),
        category_id: categoryId,
        youtube_url: youtubeUrl.trim() || null,
        is_published: isPublished,
        view_count: parsedViewCount,
        marketplace_links: links
          .filter((l) => l.name.trim() && l.url.trim())
          .map((l) => ({ name: l.name.trim(), url: l.url.trim(), price: l.price.trim() || null })),
      })
      showSuccess('Сохранено')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  // ── Marketplace link rows ──

  const addLinkRow = () => {
    setLinks((prev) => [...prev, { key: linkKeyRef.current++, name: '', url: '', price: '' }])
  }

  const updateLinkRow = (key: number, field: keyof Omit<LinkRow, 'key'>, val: string) => {
    setLinks((prev) => prev.map((r) => (r.key === key ? { ...r, [field]: val } : r)))
  }

  const removeLinkRow = (key: number) => {
    setLinks((prev) => prev.filter((r) => r.key !== key))
  }

  // ── Characteristics (immediate) ──

  const handleAddChar = async () => {
    if (!item || !newCharName.trim() || !newCharValue.trim()) return
    setAddingChar(true)
    setError(null)
    try {
      await addCharacteristic(item.id, {
        name: newCharName.trim(),
        value: newCharValue.trim(),
        group: newCharGroup.trim() || null,
      })
      setNewCharGroup('')
      setNewCharName('')
      setNewCharValue('')
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка добавления характеристики')
    } finally {
      setAddingChar(false)
    }
  }

  const handleDeleteChar = async (charId: string) => {
    if (!item) return
    setError(null)
    try {
      await deleteCharacteristic(item.id, charId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка удаления характеристики')
    }
  }

  // ── Gallery (immediate) ──

  const handleGalleryUpload = async (files: File[]) => {
    if (!item || !files.length) return
    setUploadingImages(true)
    setError(null)
    try {
      for (const file of files) {
        const key = await uploadFile(file, 'items')
        await addGalleryImage(item.id, key)
      }
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки фото')
    } finally {
      setUploadingImages(false)
    }
  }

  const handleDeleteImage = async (imageId: string) => {
    if (!item) return
    setError(null)
    try {
      await deleteGalleryImage(item.id, imageId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка удаления фото')
    }
  }

  // ── Tags (immediate) ──

  const handleAddTag = async (tagId: string) => {
    if (!item) return
    setError(null)
    try {
      await addItemTag(item.id, tagId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка добавления тега')
    }
  }

  const handleRemoveTag = async (tagId: string) => {
    if (!item) return
    setError(null)
    try {
      await removeItemTag(item.id, tagId)
      await load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка удаления тега')
    }
  }

  if (isLoading || loading) return <Spinner />
  if (!item) return null

  const availableTags = allTags.filter((t) => !item.tags.some((it) => it.id === t.id))

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <Link href="/admin" className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <h1 className="text-xl font-bold text-gray-900 truncate max-w-lg">{item.title}</h1>
          <span className={`shrink-0 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
            item.is_published
              ? 'bg-green-50 text-green-700 border-green-200'
              : 'bg-yellow-50 text-yellow-700 border-yellow-200'
          }`}>
            {item.is_published ? 'Опубликован' : 'Черновик'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href={`/items/${item.id}`}
            target="_blank"
            className="px-3 py-2 text-xs text-gray-500 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
          >
            Открыть →
          </Link>
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

        {/* ── Left: main content (2/3) ── */}
        <div className="xl:col-span-2 space-y-5">

          {/* Basic fields */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Основные поля</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Название <span className="text-red-500">*</span>
                </label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Краткое описание <span className="text-red-500">*</span>
                </label>
                <input
                  value={shortDesc}
                  onChange={(e) => setShortDesc(e.target.value)}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Описание <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={6}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </div>
            </div>
          </div>

          {/* Characteristics */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Характеристики</h3>

            {item.characteristics.length > 0 && (
              <div className="mb-4 overflow-hidden rounded-xl border border-gray-100">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500">Группа</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500">Название</th>
                      <th className="text-left px-3 py-2 text-xs font-medium text-gray-500">Значение</th>
                      <th className="w-8" />
                    </tr>
                  </thead>
                  <tbody>
                    {item.characteristics.map((ch) => (
                      <tr key={ch.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50">
                        <td className="px-3 py-2 text-xs text-gray-400">{ch.group || '—'}</td>
                        <td className="px-3 py-2 text-xs text-gray-700">{ch.name}</td>
                        <td className="px-3 py-2 text-xs text-gray-900 font-medium">{ch.value}</td>
                        <td className="px-2 py-2 text-right">
                          <button
                            onClick={() => handleDeleteChar(ch.id)}
                            className="p-1 text-gray-300 hover:text-red-500 transition-colors rounded"
                            aria-label="Удалить"
                          >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="border-t border-gray-100 pt-4">
              <p className="text-xs text-gray-400 mb-2">Добавить характеристику</p>
              <div className="grid grid-cols-[1fr_1.5fr_1.5fr_auto] gap-2 items-end">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Группа</label>
                  <input
                    value={newCharGroup}
                    onChange={(e) => setNewCharGroup(e.target.value)}
                    placeholder="Общее"
                    className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Название *</label>
                  <input
                    value={newCharName}
                    onChange={(e) => setNewCharName(e.target.value)}
                    placeholder="Материал"
                    className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Значение *</label>
                  <input
                    value={newCharValue}
                    onChange={(e) => setNewCharValue(e.target.value)}
                    placeholder="Сталь"
                    className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                </div>
                <button
                  onClick={handleAddChar}
                  disabled={addingChar || !newCharName.trim() || !newCharValue.trim()}
                  className="px-3 py-2 bg-indigo-600 text-white text-xs font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors whitespace-nowrap"
                >
                  {addingChar ? '…' : '+ Добавить'}
                </button>
              </div>
            </div>
          </div>

          {/* Gallery */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-700">Галерея</h3>
                <p className="text-xs text-gray-400 mt-0.5">Первое фото — превью карточки.</p>
              </div>
              <button
                onClick={() => galleryInputRef.current?.click()}
                disabled={uploadingImages}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 text-xs font-medium rounded-lg hover:bg-indigo-100 disabled:opacity-50 transition-colors"
              >
                {uploadingImages ? 'Загрузка…' : '+ Добавить фото'}
              </button>
            </div>
            <input
              ref={galleryInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => {
                const files = Array.from(e.target.files ?? [])
                if (files.length) handleGalleryUpload(files)
                e.target.value = ''
              }}
            />

            {item.gallery.length === 0 ? (
              <button
                onClick={() => galleryInputRef.current?.click()}
                className="w-full border-2 border-dashed border-gray-200 rounded-xl py-10 flex flex-col items-center gap-2 hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors group"
              >
                <svg className="w-8 h-8 text-gray-300 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="text-sm text-gray-400">Нажмите, чтобы добавить фото</span>
              </button>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {item.gallery.map((img, idx) => (
                  <div key={img.id} className="relative group aspect-square rounded-xl overflow-hidden bg-gray-100">
                    {resolvedUrls[img.image_url] ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={resolvedUrls[img.image_url]}
                        alt={`фото ${idx + 1}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-gray-300 border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors" />
                    <button
                      onClick={() => handleDeleteImage(img.id)}
                      className="absolute top-1.5 right-1.5 p-1 bg-white/90 rounded-full text-gray-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all shadow-sm"
                      aria-label="Удалить фото"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                    {idx === 0 && (
                      <span className="absolute bottom-1.5 left-1.5 px-1.5 py-0.5 bg-indigo-600 text-white text-xs rounded-md">
                        Главное
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Right: sidebar (1/3) ── */}
        <div className="space-y-5">

          {/* Settings */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Настройки</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Категория <span className="text-red-500">*</span>
                </label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                >
                  <option value="">— Выберите —</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">YouTube URL</label>
                <input
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  placeholder="https://youtu.be/..."
                  className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="text-xs font-medium text-gray-600">Опубликован</span>
                <button
                  onClick={() => setIsPublished((prev) => !prev)}
                  className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                    isPublished ? 'bg-indigo-600' : 'bg-gray-200'
                  }`}
                  role="switch"
                  aria-checked={isPublished}
                >
                  <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                    isPublished ? 'translate-x-[19px]' : 'translate-x-[2px]'
                  }`} />
                </button>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Количество просмотров
                </label>
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={viewCount}
                  onChange={(e) => {
                    setViewCountError(null)
                    setViewCount(Number(e.target.value))
                  }}
                  className={`w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 ${
                    viewCountError
                      ? 'border-red-300 focus:ring-red-300'
                      : 'border-gray-200 focus:ring-indigo-300'
                  }`}
                />
                {viewCountError && (
                  <p className="mt-1 text-xs text-red-500">{viewCountError}</p>
                )}
              </div>
            </div>
          </div>

          {/* Marketplace Links */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-semibold text-gray-700">Маркетплейсы</h3>
              <button
                onClick={addLinkRow}
                className="px-2.5 py-1.5 bg-indigo-50 text-indigo-600 text-xs font-medium rounded-lg hover:bg-indigo-100 transition-colors"
              >
                + Добавить
              </button>
            </div>
            <p className="text-xs text-gray-400 mb-4">Сохраняются кнопкой «Сохранить»</p>

            {links.length === 0 ? (
              <div className="border-2 border-dashed border-gray-200 rounded-xl py-6 text-center">
                <p className="text-xs text-gray-400">Нет ссылок на маркетплейсы</p>
                <button
                  onClick={addLinkRow}
                  className="mt-1.5 text-xs text-indigo-500 hover:underline"
                >
                  Добавить первую
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {links.map((row) => (
                  <div key={row.key} className="p-3 bg-gray-50 rounded-xl space-y-2">
                    <div className="flex items-center gap-1.5">
                      <input
                        value={row.name}
                        onChange={(e) => updateLinkRow(row.key, 'name', e.target.value)}
                        placeholder="Название (Wildberries, Ozon…)"
                        className="flex-1 border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                      />
                      <button
                        onClick={() => removeLinkRow(row.key)}
                        className="p-1.5 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                        aria-label="Удалить"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <input
                      value={row.url}
                      onChange={(e) => updateLinkRow(row.key, 'url', e.target.value)}
                      placeholder="https://..."
                      className="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                    />
                    <input
                      value={row.price}
                      onChange={(e) => updateLinkRow(row.key, 'price', e.target.value)}
                      placeholder="Цена (необязательно, напр. 4 990 ₽)"
                      className="w-full border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Теги</h3>

            {item.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {item.tags.map((t) => (
                  <span key={t.id} className="flex items-center gap-1 px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs rounded-full">
                    #{t.name}
                    <button
                      onClick={() => handleRemoveTag(t.id)}
                      className="ml-0.5 text-indigo-400 hover:text-indigo-700 leading-none"
                      aria-label={`Удалить тег ${t.name}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}

            {availableTags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
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

            {item.tags.length === 0 && availableTags.length === 0 && (
              <p className="text-xs text-gray-400">Теги не найдены</p>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
