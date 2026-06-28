'use client'

import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'
import type { User } from '@/types'
import * as authService from '@/services/auth'
import { getTokens, clearTokens } from '@/lib/api'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const tokens = getTokens()
    if (!tokens) {
      setIsLoading(false)
      return
    }
    authService.getMe()
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setIsLoading(false))
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const u = await authService.login(username, password)
    setUser(u)
  }, [])

  const register = useCallback(async (username: string, email: string, password: string) => {
    await authService.register(username, email, password)
  }, [])

  const logout = useCallback(async () => {
    await authService.logout()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ user, isLoading, login, register, logout, setUser }),
    [user, isLoading, login, register, logout],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
