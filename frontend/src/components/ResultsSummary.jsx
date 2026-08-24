import { ArrowLeft } from 'lucide-react';

export default function ResultsSummary({
  job,
  jobId,
  candidates,
  onBackToWorkspace,
}) {
  const totalCount = candidates.length;

  const getMatchCategoryCount = (keyword) => {
    return candidates.filter((c) => {
      const rec = (c.recommendation || '').toLowerCase();
      return rec.includes(keyword);
    }).length;
  };

  const strongCount = getMatchCategoryCount('strong') || getMatchCategoryCount('top');
  const goodCount = getMatchCategoryCount('good');
  const partialCount = getMatchCategoryCount('partial') || getMatchCategoryCount('moderate');
  const moderateCount = goodCount + partialCount;
  const weakCount = Math.max(0, totalCount - (strongCount + moderateCount));

  const totalScores = candidates.reduce(
    (sum, c) => sum + (c.score !== null && c.score !== undefined ? c.score : 0),
    0
  );
  const avgScore = totalCount > 0 ? (totalScores / totalCount).toFixed(1) : 'N/A';

  const strongPct = totalCount > 0 ? (strongCount / totalCount) * 100 : 0;
  const moderatePct = totalCount > 0 ? (moderateCount / totalCount) * 100 : 0;
  const weakPct = totalCount > 0 ? (weakCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Navigation & Job Session Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBackToWorkspace}
          className="inline-flex items-center space-x-2 text-xs font-mono text-text-secondary hover:text-accent bg-bg-surface border border-border px-3.5 py-1.5 rounded transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5 text-accent" />
          <span>← WORKSPACE</span>
        </button>

        <div className="flex items-center space-x-2 text-xs text-text-muted">
          <span>SESSION ID:</span>
          <code className="bg-bg-surface px-2 py-0.5 rounded border border-border text-text-primary font-mono">
            {jobId}
          </code>
        </div>
      </div>

      {/* Role Title Bar */}
      <div className="bg-bg-surface border border-border rounded-lg p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <span className="text-[10px] text-text-muted uppercase tracking-wider block font-mono mb-0.5">
            ASSAYED TARGET ROLE
          </span>
          <h1 className="font-sans font-medium text-lg text-text-primary">
            {job?.title || 'Candidate Screening Ledger'}
          </h1>
        </div>
      </div>

      {/* Single Horizontal Ledger Strip (Requirement 5) */}
      <div className="bg-bg-surface border border-border rounded-lg p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
        {/* Left: Total Count */}
        <div className="flex flex-col justify-center shrink-0 pr-4 md:border-r md:border-border/60">
          <span className="text-[10px] text-text-muted uppercase tracking-wider block font-mono">
            TOTAL ASSAYED
          </span>
          <span className="font-mono text-xl font-medium text-text-primary mt-0.5">
            {totalCount} <span className="text-xs text-text-muted font-normal">CANDIDATES</span>
          </span>
        </div>

        {/* Middle: Compact Tier-Distribution Bar */}
        <div className="flex-1 space-y-1.5 px-2">
          <div className="flex items-center justify-between text-[10px] text-text-muted font-mono uppercase">
            <span>DISTRIBUTION</span>
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full inline-block bg-[var(--accent-2)]" />
                <span>VERIFIED ({strongCount})</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full inline-block bg-[var(--accent)]" />
                <span>PARTIAL ({moderateCount})</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full inline-block bg-[var(--danger-muted)]" />
                <span>GAP ({weakCount})</span>
              </span>
            </div>
          </div>

          {/* Proportional Distribution Bar */}
          <div className="w-full h-2 bg-bg-base rounded-full overflow-hidden flex">
            {strongPct > 0 && (
              <div
                className="h-full bg-[var(--accent-2)] transition-all duration-500"
                style={{ width: `${strongPct}%` }}
                title={`Verified (Strong): ${strongCount}`}
              />
            )}
            {moderatePct > 0 && (
              <div
                className="h-full bg-[var(--accent)] transition-all duration-500"
                style={{ width: `${moderatePct}%` }}
                title={`Partial: ${moderateCount}`}
              />
            )}
            {weakPct > 0 && (
              <div
                className="h-full bg-[var(--danger-muted)] transition-all duration-500"
                style={{ width: `${weakPct}%` }}
                title={`Gap: ${weakCount}`}
              />
            )}
            {totalCount === 0 && (
              <div className="h-full w-full bg-border/40" />
            )}
          </div>
        </div>

        {/* Right: Average Score in Fraunces */}
        <div className="flex flex-col items-end justify-center shrink-0 pl-4 md:border-l md:border-border/60">
          <span className="text-[10px] text-text-muted uppercase tracking-wider block font-mono">
            AVG SCORE
          </span>
          <div className="flex items-baseline space-x-1 mt-0.5">
            <span className="font-display font-medium text-2xl text-text-primary">
              {avgScore}
            </span>
            <span className="font-mono text-xs text-text-muted">/10</span>
          </div>
        </div>
      </div>
    </div>
  );
}
