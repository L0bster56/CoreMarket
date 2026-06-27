export default function RecommendedProductsSkeleton() {
  return (
    <section className="mt-14">
      <div className="mb-6 space-y-2">
        <div className="h-7 w-56 bg-gray-200 rounded-xl animate-pulse" />
        <div className="h-4 w-80 bg-gray-100 rounded-lg animate-pulse" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-2xl border border-gray-100 overflow-hidden">
            <div className="h-44 bg-gray-200 animate-pulse" />
            <div className="p-4 space-y-2.5">
              <div className="h-3 w-16 bg-gray-200 rounded animate-pulse" />
              <div className="h-4 w-full bg-gray-200 rounded animate-pulse" />
              <div className="h-3 w-4/5 bg-gray-100 rounded animate-pulse" />
              <div className="h-3 w-20 bg-gray-100 rounded animate-pulse ml-auto" />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
