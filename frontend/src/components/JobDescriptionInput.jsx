import { useRef, useState } from 'react';
import { FileText, Sparkles, Trash2, Loader2, ArrowRight, Upload, FileCheck, AlertTriangle } from 'lucide-react';
import JobSummaryCard from './JobSummaryCard';

const SAMPLE_JOB_DESCRIPTION = `Senior Full Stack Engineer (React + Python)

Role Overview:
We are seeking an experienced Senior Full Stack Engineer to lead the design and implementation of high-throughput web applications and screening platforms.

Key Responsibilities:
- Build responsive, accessible UI applications using React, TypeScript, and modern state management.
- Design scalable backend microservices and RESTful APIs using Python and FastAPI.
- Integrate vector databases and semantic search tools for document analysis.
- Collaborate with product managers and recruiters to refine UX workflows and candidate scoring models.

Required Qualifications:
- 5+ years of software engineering experience with JavaScript/TypeScript, React, and Python.
- Proven track record building production REST APIs with FastAPI or Django.
- Experience working with MongoDB or PostgreSQL databases.
- Strong understanding of modern frontend performance, CSS/Tailwind, and accessibility standards.
- Bachelor's degree in Computer Science or equivalent practical experience.`;

const JOB_ICON_URL = 'https://img.icons8.com/pulsar-line/48/lightning-bolt.png';

const PRESET_JDS = [
  {
    label: "Senior Full Stack",
    text: SAMPLE_JOB_DESCRIPTION
  },
  {
    label: "AI / ML Engineer",
    text: `Senior AI / Machine Learning Engineer

Role Overview:
We are seeking an AI Engineer to design and deploy state-of-the-art LLM fine-tuning pipelines and semantic search capabilities.

Key Responsibilities:
- Build, evaluate, and optimize machine learning models using PyTorch, Hugging Face Transformers, and OpenAI/Gemini APIs.
- Implement Retrieval-Augmented Generation (RAG) architectures with Pinecone or Milvus vector databases.
- Deploy scalable model inference services on AWS or GCP using Docker and Kubernetes.

Required Qualifications:
- 4+ years of professional ML/AI engineering experience with Python, PyTorch, and NLP.
- Proven experience with RAG, embedding models, vector indexing, and prompt engineering.
- Solid background in Computer Science fundamentals, linear algebra, and statistics.
- Bachelor's or Master's degree in Computer Science, Data Science, or related field.`
  },
  {
    label: "Cloud & DevOps Architect",
    text: `DevOps & Cloud Infrastructure Architect

Role Overview:
Looking for an experienced Cloud Systems Engineer to automate infrastructure deployment and ensure sub-second application uptime.

Key Responsibilities:
- Manage multi-cluster Kubernetes infrastructure on AWS (EKS) using Terraform and Helm.
- Construct automated CI/CD pipelines using GitHub Actions and ArgoCD.
- Implement robust monitoring, alerting, and observability using Prometheus, Grafana, and Datadog.

Required Qualifications:
- 5+ years of infrastructure engineering experience with AWS, Kubernetes, Terraform, and Linux administration.
- Deep expertise in Docker containerization, networking security (VPC, IAM), and Python/Bash scripting.
- Experience with PostgreSQL, Redis, and MongoDB database administration.
- Bachelor's degree in Computer Science, Information Technology, or equivalent.`
  }
];

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.doc', '.docx'];

