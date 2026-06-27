function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function CardSkeleton() {
  return (
    <div className="bg-white rounded-3xl overflow-hidden border border-gray-100/80 shadow-sm">
      <SBox className="h-60 !rounded-none" />
      <div className="p-5 space-y-3">
        <S className="h-4 w-4/5" />
        <S className="h-3 w-full" />
        <S className="h-3 w-3/4" />
        <div className="pt-3 border-t border-gray-50 flex justify-between items-center">
          <S className="h-3 w-24" />
          <S className="h-3 w-10" />
        </div>
      </div>
    </div>
  )
}

function SidebarBlock({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 space-y-3">
      <S className="h-3 w-2/3 mb-1" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="skeleton w-4 h-4 rounded" />
          <S className={`h-3 ${i % 3 === 0 ? 'w-28' : i % 3 === 1 ? 'w-20' : 'w-24'}`} />
        </div>
      ))}
    </div>
  )
}

export default function CatalogLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <S className="h-8 w-40 mb-2" />
      <S className="h-3 w-56 mb-8" />

      {/* Search bar */}
      <SBox className="h-12 w-full max-w-2xl mb-6 !rounded-2xl" />

      {/* Layout */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <aside className="w-full lg:w-60 shrink-0 space-y-4">
          <SidebarBlock rows={6} />
          <SidebarBlock rows={4} />
          <SidebarBlock rows={3} />
        </aside>

        {/* Grid */}
        <div className="flex-1 min-w-0">
          <S className="h-3 w-32 mb-5" />
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
            {Array.from({ length: 9 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
