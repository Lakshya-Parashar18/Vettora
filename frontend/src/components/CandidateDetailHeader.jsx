import { ArrowLeft, Mail, Phone, Briefcase } from 'lucide-react';

export default function CandidateDetailHeader({
  evaluation,
  resume,
  job,
  onBackToResults,
}) {
  const score = evaluation?.score !== null && evaluation?.score !== undefined ? evaluation.score : 0;
  const scoreFormatted = score.toFixed(1);
  const recommendation = (evaluation?.recommendation || 'EVALUATED').toUpperCase();

  const name = resume?.candidate?.name || evaluation?.candidate?.name || 'Candidate Profile';
  const email = resume?.candidate?.email || evaluation?.candidate?.email || 'Not provided';
  const phone = resume?.candidate?.phone || 'Not provided';

  const jobTitle = job?.title || 'Job Screening';

  return (
    <div className="space-y-4 font-sans">
      {/* Navigation & Evaluation ID */}
      <div className="flex items-center justify-between font-mono text-xs">
        <button
          type="button"
          onClick={onBackToResults}
          className="inline-flex items-center space-x-2 text-text-secondary hover:text-accent bg-bg-surface border border-border px-3.5 py-1.5 rounded transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5 text-accent" />
          <span>← SCREENING RESULTS</span>
        </button>

        <div className="flex items-center space-x-2 text-xs text-text-muted">
          <span>EVALUATION ID:</span>
          <code className="bg-bg-surface px-2 py-0.5 rounded border border-border text-text-primary font-mono">
            {evaluation?.evaluation_id ? `${evaluation.evaluation_id.substring(0, 8)}...` : 'ID'}
          </code>
        </div>
      </div>

      {/* Main Header Banner */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 transition-colors">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start space-x-4 min-w-0">
            <div className="min-w-0">
              <div className="flex items-center space-x-2.5 flex-wrap">
                <h1 className="font-display font-medium text-2xl text-text-primary tracking-tight truncate">
                  {name}
                </h1>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-xs text-text-secondary font-mono">
                <div className="flex items-center space-x-1.5">
                  <Mail className="w-3.5 h-3.5 text-accent shrink-0" />
                  <span>{email}</span>
                </div>
                {phone !== 'Not provided' && (
                  <div className="flex items-center space-x-1.5">
                    <Phone className="w-3.5 h-3.5 text-accent shrink-0" />
                    <span>{phone}</span>
                  </div>
                )}
                {jobTitle && (
                  <div className="flex items-center space-x-1.5 text-text-primary bg-bg-base border border-border px-2 py-0.5 rounded">
                    <Briefcase className="w-3 h-3 text-accent shrink-0" />
                    <span className="font-medium">{jobTitle}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Circular Score Seal */}
          <div className="flex items-center justify-between md:justify-end space-x-4 shrink-0 pt-3 md:pt-0 border-t md:border-t-0 border-border/60">
            <div className="flex flex-col items-center justify-center shrink-0">
              <div className="w-[56px] h-[56px] rounded-full border border-accent flex flex-col items-center justify-center relative bg-bg-base animate-stamp-landing">
                <span className="font-display font-medium text-lg text-text-primary leading-none">
                  {scoreFormatted}
                </span>
                <span className="font-mono text-[9px] text-text-muted leading-none mt-0.5">/10</span>
              </div>
              <span className="font-mono text-[9px] text-text-muted tracking-wider uppercase mt-1">
                {recommendation}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
