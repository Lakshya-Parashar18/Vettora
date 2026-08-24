import { useEffect, useState } from 'react';
import { ArrowLeft, ShieldCheck, Database, Cpu, Server, Sparkles } from 'lucide-react';

const SEQUENTIAL_STATUS_MESSAGES = [
  'Parsing resumes and extracting candidate claims…',
  'Decomposing job specification sub-topics…',
  'Matching candidate evidence against decomposed scope…',
  'Calculating conceptual coverage ratios…',
  'Stamping evaluations & compiling assay ledger…',
];

export default function ProcessingState({
  statusMessage,
  currentStage,
  candidateCount,
  onReset,
  isComplete,
}) {
  const [seqIndex, setSeqIndex] = useState(0);

  useEffect(() => {
    if (isComplete) return;

    const interval = setInterval(() => {
      setSeqIndex((prev) => (prev + 1) % SEQUENTIAL_STATUS_MESSAGES.length);
    }, 1400);

    return () => clearInterval(interval);
  }, [isComplete]);

  const displayMessage =
    statusMessage || SEQUENTIAL_STATUS_MESSAGES[seqIndex];

  const steps = [
    {
      id: 'prep',
      name: 'PARSING RESUMES & CLAIMS',
      desc: `Extracting candidate profiles from upload queue (${candidateCount} candidates)`,
      icon: Database,
      stageIndex: 1,
    },
    {
      id: 'eval',
      name: 'DECOMPOSING SPECIFICATION',
      desc: 'Decomposing requirement claims into sub-topic parameters',
      icon: Server,
      stageIndex: 2,
    },
    {
      id: 'scoring',
      name: 'MATCHING EVIDENCE FIT',
      desc: 'Executing two-step LLM sub-topic match & deterministic scoring',
      icon: Cpu,
      stageIndex: 3,
    },
    {
      id: 'ranking',
      name: 'STAMPING EVALUATIONS',
      desc: 'Persisting candidate assay ledger and calculating final match scores',
      icon: Sparkles,
      stageIndex: 4,
    },
  ];

  return (
    <div className="bg-bg-surface border border-border rounded-lg p-6 max-w-2xl mx-auto my-6 font-sans transition-colors">
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center h-12 w-12 rounded-full border border-accent bg-bg-base text-accent mb-3">
          {isComplete ? (
            <span className="font-mono text-lg text-[var(--accent-2)]">✓</span>
          ) : (
            <span className="font-mono text-xs font-medium text-accent">ASSAY</span>
          )}
        </div>

        <h3 className="font-display font-medium text-xl text-text-primary">
          {isComplete ? 'Candidate Verification Complete' : 'Executing Candidate Verification Assay'}
        </h3>

        {/* Requirement 6: Sequential Mono Status Text */}
        <p className="font-mono text-xs text-accent mt-2 uppercase tracking-wider min-h-[20px] transition-all">
          {displayMessage}
        </p>
      </div>

      <div className="bg-bg-base border border-border/60 rounded p-4 mb-6 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between text-[10px] text-text-muted pb-2 border-b border-border/60 uppercase">
          <span>ASSAY PIPELINE STAGE</span>
          <span>STATUS</span>
        </div>

        {steps.map((step) => {
          const Icon = step.icon;
          const isDone = isComplete || (currentStage && currentStage > step.stageIndex);
          const isActive = !isComplete && currentStage === step.stageIndex;

          return (
            <div
              key={step.id}
              className={`flex items-start justify-between text-xs space-x-3 p-2 rounded transition-colors ${
                isActive ? 'bg-bg-surface border border-accent/40' : ''
              }`}
            >
              <div className="flex items-start space-x-2.5">
                <Icon
                  className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${
                    isDone
                      ? 'text-[var(--accent-2)]'
                      : isActive
                      ? 'text-accent'
                      : 'text-text-muted'
                  }`}
                />
                <div>
                  <div className={`font-mono font-medium text-xs ${isActive ? 'text-accent' : 'text-text-primary'}`}>
                    {step.name}
                  </div>
                  <div className="text-[11px] text-text-secondary font-sans mt-0.5">{step.desc}</div>
                </div>
              </div>

              <div className="shrink-0 font-mono text-[10px]">
                {isDone ? (
                  <span className="text-[var(--accent-2)] font-medium">COMPLETED</span>
                ) : isActive ? (
                  <span className="text-accent font-medium uppercase tracking-wider">
                    RUNNING…
                  </span>
                ) : (
                  <span className="text-text-muted">QUEUED</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-bg-base border border-border/60 rounded p-3 text-xs text-text-secondary font-sans flex items-start space-x-2.5 mb-6">
        <ShieldCheck className="w-4 h-4 text-accent shrink-0 mt-0.5" />
        <p className="leading-relaxed text-xs">
          <strong className="font-mono text-text-primary uppercase text-[11px] block mb-0.5">Assay Verification Engine:</strong>
          Requirement claims are broken into sub-topic evidence parameters prior to conceptual candidate evaluation.
        </p>
      </div>

      <div className="flex justify-center font-mono">
        <button
          type="button"
          onClick={onReset}
          className="btn-secondary text-xs"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>RETURN TO WORKSPACE</span>
        </button>
      </div>
    </div>
  );
}
