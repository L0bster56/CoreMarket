import type { Metadata, Viewport } from 'next'
import { Suspense } from 'react'
import { Geist } from 'next/font/google'
import './globals.css'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import Providers from '@/components/layout/Providers'
import { NavigationProgress } from '@/components/ui/NavigationProgress'

const geist = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
  display: 'swap',
  preload: true,
})

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000'
const SITE_NAME = 'CoreMarket'
const SITE_DESCRIPTION =
  'Каталог товаров с обзорами, характеристиками и рейтингами. Сравнивайте и выбирайте лучшее.'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#031E36',
}

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: SITE_NAME, template: `%s | ${SITE_NAME}` },
  description: SITE_DESCRIPTION,
  keywords: ['каталог', 'товары', 'обзоры', 'характеристики', 'рейтинги', 'CoreMarket'],
  authors: [{ name: 'CoreMarket' }],
  creator: 'CoreMarket',
  openGraph: {
    type: 'website',
    locale: 'ru_RU',
    url: SITE_URL,
    siteName: SITE_NAME,
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
  },
  twitter: {
    card: 'summary_large_image',
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" className={`${geist.variable} h-full`}>
      <body className="min-h-full flex flex-col antialiased">
        <Providers>
          <NavigationProgress />
          <Suspense fallback={<div className="h-16 border-b border-gray-100 bg-white" />}>
            <Header />
          </Suspense>
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
