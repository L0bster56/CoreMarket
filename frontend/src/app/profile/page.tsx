'use client'

import Image from 'next/image'
import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import * as authService from '@/services/auth'

export default function ProfilePage() {
  const router = useRouter()
  const { user, isLoading, logout, setUser } = useAuth()
  const loggingOut = useRef(false)

  const [editUsername, setEditUsername] = useState('')
  const [editSaving, setEditSaving] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)
  const [editSuccess, setEditSuccess] = useState(false)

  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [pwSaving, setPwSaving] = useState(false)
  const [pwError, setPwError] = useState<string | null>(null)
  const [pwSuccess, setPwSuccess] = useState(false)

  useEffect(() => {
    if (isLoading || loggingOut.current) return
    if (!user) router.replace('/login')
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) setEditUsername(user.username)
  }, [user])

  if (isLoading || !user) return null

  async function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = editUsername.trim()
    if (!trimmed || trimmed === user!.username) return
    setEditSaving(true)
    setEditError(null)
    setEditSuccess(false)
    try {
      const updated = await authService.updateMe({ username: trimmed })
      setUser(updated)
      setEditSuccess(true)
    } catch (err) {
      setEditError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setEditSaving(false)
    }
  }

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!oldPassword || !newPassword) return
    if (newPassword.length < 8) {
      setPwError('Минимум 8 символов')
      return
    }
    setPwSaving(true)
    setPwError(null)
    setPwSuccess(false)
    try {
      await authService.changePassword(oldPassword, newPassword)
      setPwSuccess(true)
      setOldPassword('')
      setNewPassword('')
    } catch (err) {
      setPwError(err instanceof Error ? err.message : 'Ошибка смены пароля')
    } finally {
      setPwSaving(false)
    }
  }

  async function handleLogout() {
    loggingOut.current = true
    await logout()
    router.push('/')
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Профиль</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left column */}
        <div className="md:col-span-1 space-y-4">
          {/* User card */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 text-center">
            {user.avatar_url ? (
              <Image
                src={user.avatar_url}
                alt={user.username}
                width={80}
                height={80}
                className="rounded-full mx-auto"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-indigo-100 flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-indigo-600">
                  {user.username[0].toUpperCase()}
                </span>
              </div>
            )}
            <h2 className="mt-4 text-lg font-bold text-gray-900">{user.username}</h2>
            <p className="text-sm text-gray-500">{user.email}</p>
            <span className={`mt-2 inline-block px-3 py-1 rounded-full text-xs font-semibold ${
              user.role === 'admin'
                ? 'bg-red-100 text-red-700'
                : 'bg-indigo-100 text-indigo-700'
            }`}>
              {user.role === 'admin' ? 'Администратор' : 'Пользователь'}
            </span>
            <p className="mt-3 text-xs text-gray-400">
              Зарегистрирован: {new Date(user.created_at).toLocaleDateString('ru-RU')}
            </p>
            <button
              onClick={handleLogout}
              className="mt-4 w-full py-2 border border-red-200 text-red-600 hover:bg-red-50 text-sm font-medium rounded-xl transition-colors"
            >
              Выйти из аккаунта
            </button>
          </div>

          {/* Edit profile */}
          <form onSubmit={handleEditSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
            <h3 className="text-sm font-semibold text-gray-700">Редактировать профиль</h3>
            {editError && <p className="text-xs text-red-600">{editError}</p>}
            {editSuccess && <p className="text-xs text-green-600">Сохранено</p>}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Имя пользователя</label>
              <input
                value={editUsername}
                onChange={(e) => { setEditUsername(e.target.value); setEditSuccess(false) }}
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              disabled={editSaving || !editUsername.trim() || editUsername.trim() === user.username}
              className="w-full py-2 bg-indigo-600 text-white text-sm font-medium rounded-xl disabled:opacity-50 hover:bg-indigo-700 transition-colors"
            >
              {editSaving ? 'Сохраняем...' : 'Сохранить'}
            </button>
          </form>

          {/* Change password */}
          <form onSubmit={handlePasswordSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4">
            <h3 className="text-sm font-semibold text-gray-700">Сменить пароль</h3>
            {pwError && <p className="text-xs text-red-600">{pwError}</p>}
            {pwSuccess && <p className="text-xs text-green-600">Пароль изменён</p>}
            <div>
              <label className="block text-xs text-gray-500 mb-1">Текущий пароль</label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => { setOldPassword(e.target.value); setPwSuccess(false) }}
                autoComplete="current-password"
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Новый пароль</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => { setNewPassword(e.target.value); setPwSuccess(false) }}
                placeholder="Минимум 8 символов"
                autoComplete="new-password"
                className="w-full px-3 py-2 rounded-xl border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <button
              type="submit"
              disabled={pwSaving || !oldPassword || !newPassword}
              className="w-full py-2 bg-gray-800 text-white text-sm font-medium rounded-xl disabled:opacity-50 hover:bg-gray-900 transition-colors"
            >
              {pwSaving ? 'Меняем...' : 'Сменить пароль'}
            </button>
          </form>
        </div>

        {/* Right column */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-4">Информация об аккаунте</h3>
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Username</dt>
                <dd className="font-medium text-gray-900">{user.username}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Email</dt>
                <dd className="font-medium text-gray-900">{user.email}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Роль</dt>
                <dd className="font-medium text-gray-900">
                  {user.role === 'admin' ? 'Администратор' : 'Пользователь'}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Зарегистрирован</dt>
                <dd className="font-medium text-gray-900">
                  {new Date(user.created_at).toLocaleDateString('ru-RU')}
                </dd>
              </div>
            </dl>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-6">
            <h3 className="text-base font-semibold text-gray-900 mb-3">Активность</h3>
            <p className="text-sm text-gray-400">
              История комментариев и оценок появится в следующих фазах.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
