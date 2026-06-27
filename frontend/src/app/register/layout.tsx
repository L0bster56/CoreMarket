import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Регистрация',
  description: 'Создайте аккаунт в CoreMarket',
  robots: { index: false, follow: false },
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return children
}
