import { Users, ArrowLeft, RefreshCw } from 'lucide-react';

export default function ResultsEmptyState({
  isFiltered,
  onClearFilters,
  onBackToWorkspace,
}) {
  if (isFiltered) {
    return (
      <div className="bg-bg-surface border border-border rounded-lg p-8 text-center my-6 font-sans">
        <Users className="w-6 h-6 text-text-muted mx-auto mb-2" />
        <h3 className="font-display font-medium text-lg text-text-primary">
          No Candidate Records Match Active Filters
        </h3>
        <p className="text-xs text-text-secondary mt-1 max-w-md mx-auto">
          The search query or tier filter returned 0 matching candidates. Reset filters to view all assayed records.
        </p>

        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={onClearFilters}
            className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-accent text-white font-mono text-xs rounded hover:bg-accent-hover transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RESET SEARCH &amp; FILTERS</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-bg-surface border border-border rounded-lg p-8 text-center my-6 font-sans">
      <Users className="w-6 h-6 text-text-muted mx-auto mb-2" />
      <h3 className="font-display font-medium text-lg text-text-primary">
        No Candidate Records Screened for This Session
      </h3>
      <p className="text-xs text-text-secondary mt-1 max-w-md mx-auto">
        Upload resumes to begin — Vettora reads PDF, DOC, DOCX, and TXT files for evidence decomposition and candidate screening.
      </p>

      <div className="mt-5 flex justify-center">
        <button
          type="button"
          onClick={onBackToWorkspace}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-accent text-white font-mono text-xs rounded hover:bg-accent-hover transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>RETURN TO CANDIDATE WORKSPACE</span>
        </button>
      </div>
    </div>
  );
}
