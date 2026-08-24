export default function CandidateDetailSkeleton() {
  return (
    <div className="space-y-6 animate-pulse font-sans">
      {/* Header Skeleton */}
      <div className="bg-bg-surface border border-border rounded-lg p-6 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="h-10 w-10 bg-bg-base rounded-full border border-border" />
            <div className="space-y-2">
              <div className="h-4 w-48 bg-bg-base rounded" />
              <div className="h-3 w-64 bg-bg-base rounded" />
            </div>
          </div>
          <div className="h-10 w-28 bg-bg-base rounded shrink-0" />
        </div>
      </div>

      {/* Main Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-bg-surface border border-border rounded-lg p-6 h-36" />
          <div className="bg-bg-surface border border-border rounded-lg p-6 h-48" />
          <div className="bg-bg-surface border border-border rounded-lg p-6 h-64" />
        </div>
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-bg-surface border border-border rounded-lg p-6 h-56" />
          <div className="bg-bg-surface border border-border rounded-lg p-6 h-48" />
        </div>
      </div>
    </div>
  );
}
