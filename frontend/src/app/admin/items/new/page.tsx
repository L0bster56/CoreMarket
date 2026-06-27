'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { listCategories } from '@/services/categories'
import { createItem, addGalleryImage, addCharacteristic } from '@/services/items'
import { uploadFile } from '@/services/upload'
import type { Category } from '@/types'

interface CharRow {
  key: number
  group: string
  name: string
  value: string
}

interface LinkRow {
  key: number
  name: string
  url: string
  price: string
}

interface GalleryEntry {
  key: number
  file: File
  preview: string
}

let rowKey = 0
let linkKey = 0
let galleryKey = 0

export default function NewItemPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  const [categories, setCategories] = useState<Category[]>([])
  const [catsLoading, setCatsLoading] = useState(true)

  // basic fields
  const [title, setTitle] = useState('')
  const [shortDesc, setShortDesc] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [youtubeUrl, setYoutubeUrl] = useState('')

  // characteristics
  const [chars, setChars] = useState<CharRow[]>([])

  // marketplace links
  const [links, setLinks] = useState<LinkRow[]>([])

  // gallery
  const [gallery, setGallery] = useState<GalleryEntry[]>([])
  const galleryInputRef = useRef<HTMLInputElement>(null)

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.replace('/login'); return }
    if (user.role !== 'admin') { router.replace('/'); return }
  }, [user, isLoading, router])

  useEffect(() => {
    if (!isLoading && user?.role === 'admin') {
      listCategories()
        .then(setCategories)
        .finally(() => setCatsLoading(false))
    }
  }, [isLoading, user])

  // ── Характеристики ──────────────────────────────────────────────

  const addCharRow = () => {
    setChars((prev) => [...prev, { key: rowKey++, group: '', name: '', value: '' }])
  }

  const updateCharRow = (key: number, field: keyof Omit<CharRow, 'key'>, val: string) => {
    setChars((prev) => prev.map((r) => (r.key === key ? { ...r, [field]: val } : r)))
  }

  const removeCharRow = (key: number) => {
    setChars((prev) => prev.filter((r) => r.key !== key))
  }

  // ── Ссылки на маркетплейсы ──────────────────────────────────────

  const addLinkRow = () => {
    setLinks((prev) => [...prev, { key: linkKey++, name: '', url: '', price: '' }])
  }

  const updateLinkRow = (key: number, field: keyof Omit<LinkRow, 'key'>, val: string) => {
    setLinks((prev) => prev.map((r) => (r.key === key ? { ...r, [field]: val } : r)))
  }

  const removeLinkRow = (key: number) => {
    setLinks((prev) => prev.filter((r) => r.key !== key))
  }

  // ── Галерея ─────────────────────────────────────────────────────

  const handleGalleryFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    if (!files.length) return
    const entries: GalleryEntry[] = files.map((file) => ({
      key: galleryKey++,
      file,
      preview: URL.createObjectURL(file),
    }))
    setGallery((prev) => [...prev, ...entries])
    e.target.value = ''
  }

  const removeGalleryEntry = (key: number) => {
    setGallery((prev) => {
      const entry = prev.find((e) => e.key === key)
      if (entry) URL.revokeObjectURL(entry.preview)
      return prev.filter((e) => e.key !== key)
    })
  }

  // ── Submit ───────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!title.trim() || !shortDesc.trim() || !description.trim() || !categoryId) {
      setError('Заполните обязательные поля: название, краткое описание, описание, категория')
      return
    }
    const badChar = chars.find((r) => !r.name.trim() || !r.value.trim())
    if (badChar) {
      setError('У каждой характеристики должны быть заполнены название и значение')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      const created = await createItem({
        title: title.trim(),
        short_description: shortDesc.trim(),
        description: description.trim(),
        category_id: categoryId,
        youtube_url: youtubeUrl.trim() || null,
        marketplace_links: links
          .filter((l) => l.name.trim() && l.url.trim())
          .map((l) => ({ name: l.name.trim(), url: l.url.trim(), price: l.price.trim() || null })),
      })

      await Promise.all(
        chars.map((r) =>
          addCharacteristic(created.id, {
            name: r.name.trim(),
            value: r.value.trim(),
            group: r.group.trim() || null,
          }),
        ),
      )

      for (const entry of gallery) {
        const url = await uploadFile(entry.file, 'items')
        await addGalleryImage(created.id, url)
      }

      router.push('/admin')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка создания объекта')
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading || !user) return null
  if (user.role !== 'admin') return null

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Link
          href="/admin"
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Назад
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Новый объект</h1>
      </div>

      <div className="space-y-8">
        {/* ── Основные поля ── */}
        <section className="bg-white rounded-2xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Основные поля</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Название <span className="text-red-500">*</span>
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Название объекта"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Краткое описание <span className="text-red-500">*</span>
              </label>
              <input
                value={shortDesc}
                onChange={(e) => setShortDesc(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Одно предложение"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Описание <span className="text-red-500">*</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={5}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
                placeholder="Полное описание"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Категория <span className="text-red-500">*</span>
                </label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  disabled={catsLoading}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300 disabled:opacity-50"
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
                  className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  placeholder="https://youtu.be/..."
                />
              </div>
            </div>
          </div>
        </section>

        {/* ── Характеристики ── */}
        <section className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-gray-800">Характеристики</h2>
              <p className="text-xs text-gray-400 mt-0.5">Группа необязательна. Название и значение обязательны.</p>
            </div>
            <button
              type="button"
              onClick={addCharRow}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 text-sm font-medium rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Добавить строку
            </button>
          </div>

          {chars.length === 0 ? (
            <div className="border-2 border-dashed border-gray-200 rounded-xl py-8 text-center">
              <p className="text-sm text-gray-400">Характеристик пока нет</p>
              <button
                type="button"
                onClick={addCharRow}
                className="mt-2 text-sm text-indigo-500 hover:underline"
              >
                Добавить первую
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {/* header */}
              <div className="grid grid-cols-[1fr_1.5fr_1.5fr_auto] gap-2 px-1">
                <span className="text-xs font-medium text-gray-400">Группа</span>
                <span className="text-xs font-medium text-gray-400">Название <span className="text-red-400">*</span></span>
                <span className="text-xs font-medium text-gray-400">Значение <span className="text-red-400">*</span></span>
                <span />
              </div>

              {chars.map((row) => (
                <div key={row.key} className="grid grid-cols-[1fr_1.5fr_1.5fr_auto] gap-2 items-center">
                  <input
                    value={row.group}
                    onChange={(e) => updateCharRow(row.key, 'group', e.target.value)}
                    placeholder="Общее"
                    className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                  <input
                    value={row.name}
                    onChange={(e) => updateCharRow(row.key, 'name', e.target.value)}
                    placeholder="Материал"
                    className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                  <input
                    value={row.value}
                    onChange={(e) => updateCharRow(row.key, 'value', e.target.value)}
                    placeholder="Сталь"
                    className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                  <button
                    type="button"
                    onClick={() => removeCharRow(row.key)}
                    className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                    aria-label="Удалить строку"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Ссылки на маркетплейсы ── */}
        <section className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-gray-800">Ссылки на маркетплейсы</h2>
              <p className="text-xs text-gray-400 mt-0.5">Название и URL обязательны, цена — нет.</p>
            </div>
            <button
              type="button"
              onClick={addLinkRow}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 text-sm font-medium rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Добавить ссылку
            </button>
          </div>

          {links.length === 0 ? (
            <div className="border-2 border-dashed border-gray-200 rounded-xl py-8 text-center">
              <p className="text-sm text-gray-400">Ссылок пока нет</p>
              <button type="button" onClick={addLinkRow} className="mt-2 text-sm text-indigo-500 hover:underline">
                Добавить первую
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {links.map((row) => (
                <div key={row.key} className="p-3 bg-gray-50 rounded-xl space-y-2">
                  <div className="flex items-center gap-2">
                    <input
                      value={row.name}
                      onChange={(e) => updateLinkRow(row.key, 'name', e.target.value)}
                      placeholder="Название (Wildberries, Ozon…)"
                      className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                    />
                    <button
                      type="button"
                      onClick={() => removeLinkRow(row.key)}
                      className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                      aria-label="Удалить ссылку"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <input
                    value={row.url}
                    onChange={(e) => updateLinkRow(row.key, 'url', e.target.value)}
                    placeholder="https://..."
                    className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                  />
                  <input
                    value={row.price}
                    onChange={(e) => updateLinkRow(row.key, 'price', e.target.value)}
                    placeholder="Цена (необязательно, напр. 4 990 ₽)"
                    className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                  />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* ── Галерея ── */}
        <section className="bg-white rounded-2xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-gray-800">Галерея</h2>
              <p className="text-xs text-gray-400 mt-0.5">Можно выбрать несколько фото сразу.</p>
            </div>
            <button
              type="button"
              onClick={() => galleryInputRef.current?.click()}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 text-sm font-medium rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Добавить фото
            </button>
          </div>

          <input
            ref={galleryInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleGalleryFiles}
            className="hidden"
          />

          {gallery.length === 0 ? (
            <button
              type="button"
              onClick={() => galleryInputRef.current?.click()}
              className="w-full border-2 border-dashed border-gray-200 rounded-xl py-10 flex flex-col items-center gap-2 hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors group"
            >
              <svg className="w-8 h-8 text-gray-300 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm text-gray-400 group-hover:text-indigo-500 transition-colors">
                Нажмите, чтобы выбрать фото
              </span>
            </button>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {gallery.map((entry, idx) => (
                <div key={entry.key} className="relative group aspect-square rounded-xl overflow-hidden bg-gray-100">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={entry.preview}
                    alt={`фото ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors" />
                  <button
                    type="button"
                    onClick={() => removeGalleryEntry(entry.key)}
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
              <button
                type="button"
                onClick={() => galleryInputRef.current?.click()}
                className="aspect-square rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-1 hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors group"
              >
                <svg className="w-6 h-6 text-gray-300 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-xs text-gray-400">Ещё</span>
              </button>
            </div>
          )}
        </section>

        {/* ── Ошибка + кнопки ── */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            className="flex-1 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm"
          >
            {submitting ? 'Создание…' : 'Создать объект'}
          </button>
          <Link
            href="/admin"
            className="px-6 py-3 border border-gray-200 text-sm font-medium rounded-xl hover:bg-gray-50 transition-colors text-gray-700"
          >
            Отмена
          </Link>
        </div>
      </div>
    </div>
  )
}
