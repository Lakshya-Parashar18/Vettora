import { useState } from 'react';
import { ArrowRight, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

function RequirementLedgerRow({ cm, idx }) {
  const [isOpen, setIsOpen] = useState(false);
  const matchLvl = (cm.match_level || 'missing').toLowerCase();
  const isFull = matchLvl === 'full';
  const isPartial = matchLvl === 'partial';
  const isMissing = matchLvl === 'missing' || matchLvl === 'weak';

  const glyph = isFull ? '✓' : isPartial ? '◐' : '○';
  const glyphColor = isFull
    ? 'text-[var(--accent-2)]'
    : isPartial
    ? 'text-[var(--accent)]'
    : 'text-[var(--danger-muted)]';

  const covRatio =
    cm.coverage_ratio !== undefined && cm.coverage_ratio !== null
      ? cm.coverage_ratio
      : isFull
      ? 1
      : 0;
  const subtopics = cm.subtopics || [];
  const subtopicCount = subtopics.length;
  const coveredCount = Math.round(covRatio * (subtopicCount || 1));
  const countDisplay =
    subtopicCount > 0
      ? `${coveredCount}/${subtopicCount}`
      : `${Math.round(covRatio * 100)}%`;

  const evidenceList = cm.evidence_found || [];
  const missingList = cm.critical_subtopics_missing || [];

  return (
    <div className="border-b border-border/60 last:border-b-0 py-0.5">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-controls={`evidence-reveal-${idx}`}
        className="w-full py-2 flex items-center justify-between text-left group focus:outline-none focus:ring-1 focus:ring-[var(--accent)] rounded px-1 transition-colors hover:bg-bg-base/40"
      >
        <div className="flex items-start space-x-2.5 min-w-0 flex-1 pr-2">
          <span className={`font-mono text-sm font-medium ${glyphColor} shrink-0 leading-none mt-0.5`}>
            {glyph}
          </span>
          <span className="font-sans text-xs font-medium text-text-primary leading-tight break-words">
            {cm.requirement}
          </span>
        </div>

        <div className="flex items-center space-x-2 shrink-0 font-mono text-xs">
          <span className={`font-medium ${glyphColor}`}>
            {countDisplay}
          </span>
          <span className={`text-text-muted transition-transform duration-200 text-xs leading-none ${isOpen ? 'rotate-180' : ''}`}>
            ▾
          </span>
        </div>
      </button>

      {/* Requirement 1: Expandable Evidence Reveal Block */}
      <div
        id={`evidence-reveal-${idx}`}
        className={`overflow-hidden transition-all duration-200 ease-in-out ${
          isOpen ? 'max-h-96 opacity-100 pb-2.5 pt-1' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="bg-bg-base border border-border/60 rounded p-3 text-xs space-y-2 font-mono ml-5">
          <span className="text-[10px] text-text-muted uppercase tracking-wider block font-mono">
            FROM RESUME
          </span>

          {!isMissing && evidenceList.length > 0 ? (
            <div className="font-sans text-xs text-text-primary leading-relaxed">
              &ldquo;
              {evidenceList.map((ev, i) => (
                <span key={i}>
                  <span className="text-[var(--accent-2)] font-medium">{ev}</span>
                  {i < evidenceList.length - 1 ? ' · ' : ''}
                </span>
              ))}
              &rdquo;
            </div>
          ) : (
            <p className="font-sans text-xs text-text-muted italic">
              No evidence found for this requirement in the resume
            </p>
          )}

          {cm.reasoning && (
            <p className="font-sans italic text-[11px] text-text-secondary pt-1 border-t border-border/40 leading-normal">
              {cm.reasoning}
            </p>
          )}

          {missingList.length > 0 && (
            <p className="font-sans italic text-[11px] text-[var(--danger-muted)]">
              Missing sub-topics: {missingList.join(', ')}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function CandidateResultCard({
  candidate,
  rank,
  onViewEvaluation,
  isMultiCandidate = false,
  staggerIndex = 0,
}) {
  const [isExpanded, setIsExpanded] = useState(!isMultiCandidate);

  if (!candidate) return null;

  const score = candidate.score !== null && candidate.score !== undefined ? candidate.score : 0;
  const scoreFormatted = score.toFixed(1);
  const recommendation = (candidate.recommendation || 'EVALUATED').toUpperCase();

  const name = candidate.candidate?.name || 'Candidate Profile';
  const email = candidate.candidate?.email || null;

  const scoreBreakdown = candidate.score_breakdown || {
    skills: 0,
    experience: 0,
    education: 0,
    required_criteria: 0,
    semantic_fit: 0,
  };

  const matchedReq = candidate.matched_required_skills || [];
  const missingReq = candidate.missing_required_skills || [];

  const strengths = candidate.strengths || [];
  const concerns = candidate.concerns || [];
  const conceptualMatches = candidate.conceptual_matches || [];

  // Identify top missing requirement for condensed row view
  const topMissingMatch = conceptualMatches.find(
    (cm) =>
      (cm.match_level || '').toLowerCase() === 'missing' ||
      (cm.match_level || '').toLowerCase() === 'weak'
  );
  const topMissingLabel = topMissingMatch
    ? topMissingMatch.requirement
    : missingReq.length > 0
    ? missingReq[0]
    : null;

  const breakdownMetrics = [
    { label: 'Skills Match', value: Math.round(scoreBreakdown.skills || 0) },
    { label: 'Experience Alignment', value: Math.round(scoreBreakdown.experience || 0) },
    { label: 'Education Verification', value: Math.round(scoreBreakdown.education || 0) },
    { label: 'Required Criteria', value: Math.round(scoreBreakdown.required_criteria || 0) },
    { label: 'Semantic Context Fit', value: Math.round(scoreBreakdown.semantic_fit || 0) },
  ];

  const staggerStyle = {
    animationDelay: `${staggerIndex * 40}ms`,
  };

  return (
    <div
      style={staggerStyle}
      className="bg-bg-surface border border-border rounded-lg p-4 sm:p-5 transition-colors flex flex-col font-sans animate-ledger-row"
    >
      {/* Header Row (Clickable in Multi-Candidate Mode to Toggle Expand) */}
      <div
        onClick={() => isMultiCandidate && setIsExpanded((prev) => !prev)}
        className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
          isMultiCandidate ? 'cursor-pointer select-none' : ''
        } ${isExpanded ? 'pb-4 border-b border-border/60' : ''}`}
      >
        <div className="flex items-center space-x-3.5 min-w-0">
          <div className="font-mono text-xs font-medium text-text-muted shrink-0">
            #{String(rank).padStart(2, '0')}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center space-x-2 flex-wrap">
              <h3 className="text-base font-medium text-text-primary truncate">
                {name}
              </h3>
              <span className="font-mono text-[10px] text-text-muted tracking-wider uppercase">
                · {recommendation}
              </span>
            </div>

            {!isExpanded && (
              <p className="text-xs text-text-secondary mt-0.5 font-mono truncate">
                {topMissingLabel ? (
                  <span className="text-[var(--danger-muted)]">TOP GAP: {topMissingLabel}</span>
                ) : (
                  <span className="text-[var(--accent-2)]">ALL REQUIREMENTS EVIDENCED</span>
                )}
              </p>
            )}

            {isExpanded && email && (
              <p className="text-xs text-text-muted mt-0.5 font-mono truncate">
                {email}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between sm:justify-end space-x-4 shrink-0">
          {/* Requirement 2: Score Seal with Physical Stamp Landing Scale-In */}
          <div className="flex flex-col items-center justify-center shrink-0">
            <div className="w-[50px] h-[50px] rounded-full border border-accent flex flex-col items-center justify-center relative bg-bg-base/40 animate-stamp-landing">
              <span className="font-display font-medium text-base text-text-primary leading-none">
                {scoreFormatted}
              </span>
              <span className="font-mono text-[9px] text-text-muted leading-none mt-0.5">/10</span>
            </div>
          </div>

          {candidate.evaluation_id && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onViewEvaluation(candidate.evaluation_id);
              }}
              className="btn-secondary text-xs"
              title="View full evaluation assay"
            >
              <span>INSPECT</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}

          {isMultiCandidate && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded((prev) => !prev);
              }}
              className="btn-ghost p-1 text-text-muted hover:text-text-primary"
              aria-label={isExpanded ? 'Collapse ledger' : 'Expand ledger'}
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded Full Ledger View */}
      {isExpanded && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4">
          
          {/* Left Column: Evaluation Metrics Ledger */}
          <div className="lg:col-span-5 space-y-2 font-mono text-xs border-b lg:border-b-0 lg:border-r border-border/60 pb-4 lg:pb-0 lg:pr-6">
            <span className="text-[10px] font-mono text-text-muted uppercase tracking-wider block mb-1">
              EVALUATION METRICS
            </span>
            <div className="divide-y divide-border/40">
              {breakdownMetrics.map((m) => (
                <div key={m.label} className="py-1.5 flex items-center justify-between">
                  <span className="text-text-secondary">{m.label}</span>
                  <span className="font-medium text-text-primary">{m.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Requirement Verification Ledger with Evidence Reveal Disclosure Controls */}
          <div className="lg:col-span-7 space-y-3">
            <span className="text-[10px] font-mono text-text-muted uppercase tracking-wider block">
              REQUIREMENT VERIFICATION LEDGER
            </span>

            {conceptualMatches.length > 0 ? (
              <div className="divide-y divide-border/60">
                {conceptualMatches.map((cm, idx) => (
                  <RequirementLedgerRow key={`cm-ledger-${idx}`} cm={cm} idx={idx} />
                ))}
              </div>
            ) : (
              <div className="divide-y divide-border/60">
                {matchedReq.map((skill, idx) => (
                  <div key={`req-m-${idx}`} className="py-2 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="text-[var(--accent-2)]">✓</span>
                      <span className="text-text-primary font-sans font-medium">{skill}</span>
                    </div>
                    <span className="text-[var(--accent-2)]">100%</span>
                  </div>
                ))}

                {missingReq.map((skill, idx) => (
                  <div key={`req-x-${idx}`} className="py-2 flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center space-x-2">
                      <span className="text-[var(--danger-muted)]">○</span>
                      <span className="text-text-primary font-sans font-medium">{skill}</span>
                    </div>
                    <span className="text-[var(--danger-muted)]">0%</span>
                  </div>
                ))}

                {matchedReq.length === 0 && missingReq.length === 0 && (
                  <span className="text-xs text-text-muted italic block py-2 font-mono">
                    No explicit requirement claims extracted.
                  </span>
                )}
              </div>
            )}

            {/* Strengths & Concerns */}
            {(strengths.length > 0 || concerns.length > 0) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs font-sans">
                {strengths.length > 0 && (
                  <div className="border border-border/60 rounded p-2.5 bg-bg-base/40">
                    <span className="font-mono text-[10px] text-[var(--accent-2)] uppercase tracking-wider block mb-1 flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3 shrink-0" />
                      <span>VERIFIED EVIDENCE</span>
                    </span>
                    <ul className="space-y-1 text-text-secondary text-[11px] list-disc list-inside">
                      {strengths.map((st, i) => (
                        <li key={i} className="truncate">{st}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {concerns.length > 0 && (
                  <div className="border border-border/60 rounded p-2.5 bg-bg-base/40">
                    <span className="font-mono text-[10px] text-[var(--danger-muted)] uppercase tracking-wider block mb-1 flex items-center space-x-1">
                      <AlertTriangle className="w-3 h-3 shrink-0" />
                      <span>ASSAY DISCREPANCIES</span>
                    </span>
                    <ul className="space-y-1 text-text-secondary text-[11px] list-disc list-inside">
                      {concerns.map((cn, i) => (
                        <li key={i} className="truncate">{cn}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
