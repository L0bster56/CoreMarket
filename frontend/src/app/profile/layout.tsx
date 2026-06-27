import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Профиль',
  description: 'Управление аккаунтом CoreMarket',
  robots: { index: false, follow: false },
}

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children
}
