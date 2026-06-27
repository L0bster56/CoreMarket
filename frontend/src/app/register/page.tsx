'use client'

import Link from 'next/link'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

interface FormErrors {
  username?: string
  email?: string
  password?: string
  confirm?: string
  general?: string
}

function validate(username: string, email: string, password: string, confirm: string): FormErrors {
  const errors: FormErrors = {}
  if (!username) {
    errors.username = 'Введите имя пользователя'
  } else if (username.length < 3) {
    errors.username = 'Минимум 3 символа'
  }
  if (!email) {
    errors.email = 'Введите email'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = 'Неверный формат email'
  }
  if (!password) {
    errors.password = 'Введите пароль'
  } else if (password.length < 8) {
    errors.password = 'Минимум 8 символов'
  }
  if (!confirm) {
    errors.confirm = 'Подтвердите пароль'
  } else if (password !== confirm) {
    errors.confirm = 'Пароли не совпадают'
  }
  return errors
}

export default function RegisterPage() {
  const router = useRouter()
  const { register } = useAuth()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [errors, setErrors] = useState<FormErrors>({})
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const errs = validate(username, email, password, confirm)
    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      return
    }
    setErrors({})
    setLoading(true)
    try {
      await register(username, email, password)
      router.push('/login')
    } catch (err) {
      setErrors({ general: err instanceof Error ? err.message : 'Ошибка регистрации' })
    } finally {
      setLoading(false)
    }
  }

  const field = (
    id: string,
    label: string,
    type: string,
    value: string,
    onChange: (v: string) => void,
    placeholder: string,
    error?: string,
  ) => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={loading}
        className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-60 ${
          error ? 'border-red-400 bg-red-50' : 'border-gray-300'
        }`}
      />
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  )

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold">CM</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Создать аккаунт</h1>
          <p className="text-gray-500 text-sm mt-1">
            Уже есть аккаунт?{' '}
            <Link href="/login" className="text-indigo-600 hover:underline font-medium">
              Войти
            </Link>
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          noValidate
          className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 space-y-5"
        >
          {errors.general && (
            <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
              {errors.general}
            </div>
          )}

          {field('username', 'Имя пользователя', 'text', username, setUsername, 'username', errors.username)}
          {field('email', 'Email', 'email', email, setEmail, 'you@example.com', errors.email)}
          {field('password', 'Пароль', 'password', password, setPassword, 'Минимум 8 символов', errors.password)}
          {field('confirm', 'Подтвердить пароль', 'password', confirm, setConfirm, '••••••••', errors.confirm)}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-xl transition-colors text-sm flex items-center justify-center gap-2"
          >
            {loading && (
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
            )}
            {loading ? 'Регистрируем...' : 'Зарегистрироваться'}
          </button>
        </form>
      </div>
    </div>
  )
}
