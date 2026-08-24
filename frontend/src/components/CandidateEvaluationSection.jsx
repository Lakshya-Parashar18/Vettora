import { useState } from 'react';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Award,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
} from 'lucide-react';
import ReasoningTraceView from './ReasoningTraceView';

export default function CandidateEvaluationSection({ evaluation }) {
  const [activeTab, setActiveTab] = useState('ledger'); // 'ledger' | 'trace'
  const [expandedRows, setExpandedRows] = useState({});

  if (!evaluation) return null;

  const toggleRow = (idx) => {
    setExpandedRows((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const justification = evaluation.justification || 'No explicit justification text provided.';
  const scoreConfidence = evaluation.score_confidence || 85;
  const matchTier = evaluation.match_tier || evaluation.recommendation || 'Strong Match';

  const subScores = evaluation.sub_scores || {
    technical_fit: 80,
    cs_fundamentals: 85,
    problem_solving: 75,
    experience_alignment: 75,
    education_fit: 90,
    soft_skills_evidence: 70,
    technology_fit: 80,
    role_alignment: 80,
    adaptability: 80,
  };

  const conceptualMatches = evaluation.conceptual_matches || [];
  const strengths = evaluation.strengths || [];
  const concerns = evaluation.concerns || [];
  const evidence = evaluation.evidence || [];

  const subScoreMetrics = [
    { label: 'Technical Fit', value: Math.round(subScores.technical_fit || 80) },
    { label: 'Core Fundamentals', value: Math.round(subScores.cs_fundamentals || 85) },
    { label: 'Role Alignment', value: Math.round(subScores.role_alignment || 80) },
    { label: 'Experience Alignment', value: Math.round(subScores.experience_alignment || 75) },
    { label: 'Soft Skill Evidence', value: Math.round(subScores.soft_skills_evidence || 70) },
    { label: 'Education Fit', value: Math.round(subScores.education_fit || 90) },
    { label: 'Adaptability', value: Math.round(subScores.adaptability || 80) },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* 1. Candidate Summary & Sub-Scores Grid */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-4 font-mono text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/60 pb-3">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-accent" />
            <span className="text-xs uppercase tracking-wider text-text-primary font-medium">
              CANDIDATE ASSAY SUMMARY &amp; METRICS
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <span className="bg-bg-base border border-accent/40 text-accent px-2.5 py-1 rounded text-[11px] font-medium uppercase">
              {matchTier}
            </span>
            <span className="bg-bg-base border border-border text-text-secondary px-2 py-1 rounded text-[11px]">
              {scoreConfidence}% Confidence
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {subScoreMetrics.map((m) => (
            <div
              key={m.label}
              className="bg-bg-base border border-border/60 rounded p-3 space-y-1.5"
            >
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-text-muted truncate">{m.label}</span>
                <span className="font-medium text-text-primary">{m.value}%</span>
              </div>
              <div className="w-full bg-border/40 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-accent h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(Math.max(m.value, 0), 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Executive Justification Box */}
      <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-mono text-accent uppercase tracking-wider">
          <FileText className="w-3.5 h-3.5 text-accent" />
          <span>EVALUATION ASSAY JUSTIFICATION</span>
        </div>
        <p className="text-sm text-text-primary leading-relaxed">
          {justification}
        </p>
      </div>

      {/* 3. Navigation Tabs: Requirement Verification Ledger vs Reasoning Trace Pipeline */}
      <div className="flex items-center space-x-2 border-b border-border/60 pb-1 font-mono text-xs">
        <button
          type="button"
          onClick={() => setActiveTab('ledger')}
          className={`px-4 py-2 rounded-t font-medium transition-colors flex items-center space-x-2 ${
            activeTab === 'ledger'
              ? 'bg-bg-surface border-t border-l border-r border-border text-accent'
              : 'text-text-muted hover:text-text-primary'
          }`}
        >
          <Award className="w-3.5 h-3.5" />
          <span>REQUIREMENT VERIFICATION LEDGER ({conceptualMatches.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('trace')}
          className={`px-4 py-2 rounded-t font-medium transition-colors flex items-center space-x-2 ${
            activeTab === 'trace'
              ? 'bg-bg-surface border-t border-l border-r border-border text-accent'
              : 'text-text-muted hover:text-text-primary'
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>REASONING TRACE PIPELINE</span>
        </button>
      </div>

      {/* 4. Tab Content A: Requirement Verification Ledger */}
      {activeTab === 'ledger' && (
        <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-4">
          {conceptualMatches.length > 0 ? (
            <div className="space-y-3 font-mono text-xs">
              {conceptualMatches.map((cm, idx) => {
                const isExpanded = !!expandedRows[idx];
                const covPct = Math.round((cm.coverage_ratio || 0) * 100);
                const matchLvl = (cm.match_level || 'missing').toUpperCase();

                const isFull = matchLvl === 'FULL' || matchLvl === 'FULL_MATCH';
                const isPartial = matchLvl.includes('PARTIAL') || matchLvl.includes('RELATED') || matchLvl === 'STRONG_MATCH';
                
                const badgeBg = isFull
                  ? 'bg-[var(--accent-2)]/10 border-[var(--accent-2)]/40 text-[var(--accent-2)]'
                  : isPartial
                  ? 'bg-accent/10 border-accent/40 text-accent'
                  : 'bg-[var(--danger-muted)]/10 border-[var(--danger-muted)]/40 text-[var(--danger-muted)]';

                const isSoftSkill = (cm.requirement || '').toLowerCase().includes('communication') ||
                                    (cm.requirement || '').toLowerCase().includes('interpersonal') ||
                                    (cm.requirement || '').toLowerCase().includes('customer');

                const totalConcepts = cm.conceptual_scope?.length || 1;
                const coveredCount = cm.evidence_found?.length || (isFull ? 1 : 0);

                return (
                  <div
                    key={idx}
                    className="bg-bg-base border border-border/60 rounded p-4 space-y-3"
                  >
                    {/* Top Summary Bar */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm text-text-primary">
                            {cm.requirement}
                          </span>
                          <span className="text-[10px] uppercase px-2 py-0.5 rounded border border-border text-text-muted bg-bg-surface">
                            {cm.requirement_type || 'CRITICAL'}
                          </span>
                        </div>

                        <div className="flex items-center space-x-3 text-[11px] text-text-secondary">
                          <span>Coverage: {coveredCount}/{totalConcepts} domains ({covPct}%)</span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <span className={`text-[10px] uppercase px-2.5 py-1 rounded border font-medium ${badgeBg}`}>
                          {matchLvl.replace('_', ' ')} ({covPct}%)
                        </span>

                        <button
                          type="button"
                          onClick={() => toggleRow(idx)}
                          className="px-2.5 py-1 bg-bg-surface border border-border hover:border-accent text-text-primary rounded flex items-center space-x-1 transition-colors text-[11px]"
                          aria-expanded={isExpanded}
                        >
                          <span>{isExpanded ? 'Hide' : 'Why? / Inspect'}</span>
                          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </button>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-border/40 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isFull ? 'bg-[var(--accent-2)]' : isPartial ? 'bg-[var(--accent)]' : 'bg-[var(--danger-muted)]'
                        }`}
                        style={{ width: `${Math.min(Math.max(covPct, 0), 100)}%` }}
                      />
                    </div>

                    {/* Expandable Disclosure Content */}
                    {isExpanded && (
                      <div className="pt-3 border-t border-border/40 space-y-3 text-xs font-mono bg-bg-surface/50 p-3 rounded">
                        {/* Explanation Text */}
                        <div className="space-y-1">
                          <span className="text-[10px] text-text-muted uppercase block">EXPLANATION:</span>
                          {isSoftSkill && covPct === 0 ? (
                            <p className="text-text-secondary font-sans leading-relaxed text-xs italic bg-bg-base border border-border p-2.5 rounded">
                              Insufficient resume evidence. Validate soft skill demonstration during interview rather than treating as proof of absence.
                            </p>
                          ) : (
                            <p className="text-text-primary font-sans leading-relaxed text-xs">
                              "{cm.reasoning || cm.explanation || 'Evaluated via multi-tier conceptual matching engine.'}"
                            </p>
                          )}
                        </div>

                        {/* Evidence Subtopics Breakdown */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                          {cm.evidence_found && cm.evidence_found.length > 0 && (
                            <div className="space-y-1">
                              <span className="text-[10px] text-[var(--accent-2)] uppercase block font-medium">
                                ✓ Evidenced Subtopics ({cm.evidence_found.length}):
                              </span>
                              <div className="flex flex-wrap gap-1">
                                {cm.evidence_found.map((st, i) => (
                                  <span key={i} className="bg-bg-base text-[var(--accent-2)] px-2 py-0.5 rounded border border-[var(--accent-2)]/40 text-[11px]">
                                    ✓ {st}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {cm.critical_subtopics_missing && cm.critical_subtopics_missing.length > 0 && (
                            <div className="space-y-1">
                              <span className="text-[10px] text-[var(--danger-muted)] uppercase block font-medium">
                                ○ Missing Subtopics ({cm.critical_subtopics_missing.length}):
                              </span>
                              <div className="flex flex-wrap gap-1">
                                {cm.critical_subtopics_missing.map((st, i) => (
                                  <span key={i} className="bg-bg-base text-[var(--danger-muted)] px-2 py-0.5 rounded border border-[var(--danger-muted)]/40 text-[11px]">
                                    ○ {st}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-text-muted italic text-xs">No requirement records available.</p>
          )}
        </div>
      )}

      {/* 5. Tab Content B: Reasoning Trace Pipeline */}
      {activeTab === 'trace' && (
        <ReasoningTraceView conceptualMatches={conceptualMatches} evidence={evidence} />
      )}

      {/* 6. Strengths & Concerns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 font-sans text-xs pt-2">
        <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-3">
          <h3 className="text-xs font-mono uppercase tracking-wider text-[var(--accent-2)] flex items-center space-x-2">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>VERIFIED STRENGTHS ({strengths.length})</span>
          </h3>

          {strengths.length > 0 ? (
            <ul className="space-y-2 text-text-primary">
              {strengths.map((st, i) => (
                <li key={i} className="border-b border-border/40 pb-2 last:border-b-0 leading-relaxed">
                  {st}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-text-muted italic">No explicit strengths recorded.</p>
          )}
        </div>

        <div className="bg-bg-surface border border-border rounded-lg p-5 space-y-3">
          <h3 className="text-xs font-mono uppercase tracking-wider text-[var(--danger-muted)] flex items-center space-x-2">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>EVALUATION DISCREPANCIES ({concerns.length})</span>
          </h3>

          {concerns.length > 0 ? (
            <ul className="space-y-2 text-text-primary">
              {concerns.map((cn, i) => (
                <li key={i} className="border-b border-border/40 pb-2 last:border-b-0 leading-relaxed">
                  {cn}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-text-muted italic">No evaluation concerns identified.</p>
          )}
        </div>
      </div>
    </div>
  );
}