export default function JobDescriptionInput({
  value,
  onChange,
  onClear,
  onCreateJob,
  onUploadJobFile,
  isCreatingJob,
  createdJob,
  jobId,
  onResetJob,
  error,
}) {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileValidationError, setFileValidationError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;
  const charCount = value.length;

  if (createdJob && jobId) {
    return <JobSummaryCard job={createdJob} jobId={jobId} onEdit={onResetJob} />;
  }

  const validateAndSetFile = (file) => {
    setFileValidationError(null);
    if (!file) return;

    const extension = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setFileValidationError(`"${file.name}" is invalid. Please select a PDF, TXT, DOC, or DOCX document.`);
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setFileValidationError(`"${file.name}" exceeds 5MB size limit.`);
      return;
    }

    setSelectedFile(file);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setInputMode('file');
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileUploadSubmit = () => {
    if (!selectedFile || isCreatingJob) return;
    if (onUploadJobFile) {
      onUploadJobFile(selectedFile);
    }
  };

  return (
    <div className="bg-bg-surface border border-border rounded-lg p-5 flex flex-col h-full font-sans transition-colors">
      {/* Header Row */}
      <div className="flex items-center justify-between mb-3 border-b border-border/60 pb-3">
        <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-text-primary">
          <FileText className="w-3.5 h-3.5 text-accent" />
          <span>TARGET JOB SPECIFICATION</span>
        </div>

        {/* Requirement 2: Two-Option Segmented Toggle */}
        <div className="flex items-center bg-bg-base p-0.5 rounded border border-border text-xs font-mono">
          <button
            type="button"
            onClick={() => setInputMode('text')}
            className={`px-3 py-1 rounded transition-colors flex items-center space-x-1.5 ${
              inputMode === 'text'
                ? 'bg-bg-surface border border-border-strong text-text-primary font-medium'
                : 'text-text-secondary hover:text-text-primary border border-transparent'
            }`}
          >
            <FileText className="w-3 h-3" />
            <span>PASTE TEXT</span>
          </button>
          <button
            type="button"
            onClick={() => setInputMode('file')}
            className={`px-3 py-1 rounded transition-colors flex items-center space-x-1.5 ${
              inputMode === 'file'
                ? 'bg-bg-surface border border-border-strong text-text-primary font-medium'
                : 'text-text-secondary hover:text-text-primary border border-transparent'
            }`}
          >
            <Upload className="w-3 h-3" />
            <span>UPLOAD FILE</span>
          </button>
        </div>
      </div>

      {inputMode === 'text' ? (
        <>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-2 text-xs font-sans">
            <div className="flex flex-wrap items-center gap-1.5 font-mono text-[11px]">
              <span className="text-text-muted mr-1 font-sans flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-accent shrink-0" />
                <span>Presets:</span>
              </span>
              {PRESET_JDS.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onChange(preset.text)}
                  className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-bg-base border border-accent/40 text-accent hover:bg-accent/15 transition-colors font-medium cursor-pointer"
                >
                  <img
                    src={JOB_ICON_URL}
                    alt="Job spec icon"
                    className="w-3.5 h-3.5 object-contain shrink-0 icon-theme-adaptive"
                  />
                  <span>{preset.label}</span>
                </button>
              ))}
            </div>
            <div className="flex items-center space-x-2 font-mono shrink-0">
              {value && (
                <button
                  type="button"
                  onClick={onClear}
                  className="btn-ghost text-xs text-text-muted hover:text-[var(--danger-muted)] flex items-center space-x-1"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>CLEAR</span>
                </button>
              )}
            </div>
          </div>

          <div className="relative flex-1 flex flex-col min-h-[200px]">
            <textarea
              id="job-description-input"
              data-scroll-prevent="true"
              data-lenis-prevent="true"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onWheel={(e) => {
                const el = e.currentTarget;
                if (el.scrollHeight > el.clientHeight) {
                  const isAtTop = el.scrollTop === 0 && e.deltaY < 0;
                  const isAtBottom =
                    Math.abs(el.scrollHeight - el.clientHeight - el.scrollTop) < 1 && e.deltaY > 0;
                  if (!isAtTop && !isAtBottom) {
                    e.stopPropagation();
                  }
                }
              }}
              placeholder="Paste job description requirements..."
              rows={8}
              disabled={isCreatingJob}
              className="w-full flex-1 bg-bg-surface border border-border rounded p-3.5 text-xs sm:text-sm text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-[var(--accent)] resize-y font-sans leading-relaxed overflow-y-auto min-h-[180px]"
              aria-describedby="jd-helper-text"
            />
          </div>

          {error && (
            <div className="mt-3 text-xs font-mono text-[var(--danger-muted)] bg-bg-base border border-[var(--danger-muted)]/40 rounded p-2.5">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between mt-3 text-[11px] text-text-muted border-t border-border/60 pt-2.5 font-mono">
            <span id="jd-helper-text">50+ characters required for optimal assay</span>
            <div className="flex items-center space-x-3">
              <span>{wordCount} WORDS</span>
              <span>•</span>
              <span>{charCount} CHARS</span>
            </div>
          </div>

          <div className="mt-3">
            {/* Requirement 1: Primary Button variant with dark ink text on copper fill */}
            <button
              type="button"
              disabled={!value.trim() || isCreatingJob}
              onClick={onCreateJob}
              className="btn-primary w-full"
            >
              {isCreatingJob ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
                  <span>DECOMPOSING SPECIFICATION...</span>
                </>
              ) : (
                <>
                  <span>SAVE &amp; DECOMPOSE JOB SPECIFICATION</span>
                  <ArrowRight className="w-3.5 h-3.5 text-current" />
                </>
              )}
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="text-xs text-text-secondary mb-3 leading-relaxed">
            Upload Job Description file (.PDF, .TXT, .DOC, .DOCX). Requirements will be decomposed into sub-topic claims.
          </p>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.txt,.doc,.docx,application/pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="hidden"
            id="jd-file-input"
          />

          {/* Requirement 3: 1px dashed border switching to solid --accent on drag-over */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            tabIndex={0}
            role="button"
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            aria-label="Upload PDF or TXT Job Description"
            className={`flex-1 min-h-[180px] rounded p-6 text-center cursor-pointer flex flex-col items-center justify-center transition-colors font-mono text-xs ${
              isDragOver
                ? 'border-2 border-solid border-accent bg-bg-surface'
                : selectedFile
                ? 'border border-solid border-[var(--accent-2)] bg-bg-surface'
                : 'border border-dashed border-border bg-bg-surface hover:border-border-strong'
            }`}
          >
            {selectedFile ? (
              <div className="flex flex-col items-center space-y-2">
                <FileCheck className="w-6 h-6 text-[var(--accent-2)]" />
                <p className="text-xs font-medium text-text-primary truncate max-w-[240px]">
                  {selectedFile.name}
                </p>
                <p className="text-[11px] text-text-muted">
                  {(selectedFile.size / 1024).toFixed(1)} KB • Click or drop to replace
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-2">
                <Upload className="w-6 h-6 text-accent" />
                <div>
                  <p className="text-xs font-medium text-text-primary">
                    <span className="text-accent font-medium">Click to select file</span> or drag &amp; drop document
                  </p>
                  <p className="text-[11px] text-text-muted mt-1">
                    PDF, TXT, DOC, or DOCX format (Max 5MB)
                  </p>
                </div>
              </div>
            )}
          </div>

          {(fileValidationError || error) && (
            <div className="mt-3 bg-bg-base border border-[var(--danger-muted)]/40 rounded p-2.5 text-xs font-mono text-[var(--danger-muted)] flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{fileValidationError || error}</span>
            </div>
          )}

          <div className="mt-4">
            <button
              type="button"
              disabled={!selectedFile || isCreatingJob}
              onClick={handleFileUploadSubmit}
              className="btn-primary w-full"
            >
              {isCreatingJob ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
                  <span>PARSING &amp; DECOMPOSING SPECIFICATION...</span>
                </>
              ) : (
                <>
                  <span>UPLOAD &amp; DECOMPOSE JOB SPECIFICATION</span>
                  <ArrowRight className="w-3.5 h-3.5 text-current" />
                </>
              )}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
