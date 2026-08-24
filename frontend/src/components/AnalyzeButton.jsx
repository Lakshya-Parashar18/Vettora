import { BrainCircuit, ArrowRight, AlertCircle } from 'lucide-react';

export default function AnalyzeButton({ isDisabled, disabledReason, onAnalyze, candidateCount }) {
  return (
    <div className="flex flex-col items-center justify-center pt-2 pb-4 font-mono">
      <button
        type="button"
        disabled={isDisabled}
        onClick={onAnalyze}
        className={`w-full max-w-md flex items-center justify-center space-x-2 py-3 px-6 rounded font-mono text-xs font-medium uppercase tracking-wider transition-colors ${
          isDisabled
            ? 'bg-bg-base border border-border text-text-muted cursor-not-allowed'
            : 'bg-accent hover:bg-accent-hover text-white border border-accent'
        }`}
      >
        <BrainCircuit className="w-4 h-4 text-current" />
        <span>EXECUTE CANDIDATE ASSAY</span>

        {!isDisabled && candidateCount > 0 && (
          <span className="ml-1 px-2 py-0.5 text-[10px] bg-white/20 text-white rounded font-mono">
            {candidateCount}
          </span>
        )}

        {!isDisabled && <ArrowRight className="w-3.5 h-3.5 text-white" />}
      </button>

      {isDisabled && disabledReason && (
        <div className="flex items-center space-x-1.5 text-xs text-text-muted mt-2.5 font-mono">
          <AlertCircle className="w-3.5 h-3.5 text-[var(--accent)] shrink-0" />
          <span>{disabledReason}</span>
        </div>
      )}

      {!isDisabled && (
        <div className="text-[11px] text-text-muted mt-2 font-mono">
          Ready to execute evidence decomposition and conceptual screening
        </div>
      )}
    </div>
  );
}
