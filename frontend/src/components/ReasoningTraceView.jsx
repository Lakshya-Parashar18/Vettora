import { useState } from 'react';
import { ArrowRight, ShieldCheck } from 'lucide-react';

export default function ReasoningTraceView({ conceptualMatches = [] }) {
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!conceptualMatches || conceptualMatches.length === 0) {
    return (
      <div className="bg-bg-base border border-border rounded p-6 text-center text-xs font-mono text-text-muted">
        No structured reasoning trace records available.
      </div>
    );
  }

  const selectedMatch = conceptualMatches[selectedIdx] || conceptualMatches[0];
  const isSoftSkill = (selectedMatch.requirement || '').toLowerCase().includes('communication') || 
                      (selectedMatch.requirement || '').toLowerCase().includes('interpersonal') || 
                      (selectedMatch.requirement || '').toLowerCase().includes('customer');

  return (
    <div className="space-y-4 font-sans text-xs">
      <div className="flex items-center space-x-2 text-xs font-mono text-accent uppercase tracking-wider">
        <ShieldCheck className="w-3.5 h-3.5 text-accent" />
        <span>INTELLIGENCE REASONING TRACE PIPELINE</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Left Column: Requirements Selector List (4 cols) */}
        <div className="md:col-span-4 bg-bg-base border border-border rounded-lg p-2 space-y-1 font-mono text-xs max-h-96 overflow-y-auto">
          <span className="text-[10px] text-text-muted uppercase px-2 py-1 block">
            Target Requirements ({conceptualMatches.length})
          </span>
          {conceptualMatches.map((cm, idx) => {
            const isSelected = idx === selectedIdx;
            const pct = Math.round((cm.coverage_ratio || 0) * 100);
            return (
              <button
                key={idx}
                type="button"
                onClick={() => setSelectedIdx(idx)}
                className={`w-full text-left px-3 py-2.5 rounded transition-colors flex items-center justify-between gap-2 ${
                  isSelected
                    ? 'bg-bg-surface border border-accent text-text-primary font-medium'
                    : 'hover:bg-bg-surface/60 text-text-secondary border border-transparent'
                }`}
              >
                <span className="truncate">{cm.requirement}</span>
                <span
                  className={`text-[10px] font-mono shrink-0 px-1.5 py-0.5 rounded ${
                    pct >= 70
                      ? 'bg-[var(--accent-2)]/10 text-[var(--accent-2)] border border-[var(--accent-2)]/30'
                      : pct > 0
                      ? 'bg-accent/10 text-accent border border-accent/30'
                      : 'bg-[var(--danger-muted)]/10 text-[var(--danger-muted)] border border-[var(--danger-muted)]/30'
                  }`}
                >
                  {pct}%
                </span>
              </button>
            );
          })}
        </div>

        {/* Right Column: Reasoning Trace Step-by-Step Diagram (8 cols) */}
        <div className="md:col-span-8 bg-bg-base border border-border rounded-lg p-4 space-y-4 font-mono">
          <div className="flex items-center justify-between border-b border-border/60 pb-3">
            <h4 className="font-sans text-sm font-medium text-text-primary">
              Trace: {selectedMatch.requirement}
            </h4>
            <span className="text-[10px] uppercase bg-bg-surface border border-border px-2 py-0.5 rounded text-accent">
              {selectedMatch.match_level || 'EVALUATED'}
            </span>
          </div>

          {/* Trace Pipeline Steps */}
          <div className="space-y-3 font-mono text-xs">
            {/* Step 1: JD Requirement */}
            <div className="bg-bg-surface border border-border/60 rounded p-3 space-y-1">
              <div className="flex items-center space-x-2 text-[10px] text-text-muted uppercase">
                <span className="bg-accent/20 text-accent px-1.5 py-0.2 rounded">STEP 1</span>
                <span>JD Requirement</span>
              </div>
              <p className="font-medium text-text-primary text-xs">{selectedMatch.requirement}</p>
            </div>

            <div className="flex justify-center text-text-muted">
              <ArrowRight className="w-3.5 h-3.5 transform rotate-90" />
            </div>

            {/* Step 2: Decomposed Sub-Concepts */}
            <div className="bg-bg-surface border border-border/60 rounded p-3 space-y-1">
              <div className="flex items-center space-x-2 text-[10px] text-text-muted uppercase">
                <span className="bg-accent/20 text-accent px-1.5 py-0.2 rounded">STEP 2</span>
                <span>Ontology Sub-Concepts</span>
              </div>
              {selectedMatch.conceptual_scope && selectedMatch.conceptual_scope.length > 0 ? (
                <div className="flex flex-wrap gap-1 pt-1">
                  {selectedMatch.conceptual_scope.map((st, i) => (
                    <span key={i} className="bg-bg-base text-text-secondary px-2 py-0.5 rounded border border-border text-[11px]">
                      {st}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-text-secondary italic text-xs">Single concept target.</p>
              )}
            </div>

            <div className="flex justify-center text-text-muted">
              <ArrowRight className="w-3.5 h-3.5 transform rotate-90" />
            </div>

            {/* Step 3: Evidenced vs Missing Subtopics */}
            <div className="bg-bg-surface border border-border/60 rounded p-3 space-y-2">
              <div className="flex items-center space-x-2 text-[10px] text-text-muted uppercase">
                <span className="bg-accent/20 text-accent px-1.5 py-0.2 rounded">STEP 3</span>
                <span>Resume Evidence Extraction</span>
              </div>

              {selectedMatch.evidence_found && selectedMatch.evidence_found.length > 0 ? (
                <div className="space-y-1">
                  <span className="text-[10px] text-[var(--accent-2)] uppercase block">Evidenced ({selectedMatch.evidence_found.length}):</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedMatch.evidence_found.map((st, i) => (
                      <span key={i} className="bg-[var(--accent-2)]/10 text-[var(--accent-2)] px-2 py-0.5 rounded border border-[var(--accent-2)]/40 text-[11px]">
                        ✓ {st}
                      </span>
                    ))}
                  </div>
                </div>
              ) : isSoftSkill ? (
                <div className="bg-bg-base border border-border rounded p-2.5 text-[11px] text-text-secondary italic">
                  Insufficient resume evidence. Validate soft skill demonstration during interview rather than treating as proof of absence.
                </div>
              ) : (
                <div className="text-[11px] text-[var(--danger-muted)] italic">
                  No direct resume evidence found.
                </div>
              )}

              {selectedMatch.critical_subtopics_missing && selectedMatch.critical_subtopics_missing.length > 0 && (
                <div className="space-y-1 pt-1">
                  <span className="text-[10px] text-[var(--danger-muted)] uppercase block">Missing Subtopics ({selectedMatch.critical_subtopics_missing.length}):</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedMatch.critical_subtopics_missing.map((st, i) => (
                      <span key={i} className="bg-[var(--danger-muted)]/10 text-[var(--danger-muted)] px-2 py-0.5 rounded border border-[var(--danger-muted)]/40 text-[11px]">
                        ○ {st}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-center text-text-muted">
              <ArrowRight className="w-3.5 h-3.5 transform rotate-90" />
            </div>

            {/* Step 4: Decision Explanation */}
            <div className="bg-bg-surface border border-border/60 rounded p-3 space-y-1">
              <div className="flex items-center space-x-2 text-[10px] text-text-muted uppercase">
                <span className="bg-accent/20 text-accent px-1.5 py-0.2 rounded">STEP 4</span>
                <span>Evidence-Based Decision Factor</span>
              </div>
              <p className="font-sans text-xs text-text-primary leading-relaxed pt-1 italic">
                "{selectedMatch.reasoning || selectedMatch.explanation || 'Evaluated via deterministic multi-tier evidence engine.'}"
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
