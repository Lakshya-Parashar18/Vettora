import { FileText, Upload, BrainCircuit } from 'lucide-react';

export default function WorkflowSteps({ currentStep = 1 }) {
  const steps = [
    {
      number: '01',
      title: 'Job Description',
      desc: 'Define role requirements',
      icon: FileText,
    },
    {
      number: '02',
      title: 'Upload Resumes',
      desc: 'Add candidate PDF/DOC/TXT files',
      icon: Upload,
    },
    {
      number: '03',
      title: 'Assay Evaluation',
      desc: 'Execute evidence screening',
      icon: BrainCircuit,
    },
  ];

  return (
    <div className="w-full bg-bg-surface border border-border rounded-lg p-4 mb-8 font-mono text-xs">
      <div className="flex items-center justify-between text-text-muted mb-3 pb-2 border-b border-border/50 text-[11px] uppercase tracking-wider">
        <span>Assay Procedure Workflow</span>
        <span>01 · 02 · 03 Sequence</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === idx + 1;
          const isDone = currentStep > idx + 1;

          return (
            <div
              key={step.number}
              className={`flex items-center p-3 rounded border transition-colors ${
                isActive
                  ? 'border-accent bg-bg-base text-text-primary'
                  : isDone
                  ? 'border-accent-2/60 bg-bg-surface text-text-secondary'
                  : 'border-border bg-bg-surface text-text-muted opacity-80'
              }`}
            >
              <span
                className={`font-mono text-xs font-medium mr-3 ${
                  isActive
                    ? 'text-accent'
                    : isDone
                    ? 'text-accent-2'
                    : 'text-text-muted'
                }`}
              >
                {step.number} ·
              </span>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-sans font-medium text-xs text-text-primary truncate">
                    {step.title}
                  </span>
                  <Icon
                    className={`w-3.5 h-3.5 ml-1 shrink-0 ${
                      isActive ? 'text-accent' : isDone ? 'text-accent-2' : 'text-text-muted'
                    }`}
                  />
                </div>
                <p className="font-sans text-[11px] text-text-secondary truncate mt-0.5 font-normal">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
