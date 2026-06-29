import type { NextConfig } from "next";
import path from "path";

const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
  },
]

const nextConfig: NextConfig = {
  cacheLife: {
    presigned: {
      stale: 300,
      revalidate: 2700,
      expire: 3300,
    },
    catalog: {
      stale: 60,
      revalidate: 300,
      expire: 3600,
    },
  },

  cacheHandlers: {
    remote: path.resolve('./cache-handlers/redis-handler.js'),
  },

  poweredByHeader: false,
  compress: true,

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },

  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'i.pravatar.cc' },
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'http', hostname: 'minio' },
    ],
    minimumCacheTTL: 3600,
  },

  experimental: {
    optimizePackageImports: [
      '@/components/ui',
      '@/components/layout',
      '@/services',
      '@/lib',
    ],
  },
};

export default nextConfig;
