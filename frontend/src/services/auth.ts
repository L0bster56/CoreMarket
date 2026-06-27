import { api, setTokens, clearTokens } from '@/lib/api'
import type { User } from '@/types'

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function login(username: string, password: string): Promise<User> {
  const tokens = await api.post<TokenResponse>('/auth/login', { username, password })
  setTokens({ access_token: tokens.access_token, refresh_token: tokens.refresh_token })
  return api.get<User>('/auth/me')
}

export async function register(username: string, email: string, password: string): Promise<User> {
  return api.post<User>('/auth/register', { username, email, password })
}

export async function logout(): Promise<void> {
  try {
    await api.post<void>('/auth/logout', {})
  } finally {
    clearTokens()
  }
}

export async function getMe(): Promise<User> {
  return api.get<User>('/auth/me')
}

export async function updateMe(data: { username?: string; avatar_url?: string | null }): Promise<User> {
  return api.patch<User>('/auth/me', data)
}

export async function changePassword(old_password: string, new_password: string): Promise<void> {
  await api.patch<void>('/auth/change-password', { old_password, new_password })
}
