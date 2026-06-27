function S({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-full ${className}`} />
}

function SBox({ className = '' }: { className?: string }) {
  return <div className={`skeleton rounded-2xl ${className}`} />
}

function CardSkeleton() {
  return (
    <div className="bg-white rounded-3xl overflow-hidden border border-gray-100/80 shadow-sm">
      <SBox className="h-52 !rounded-none" />
      <div className="p-5 space-y-3">
        <S className="h-4 w-4/5" />
        <S className="h-3 w-full" />
        <S className="h-3 w-2/3" />
        <div className="pt-3 border-t border-gray-50 flex justify-between">
          <S className="h-3 w-20" />
          <S className="h-3 w-10" />
        </div>
      </div>
    </div>
  )
}

export default function TagLoading() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 mb-6">
        <S className="h-3 w-16" />
        <S className="h-3 w-2 !rounded" />
        <S className="h-3 w-24" />
      </div>

      {/* Heading + badge */}
      <div className="flex items-center gap-3 mb-2">
        <S className="h-9 w-44" />
        <S className="h-7 w-20" />
      </div>
      <S className="h-3 w-28 mb-8" />

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    </div>
  )
}
