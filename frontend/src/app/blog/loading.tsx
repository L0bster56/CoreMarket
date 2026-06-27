function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function BlogCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm">
      <SBox className="h-48 !rounded-none" />
      <div className="p-5 space-y-3">
        <S className="h-3 w-20" />
        <S className="h-5 w-4/5" />
        <S className="h-4 w-3/5" />
        <S className="h-3 w-full" />
        <S className="h-3 w-5/6" />
        <div className="flex items-center gap-2 pt-1">
          <div className="skeleton w-6 h-6 rounded-full shrink-0" />
          <S className="h-3 w-28" />
        </div>
      </div>
    </div>
  )
}

export default function BlogLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <S className="h-8 w-24 mb-2" />
      <S className="h-3 w-48 mb-8" />

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <aside className="w-full lg:w-56 shrink-0 space-y-4">
          <div className="bg-white rounded-2xl p-4 border border-gray-100 space-y-2">
            <S className="h-3 w-2/3 mb-2" />
            {Array.from({ length: 5 }).map((_, i) => (
              <SBox key={i} className="h-9 !rounded-xl" />
            ))}
          </div>
          <div className="bg-white rounded-2xl p-4 border border-gray-100 space-y-2">
            <S className="h-3 w-1/2 mb-2" />
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <S key={i} className={`h-6 ${i % 3 === 0 ? 'w-16' : i % 3 === 1 ? 'w-20' : 'w-14'}`} />
              ))}
            </div>
          </div>
        </aside>

        {/* Posts grid */}
        <div className="flex-1 min-w-0">
          {/* Search bar */}
          <SBox className="h-11 w-full max-w-md mb-6 !rounded-xl" />
          <S className="h-3 w-32 mb-5" />
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <BlogCardSkeleton key={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
