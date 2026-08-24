import { useEffect, useState, useCallback } from 'react';
import CandidateDetailHeader from './CandidateDetailHeader';
import CandidateEvaluationSection from './CandidateEvaluationSection';
import CandidateResumeTimeline from './CandidateResumeTimeline';
import CandidateDetailSkeleton from './CandidateDetailSkeleton';
import { getEvaluationApi, getResumeApi, getJobApi } from '../services/api';
import { AlertCircle, RefreshCw, Briefcase, Clock } from 'lucide-react';

export default function CandidateDetailView({ evaluationId, onBackToResults }) {
  const [evaluation, setEvaluation] = useState(null);
  const [resume, setResume] = useState(null);
  const [job, setJob] = useState(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCandidateData = useCallback(async (isMounted = { current: true }) => {
    if (!evaluationId) return;

    setError(null);

    try {
      const evalData = await getEvaluationApi(evaluationId);
      if (!isMounted.current) return;
      setEvaluation(evalData);

      const fetchPromises = [];

      if (evalData?.resume_id) {
        fetchPromises.push(
          getResumeApi(evalData.resume_id)
            .then((r) => {
              if (isMounted.current) setResume(r.resume || null);
            })
            .catch(() => {
              if (isMounted.current) setResume(null);
            })
        );
      }

      if (evalData?.job_id) {
        fetchPromises.push(
          getJobApi(evalData.job_id)
            .then((j) => {
              if (isMounted.current) setJob(j.job || null);
            })
            .catch(() => {
              if (isMounted.current) setJob(null);
            })
        );
      }

      await Promise.allSettled(fetchPromises);
    } catch (err) {
      if (isMounted.current) {
        setError(
          typeof err === 'string'
            ? err
            : err.message || 'Unable to load candidate evaluation assay record from database.'
        );
      }
    } finally {
      if (isMounted.current) {
        setIsLoading(false);
      }
    }
  }, [evaluationId]);

  useEffect(() => {
    const isMounted = { current: true };
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchCandidateData(isMounted);
    return () => {
      isMounted.current = false;
    };
  }, [fetchCandidateData]);

  const handleBackNav = () => {
    if (onBackToResults) {
      onBackToResults();
    } else if (evaluation?.job_id) {
      window.location.hash = `#results/${evaluation.job_id}`;
    } else {
      window.location.hash = '#workspace';
    }
  };

  if (isLoading) {
    return <CandidateDetailSkeleton />;
  }

  if (error || !evaluation) {
    return (
      <div className="bg-bg-surface border border-border rounded-lg p-8 text-center my-6 max-w-xl mx-auto space-y-4 font-sans">
        <div className="h-10 w-10 rounded-full bg-bg-base border border-accent text-accent flex items-center justify-center mx-auto">
          <AlertCircle className="w-5 h-5" />
        </div>

        <h3 className="font-display font-medium text-lg text-text-primary">Evaluation Record Unavailable</h3>
        <p className="text-xs text-text-secondary font-mono">{error || 'Evaluation record not found.'}</p>

        <div className="flex justify-center space-x-3 pt-2 font-mono text-xs">
          <button
            type="button"
            onClick={() => {
              setIsLoading(true);
              fetchCandidateData();
            }}
            className="inline-flex items-center space-x-1.5 px-4 py-2 bg-accent text-white rounded hover:bg-accent-hover transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RETRY FETCH</span>
          </button>

          <button
            type="button"
            onClick={handleBackNav}
            className="inline-flex items-center space-x-1.5 px-4 py-2 bg-bg-base text-text-primary border border-border rounded transition-colors"
          >
            <span>← SCREENING RESULTS</span>
          </button>
        </div>
      </div>
    );
  }

  const scoreFormatted = (evaluation.score || 0).toFixed(1);

  return (
    <div className="space-y-6 font-sans">
      {/* 1. Header Navigation & Contact Summary */}
      <CandidateDetailHeader
        evaluation={evaluation}
        resume={resume}
        job={job}
        onBackToResults={handleBackNav}
      />

      {/* 2. Responsive 2-Column Evaluation Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Primary Column: Evaluation Report & Resume Details (8 cols on lg) */}
        <div className="lg:col-span-8 space-y-6">
          <CandidateEvaluationSection evaluation={evaluation} />

          {resume && (
            <div className="pt-2">
              <h2 className="text-xs font-mono uppercase tracking-wider text-text-muted mb-4 flex items-center space-x-2">
                <Briefcase className="w-3.5 h-3.5 text-accent" />
                <span>CANDIDATE EVIDENCE &amp; TIMELINE</span>
              </h2>
              <CandidateResumeTimeline resume={resume} />
            </div>
          )}
        </div>

        {/* Right Secondary Panel: Compact Score Summary & Job Context (4 cols on lg) */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Quick Score Panel */}
          <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-3 font-mono text-xs">
            <span className="text-[10px] text-text-muted uppercase tracking-wider block">
              ASSAY SCORE SUMMARY
            </span>

            <div className="bg-bg-base border border-border rounded p-4 text-center">
              <div className="flex items-baseline justify-center space-x-1">
                <span className="font-display font-medium text-3xl text-text-primary">{scoreFormatted}</span>
                <span className="text-xs text-text-muted"> / 10</span>
              </div>
              <p className="text-xs font-mono text-accent mt-1 uppercase">
                {evaluation.recommendation}
              </p>
            </div>

            <div className="divide-y divide-border/60 text-xs pt-1">
              <div className="flex justify-between py-1.5">
                <span className="text-text-muted">Requirements Full Match</span>
                <span className="font-medium text-[var(--accent-2)]">
                  {evaluation.matched_required_skills?.length || 0}
                </span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-text-muted">Requirements Missing</span>
                <span className="font-medium text-[var(--danger-muted)]">
                  {evaluation.missing_required_skills?.length || 0}
                </span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-text-muted">Preferred Skills Present</span>
                <span className="font-medium text-text-primary">
                  {evaluation.matched_preferred_skills?.length || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Job Context Panel */}
          {job && (
            <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-3 font-mono text-xs">
              <div className="flex items-center space-x-2 text-[10px] text-text-muted uppercase tracking-wider">
                <Briefcase className="w-3.5 h-3.5 text-accent" />
                <span>ASSAY SPECIFICATION</span>
              </div>

              <h4 className="font-sans text-sm font-medium text-text-primary">
                {job.title || 'Job Specification'}
              </h4>

              {job.experience?.minimum_years !== null && job.experience?.minimum_years !== undefined && (
                <div className="flex items-center space-x-1.5 text-xs text-text-secondary">
                  <Clock className="w-3.5 h-3.5 text-accent" />
                  <span>REQUIRED EXP: {job.experience.minimum_years}+ YEARS</span>
                </div>
              )}

              {job.required_skills?.length > 0 && (
                <div className="pt-2 border-t border-border/60">
                  <span className="text-[10px] text-text-muted uppercase block mb-1.5">
                    Target Requirement Claims
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {job.required_skills.map((sk, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 text-[10px] text-text-primary bg-bg-base border border-border rounded"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
