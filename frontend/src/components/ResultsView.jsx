import { useEffect, useState, useMemo, useCallback } from 'react';
import ResultsSummary from './ResultsSummary';
import ResultsControls from './ResultsControls';
import CandidateResultCard from './CandidateResultCard';
import CandidateSkeletonCard from './CandidateSkeletonCard';
import ResultsEmptyState from './ResultsEmptyState';
import { getCandidatesApi, getJobApi } from '../services/api';
import { AlertCircle, RefreshCw, Info } from 'lucide-react';

export default function ResultsView({
  jobId,
  initialResults,
  onBackToWorkspace,
  onViewEvaluation,
}) {
  const [candidates, setCandidates] = useState(initialResults?.candidates || []);
  const [job, setJob] = useState(null);

  const [isLoading, setIsLoading] = useState(!initialResults?.candidates);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [recommendationFilter, setRecommendationFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('SCORE_DESC');

  const fetchResultsData = useCallback(async () => {
    if (!jobId) return;

    setError(null);

    try {
      const [candRes, jobRes] = await Promise.allSettled([
        getCandidatesApi(jobId),
        getJobApi(jobId),
      ]);

      if (candRes.status === 'fulfilled' && candRes.value?.candidates) {
        setCandidates(candRes.value.candidates);
      } else if (candRes.status === 'rejected') {
        throw new Error(
          candRes.reason?.message || 'Could not retrieve candidate screening records.'
        );
      }

      if (jobRes.status === 'fulfilled' && jobRes.value?.job) {
        setJob(jobRes.value.job);
      }
    } catch (err) {
      setError(
        typeof err === 'string'
          ? err
          : err.message || 'Failed to connect to the backend database service.'
      );
    } finally {
      setIsLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!initialResults?.candidates) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchResultsData();
    }
  }, [initialResults?.candidates, fetchResultsData]);

  const processedCandidates = useMemo(
    () => candidates.filter((c) => c.status === 'processed' || c.score !== null),
    [candidates]
  );
  const failedCandidates = useMemo(
    () => candidates.filter((c) => c.status === 'failed' && c.score === null),
    [candidates]
  );

  const filteredCandidates = useMemo(() => {
    let list = [...processedCandidates];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((c) => {
        const name = (c.candidate?.name || '').toLowerCase();
        const email = (c.candidate?.email || '').toLowerCase();
        return name.includes(q) || email.includes(q);
      });
    }

    if (recommendationFilter !== 'ALL') {
      list = list.filter((c) => {
        const rec = (c.recommendation || '').toLowerCase();
        if (recommendationFilter === 'STRONG') return rec.includes('strong') || rec.includes('top');
        if (recommendationFilter === 'GOOD') return rec.includes('good');
        if (recommendationFilter === 'PARTIAL') return rec.includes('partial') || rec.includes('moderate');
        if (recommendationFilter === 'WEAK') return rec.includes('weak') || rec.includes('low');
        return true;
      });
    }

    list.sort((a, b) => {
      const scoreA = a.score !== null && a.score !== undefined ? a.score : -1;
      const scoreB = b.score !== null && b.score !== undefined ? b.score : -1;
      const nameA = (a.candidate?.name || '').toLowerCase();
      const nameB = (b.candidate?.name || '').toLowerCase();

      if (sortBy === 'SCORE_DESC') {
        if (scoreB !== scoreA) return scoreB - scoreA;
        return nameA.localeCompare(nameB);
      }
      if (sortBy === 'SCORE_ASC') {
        if (scoreA !== scoreB) return scoreA - scoreB;
        return nameA.localeCompare(nameB);
      }
      if (sortBy === 'NAME_ASC') {
        return nameA.localeCompare(nameB);
      }
      return 0;
    });

    return list;
  }, [processedCandidates, searchQuery, recommendationFilter, sortBy]);

  const handleClearFilters = () => {
    setSearchQuery('');
    setRecommendationFilter('ALL');
    setSortBy('SCORE_DESC');
  };

  const handleCandidateViewEvaluation = (evaluationId) => {
    if (onViewEvaluation) {
      onViewEvaluation(evaluationId);
    } else {
      window.location.hash = `#candidate/${evaluationId}`;
    }
  };

  const handleExportCsv = () => {
    if (!filteredCandidates || filteredCandidates.length === 0) return;

    const headers = [
      'Rank',
      'Candidate Name',
      'Email',
      'Phone',
      'Final Score (0-10)',
      'Match Tier',
      'Confidence (%)',
      'Experience Years',
      'Education Level',
      'Required Skills Matched',
      'Justification Summary',
    ];

    const rows = filteredCandidates.map((c, idx) => {
      const name = c.candidate_name || c.name || `Candidate #${idx + 1}`;
      const email = c.email || 'N/A';
      const phone = c.phone || 'N/A';
      const score = c.final_score !== undefined && c.final_score !== null ? Number(c.final_score).toFixed(1) : (c.score !== undefined ? Number(c.score).toFixed(1) : '0.0');
      const tier = c.recommendation || c.match_tier || 'N/A';
      const confidence = c.score_confidence || 85;
      const expYears = c.experience_years !== undefined ? c.experience_years : 'N/A';
      const eduLevel = c.education_level || 'N/A';
      const reqMatched = Array.isArray(c.matched_required_skills) ? c.matched_required_skills.join('; ') : 'N/A';
      const justification = (c.justification || '').replace(/"/g, '""');

      return [
        idx + 1,
        `"${name}"`,
        `"${email}"`,
        `"${phone}"`,
        score,
        `"${tier}"`,
        `"${confidence}%"`,
        expYears,
        `"${eduLevel}"`,
        `"${reqMatched}"`,
        `"${justification}"`,
      ].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `vettora_rankings_${jobId || 'export'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportJson = () => {
    if (!filteredCandidates || filteredCandidates.length === 0) return;

    const exportData = {
      job_id: jobId,
      exported_at: new Date().toISOString(),
      candidates_count: filteredCandidates.length,
      candidates: filteredCandidates,
    };

    const jsonContent = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `vettora_candidates_${jobId || 'export'}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="space-y-6 font-sans">
        <div className="bg-bg-surface border border-border rounded-lg p-6 animate-pulse space-y-4">
          <div className="h-5 w-48 bg-bg-base rounded" />
          <div className="h-4 w-72 bg-bg-base rounded" />
        </div>

        <div className="space-y-4">
          <CandidateSkeletonCard />
          <CandidateSkeletonCard />
          <CandidateSkeletonCard />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-bg-surface border border-border rounded-lg p-8 text-center my-6 max-w-2xl mx-auto font-sans">
        <div className="h-10 w-10 rounded-full bg-bg-base border border-[var(--danger-muted)] text-[var(--danger-muted)] flex items-center justify-center mx-auto mb-3">
          <AlertCircle className="w-5 h-5" />
        </div>

        <h3 className="font-display font-medium text-lg text-text-primary">Unable to Load Screening Results</h3>
        <p className="text-xs text-text-secondary font-mono mt-1 max-w-md mx-auto">{error}</p>

        <div className="mt-5 flex justify-center space-x-3 font-mono text-xs">
          <button
            type="button"
            onClick={() => {
              setIsLoading(true);
              fetchResultsData();
            }}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-accent text-white rounded hover:bg-accent-hover transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RETRY CONNECTION</span>
          </button>

          <button
            type="button"
            onClick={onBackToWorkspace}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-bg-base text-text-primary border border-border rounded transition-colors"
          >
            <span>← WORKSPACE</span>
          </button>
        </div>
      </div>
    );
  }

  const isFiltered = searchQuery.trim() !== '' || recommendationFilter !== 'ALL';

  return (
    <div className="space-y-6 font-sans">
      {/* Header Summary Component */}
      <ResultsSummary
        job={job}
        jobId={jobId}
        candidates={processedCandidates}
        onBackToWorkspace={onBackToWorkspace}
      />

      {/* Partial Candidate Failures Warning Notice */}
      {failedCandidates.length > 0 && (
        <div className="bg-bg-surface border border-[var(--danger-muted)]/40 rounded p-3 text-xs text-[var(--danger-muted)] flex items-center justify-between font-mono">
          <div className="flex items-center space-x-2">
            <Info className="w-3.5 h-3.5 shrink-0" />
            <span>
              <strong>{processedCandidates.length}</strong> candidates ranked successfully ·{' '}
              <strong>{failedCandidates.length}</strong> candidate{failedCandidates.length === 1 ? '' : 's'} could not be evaluated due to file unreadability.
            </span>
          </div>
        </div>
      )}

      {/* Interactive Controls (Search, Filter, Sort, CSV/JSON Export) */}
      <ResultsControls
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        recommendationFilter={recommendationFilter}
        onFilterChange={setRecommendationFilter}
        sortBy={sortBy}
        onSortChange={setSortBy}
        totalResultsCount={processedCandidates.length}
        filteredCount={filteredCandidates.length}
        onExportCsv={handleExportCsv}
        onExportJson={handleExportJson}
      />

      {/* Candidate List or Empty State */}
      {filteredCandidates.length === 0 ? (
        <ResultsEmptyState
          isFiltered={isFiltered}
          onClearFilters={handleClearFilters}
          onBackToWorkspace={onBackToWorkspace}
        />
      ) : (
        <div className="space-y-4">
          {filteredCandidates.map((candidate, idx) => (
            <CandidateResultCard
              key={candidate.evaluation_id || candidate.resume_id || idx}
              candidate={candidate}
              rank={idx + 1}
              onViewEvaluation={handleCandidateViewEvaluation}
              isMultiCandidate={filteredCandidates.length > 1}
              staggerIndex={idx}
            />
          ))}
        </div>
      )}
    </div>
  );
}
