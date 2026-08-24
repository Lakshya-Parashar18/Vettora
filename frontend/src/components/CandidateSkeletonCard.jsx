export default function CandidateSkeletonCard() {
  return (
    <div className="bg-bg-surface border border-border rounded-lg p-5 animate-pulse space-y-4 font-sans">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-6 w-8 bg-bg-base rounded" />
          <div className="space-y-1.5">
            <div className="h-4 w-40 bg-bg-base rounded" />
            <div className="h-3 w-28 bg-bg-base rounded" />
          </div>
        </div>
        <div className="h-14 w-14 rounded-full border border-border bg-bg-base" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-border/60 pt-4">
        <div className="space-y-2">
          <div className="h-3 w-24 bg-bg-base rounded" />
          <div className="space-y-1.5">
            <div className="h-4 w-full bg-bg-base rounded" />
            <div className="h-4 w-full bg-bg-base rounded" />
          </div>
        </div>
        <div className="space-y-2">
          <div className="h-3 w-24 bg-bg-base rounded" />
          <div className="space-y-1">
            <div className="h-3 w-full bg-bg-base rounded" />
            <div className="h-3 w-3/4 bg-bg-base rounded" />
          </div>
        </div>
      </div>
    </div>
  );
}
