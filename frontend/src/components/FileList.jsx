import {
  FileText,
  FileCode,
  Trash2,
  Users,
  XCircle,
  Loader2,
} from 'lucide-react';

export default function FileList({ files, onRemoveFile, onClearAll }) {
  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileTypeBadge = (filename) => {
    const ext = (filename || '').split('.').pop().toLowerCase();
    if (ext === 'pdf') {
      return { label: 'PDF', icon: FileText };
    }
    return { label: 'TXT', icon: FileCode };
  };

  if (!files || files.length === 0) {
    return (
      <div className="bg-bg-surface border border-border border-dashed rounded-lg p-5 text-center my-3 transition-colors font-sans">
        <Users className="w-5 h-5 text-text-muted mx-auto mb-1.5" />
        <p className="text-xs font-medium text-text-primary">
          Upload resumes to begin — Vettora reads PDF, DOC, DOCX, and TXT.
        </p>
        <p className="text-[11px] text-text-muted mt-1 font-mono">
          Batch candidate records will list here prior to assay screening.
        </p>
      </div>
    );
  }

  const processedFiles = files.filter((f) => f.status === 'processed' || (!f.status && f.resume_id));
  const failedFiles = files.filter((f) => f.status === 'failed');

  return (
    <div className="mt-4 space-y-3 font-mono text-xs">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center space-x-2">
          <span className="text-[10px] text-text-muted uppercase tracking-wider">
            BATCH RESUME QUEUE
          </span>
          <span className="text-[10px] text-text-primary bg-bg-surface border border-border px-2 py-0.5 rounded">
            {processedFiles.length} READY / {files.length} TOTAL
          </span>
        </div>

        {files.length > 1 && (
          <button
            type="button"
            onClick={onClearAll}
            className="btn-ghost text-[10px] hover:text-[var(--danger-muted)] uppercase"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>REMOVE ALL</span>
          </button>
        )}
      </div>

      <div
        onWheel={(e) => e.stopPropagation()}
        onTouchMove={(e) => e.stopPropagation()}
        className="space-y-2 max-h-[260px] overflow-y-auto pr-1"
      >
        {files.map((file, index) => {
          const badge = getFileTypeBadge(file.name || 'resume.pdf');
          const Icon = badge.icon;

          const isProcessed = file.status === 'processed' || (!file.status && file.resume_id);
          const isFailed = file.status === 'failed';
          const isPending = file.status === 'uploading';
          const candidateName = file.candidate?.name || file.candidate_name;

          return (
            <div
              key={`${file.name}-${index}`}
              className="group flex flex-col bg-bg-surface border border-border rounded p-3 transition-colors hover:border-border-strong"
            >
              <div className="flex items-center justify-between min-w-0">
                <div className="flex items-center space-x-3 min-w-0 pr-2">
                  <Icon className="w-4 h-4 text-accent shrink-0" />

                  <div className="min-w-0">
                    <div className="flex items-center space-x-2">
                      <p className="font-sans text-xs font-medium text-text-primary truncate">
                        {file.name}
                      </p>
                      {candidateName && (
                        <span className="text-xs text-text-secondary font-normal truncate">
                          ({candidateName})
                        </span>
                      )}
                    </div>

                    {/* Requirement 3: Processed status as small --accent-2 mono label (no green badge) */}
                    <div className="flex items-center space-x-2 mt-0.5 text-[10px] text-text-muted">
                      <span className="font-mono text-text-muted">{badge.label}</span>
                      <span>•</span>
                      {isProcessed && (
                        <span className="text-[var(--accent-2)] font-mono font-medium">
                          PROCESSED
                        </span>
                      )}
                      {isFailed && (
                        <span className="text-[var(--danger-muted)] font-mono font-medium">
                          UNREADABLE
                        </span>
                      )}
                      {isPending && (
                        <span className="text-accent font-mono font-medium flex items-center space-x-1">
                          <Loader2 className="w-2.5 h-2.5 animate-spin" />
                          <span>PARSING</span>
                        </span>
                      )}
                      <span>•</span>
                      <span>{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                </div>

                {/* Requirement 3: Delete icon as ghost button appearing on row hover only */}
                <button
                  type="button"
                  onClick={() => onRemoveFile(index)}
                  className="btn-ghost p-1.5 opacity-0 group-hover:opacity-100 transition-opacity hover:text-[var(--danger-muted)]"
                  title={`Remove ${file.name}`}
                  aria-label={`Remove file ${file.name}`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {isFailed && file.error && (
                <div className="mt-2 text-[11px] text-[var(--danger-muted)] bg-bg-base border border-[var(--danger-muted)]/30 rounded p-2">
                  {typeof file.error === 'string'
                    ? file.error
                    : file.error.message || 'File unreadable. Please upload valid PDF, DOCX, or TXT file.'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {failedFiles.length > 0 && processedFiles.length > 0 && (
        <div className="p-2.5 bg-bg-surface border border-border rounded text-[11px] text-text-secondary font-mono">
          <span>{processedFiles.length} candidate documents ready for screening. Unreadable files omitted.</span>
        </div>
      )}
    </div>
  );
}
