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
  // ─── New Next.js 16 Cache Components (PPR) ────────────────────────────────
  // Enables 'use cache' directive, Partial Prerendering, and cacheLife/cacheTag APIs.
  // Pages remain compatible with the old `export const revalidate` / `force-dynamic`
  // patterns — migration is incremental.
  cacheComponents: true,

  // ─── Custom cache lifetimes ────────────────────────────────────────────────
  cacheLife: {
    // Presigned S3 URLs: valid for 2hr. Cache for 45min (well below 1hr buffer).
    // Used by storage.ts via 'use cache: remote'.
    presigned: {
      stale: 300,    // 5min client stale
      revalidate: 2700, // 45min server revalidation
      expire: 3300,  // 55min hard expire (keeps 5min safety margin under 1hr URL expiry)
    },
    // Catalog / product lists: change often but not per-second.
    catalog: {
      stale: 60,     // 1min client stale
      revalidate: 300, // 5min server revalidation
      expire: 3600,  // 1hr hard expire
    },
  },

  // ─── Redis remote cache handler ───────────────────────────────────────────
  // 'use cache: remote' stores entries in Redis (db 1).
  // Falls back gracefully to in-memory if REDIS_URL is not set or Redis is down.
  cacheHandlers: {
    remote: path.resolve('./cache-handlers/redis-handler.js'),
  },

  // ─── General ──────────────────────────────────────────────────────────────
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
