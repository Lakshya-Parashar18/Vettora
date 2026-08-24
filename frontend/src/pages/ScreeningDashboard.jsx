import { useState, useEffect } from 'react';
import WorkflowSteps from '../components/WorkflowSteps';
import JobDescriptionInput from '../components/JobDescriptionInput';
import ResumeUploader from '../components/ResumeUploader';
import FileList from '../components/FileList';
import AnalyzeButton from '../components/AnalyzeButton';
import ProcessingState from '../components/ProcessingState';
import ResultsView from '../components/ResultsView';
import CandidateDetailView from '../components/CandidateDetailView';
import {
  submitJobDescriptionToApi,
  uploadJobDescriptionFileToApi,
  uploadResumesToApi,
  screenCandidatesApi,
} from '../services/api';
import { Upload, AlertCircle } from 'lucide-react';

export default function ScreeningDashboard() {
  const [jobDescription, setJobDescription] = useState('');
  const [jobId, setJobId] = useState(null);
  const [structuredJob, setStructuredJob] = useState(null);
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [jobError, setJobError] = useState(null);

  const [selectedResumes, setSelectedResumes] = useState([]);
  const [isUploadingResumes, setIsUploadingResumes] = useState(false);
  const [uploadValidationError, setUploadValidationError] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const [appState, setAppState] = useState('workspace'); // 'workspace', 'screening', 'results', 'candidate'
  const [activeEvaluationId, setActiveEvaluationId] = useState(null);
  const [screeningStage, setScreeningStage] = useState(1);
  const [screeningStatus, setScreeningStatus] = useState('');
  const [screeningResults, setScreeningResults] = useState(null);
  const [screeningError, setScreeningError] = useState(null);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash.startsWith('#candidate/')) {
        const evalId = hash.replace('#candidate/', '');
        setActiveEvaluationId(evalId);
        setAppState('candidate');
      } else if (hash.startsWith('#results/') && jobId) {
        setAppState('results');
      } else if (!hash || hash === '#workspace') {
        setAppState('workspace');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [jobId]);

  const handleCreateJob = async () => {
    if (!jobDescription.trim() || isCreatingJob) return;

    setIsCreatingJob(true);
    setJobError(null);

    try {
      const res = await submitJobDescriptionToApi(jobDescription);
      if (res.status === 'processed' && res.job) {
        setJobId(res.job_id);
        setStructuredJob(res.job);
      } else if (res.error) {
        setJobError(res.error.message || 'Job description could not be analyzed.');
      } else {
        setJobError('Failed to process Job Description.');
      }
    } catch (err) {
      setJobError(
        typeof err === 'string'
          ? err
          : err.message || 'Could not connect to the screening service.'
      );
    } finally {
      setIsCreatingJob(false);
    }
  };

  const handleUploadJobFile = async (file) => {
    if (!file || isCreatingJob) return;

    setIsCreatingJob(true);
    setJobError(null);

    try {
      const res = await uploadJobDescriptionFileToApi(file);
      if (res.status === 'processed' && res.job) {
        setJobId(res.job_id);
        setStructuredJob(res.job);
      } else if (res.error) {
        setJobError(res.error.message || 'Job description file could not be analyzed.');
      } else {
        setJobError('Failed to process uploaded Job Description file.');
      }
    } catch (err) {
      setJobError(
        typeof err === 'string'
          ? err
          : err.message || 'Could not upload Job Description file.'
      );
    } finally {
      setIsCreatingJob(false);
    }
  };

  const handleResetJob = () => {
    setJobId(null);
    setStructuredJob(null);
    setJobError(null);
  };

  const handleFilesSelected = async (newFiles) => {
    if (!newFiles || newFiles.length === 0) return;

    setUploadError(null);

    const existingNames = new Set(selectedResumes.map((f) => f.name));
    const uniqueFiles = newFiles.filter((f) => !existingNames.has(f.name));

    if (uniqueFiles.length === 0) {
      setUploadValidationError('Selected file(s) have already been added to the queue.');
      return;
    }

    const pendingItems = uniqueFiles.map((file) => ({
      name: file.name,
      size: file.size,
      status: 'uploading',
      candidate: null,
      resume_id: null,
    }));

    setSelectedResumes((prev) => [...prev, ...pendingItems]);
    setIsUploadingResumes(true);

    try {
      const res = await uploadResumesToApi(uniqueFiles);
      if (res && res.resumes) {
        setSelectedResumes((prev) => {
          const updated = [...prev];
          res.resumes.forEach((retItem) => {
            const matchIdx = updated.findIndex(
              (f) => f.name === retItem.filename && f.status === 'uploading'
            );
            if (matchIdx !== -1) {
              updated[matchIdx] = {
                name: retItem.filename,
                size: updated[matchIdx].size,
                status: retItem.status || 'processed',
                resume_id: retItem.resume_id || null,
                candidate: retItem.candidate || null,
                error: retItem.error
                  ? retItem.error.message || 'Processing failed'
                  : null,
              };
            }
          });
          return updated;
        });
      }
    } catch {
      setUploadError('One or more resumes could not be processed.');
      setSelectedResumes((prev) =>
        prev.map((f) =>
          f.status === 'uploading'
            ? { ...f, status: 'failed', error: 'Upload or text extraction failed.' }
            : f
        )
      );
    } finally {
      setIsUploadingResumes(false);
    }
  };

  const handleRemoveFile = (indexToRemove) => {
    setSelectedResumes((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const processedResumes = selectedResumes.filter(
    (f) => (f.status === 'processed' || (!f.status && f.resume_id)) && f.resume_id
  );
  const validResumeIds = processedResumes.map((f) => f.resume_id);

  const isJdMissing = !jobId;
  const hasNoValidResumes = validResumeIds.length === 0;
  const isAnalyzeDisabled = isJdMissing || hasNoValidResumes || isUploadingResumes || isCreatingJob;

  let disabledReason = '';
  if (isJdMissing && hasNoValidResumes) {
    disabledReason = 'Please structure a Job Description and upload at least one valid resume.';
  } else if (isJdMissing) {
    disabledReason = 'Please structure and save your Job Description to proceed.';
  } else if (hasNoValidResumes) {
    disabledReason = 'Please upload at least one valid resume (.pdf or .txt).';
  } else if (isUploadingResumes) {
    disabledReason = 'Please wait for file processing to complete.';
  }

  const currentStep = isJdMissing ? 1 : hasNoValidResumes ? 2 : 3;

  const handleAnalyzeCandidates = async () => {
    if (isAnalyzeDisabled) return;

    setAppState('screening');
    setScreeningError(null);
    setScreeningStage(1);
    setScreeningStatus('Preparing candidates & loading profiles from database...');

    try {
      await new Promise((resolve) => setTimeout(resolve, 400));
      setScreeningStage(2);
      setScreeningStatus('Evaluating requirements against job profile...');

      await new Promise((resolve) => setTimeout(resolve, 400));
      setScreeningStage(3);
      setScreeningStatus('Calculating criteria scores & running semantic engine...');

      const apiResult = await screenCandidatesApi(jobId, validResumeIds);

      setScreeningStage(4);
      setScreeningStatus('Ranking candidates by final score...');
      await new Promise((resolve) => setTimeout(resolve, 300));

      setScreeningResults(apiResult);
      setAppState('results');
      window.location.hash = `#results/${jobId}`;
    } catch (err) {
      setScreeningError(
        typeof err === 'string'
          ? err
          : err.message || 'Could not complete candidate screening.'
      );
      setAppState('workspace');
    }
  };

  const handleBackToWorkspace = () => {
    setAppState('workspace');
    window.location.hash = '#workspace';
  };

  const handleViewEvaluation = (evalId) => {
    setActiveEvaluationId(evalId);
    setAppState('candidate');
    window.location.hash = `#candidate/${evalId}`;
  };

  const handleBackToResults = () => {
    setAppState('results');
    window.location.hash = `#results/${jobId}`;
  };

  if (appState === 'candidate') {
    return (
      <main className="flex-1 app-container py-6 sm:py-8 flex flex-col justify-between">
        <CandidateDetailView
          evaluationId={activeEvaluationId}
          onBackToResults={handleBackToResults}
        />
      </main>
    );
  }

  if (appState === 'results') {
    return (
      <main className="flex-1 app-container py-6 sm:py-8 flex flex-col justify-between">
        <ResultsView
          jobId={jobId}
          initialResults={screeningResults}
          onBackToWorkspace={handleBackToWorkspace}
          onViewEvaluation={handleViewEvaluation}
        />
      </main>
    );
  }

  return (
    <main className="flex-1 app-container py-6 sm:py-8 flex flex-col justify-between">
      <div>
        <div className="mb-6 border-b border-border/60 pb-4">
          <h1 className="font-display font-medium text-2xl text-text-primary tracking-tight">
            Candidate Verification Workspace
          </h1>
          <p className="font-mono text-xs text-text-muted mt-1 uppercase tracking-wider">
            evidence-based candidate screening &amp; conceptual fit verification
          </p>
        </div>

        <WorkflowSteps currentStep={appState === 'screening' ? 3 : currentStep} />

        {screeningError && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-600 dark:text-red-300 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
              <span>{screeningError}</span>
            </div>
            <button
              type="button"
              onClick={() => setScreeningError(null)}
              className="text-red-500 hover:opacity-80 font-mono text-[11px]"
            >
              Dismiss
            </button>
          </div>
        )}

        {appState === 'screening' ? (
          <ProcessingState
            statusMessage={screeningStatus}
            currentStage={screeningStage}
            candidateCount={validResumeIds.length}
            onReset={handleBackToWorkspace}
            isComplete={false}
          />
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
              
              <div className="flex flex-col h-full min-w-0">
                <JobDescriptionInput
                  value={jobDescription}
                  onChange={setJobDescription}
                  onClear={() => {
                    setJobDescription('');
                    handleResetJob();
                  }}
                  onCreateJob={handleCreateJob}
                  onUploadJobFile={handleUploadJobFile}
                  isCreatingJob={isCreatingJob}
                  createdJob={structuredJob}
                  jobId={jobId}
                  onResetJob={handleResetJob}
                  error={jobError}
                />
              </div>

              <div className="bg-bg-surface border border-border-default rounded-xl p-5 shadow-xs flex flex-col justify-between h-full min-w-0 transition-colors">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="flex items-center text-sm font-semibold text-text-primary space-x-2">
                      <Upload className="w-4 h-4 text-accent" />
                      <span>Resume Upload</span>
                      <span className="text-red-500 font-bold">*</span>
                    </h3>
                    <span className="text-[11px] font-mono text-text-muted">PDF / TXT / DOC / DOCX</span>
                  </div>

                  <p className="text-xs text-text-secondary mb-4 leading-relaxed">
                    Upload candidate resumes. Supports batch upload.
                  </p>

                  <ResumeUploader
                    onFilesSelected={handleFilesSelected}
                    validationError={uploadValidationError}
                    setValidationError={setUploadValidationError}
                  />

                  {uploadError && (
                    <div className="mt-3 text-xs text-amber-600 bg-amber-500/10 border border-amber-500/30 rounded-lg p-2.5 flex items-center justify-between">
                      <span>{uploadError}</span>
                      <button
                        type="button"
                        onClick={() => setUploadError(null)}
                        className="text-amber-600 font-mono text-[10px]"
                      >
                        Dismiss
                      </button>
                    </div>
                  )}

                  <FileList
                    files={selectedResumes}
                    onRemoveFile={handleRemoveFile}
                    onClearAll={() => setSelectedResumes([])}
                    isUploading={isUploadingResumes}
                  />
                </div>

                <div className="mt-4 pt-3 border-t border-border-default text-[11px] text-text-muted flex items-center justify-between font-mono">
                  <span>Max 5 MB per resume</span>
                  <span>{validResumeIds.length} ready / {selectedResumes.length} total</span>
                </div>
              </div>

            </div>

            <div className="bg-bg-surface border border-border-default rounded-xl p-4 sm:p-6 text-center transition-colors">
              <AnalyzeButton
                isDisabled={isAnalyzeDisabled}
                disabledReason={disabledReason}
                onAnalyze={handleAnalyzeCandidates}
                candidateCount={validResumeIds.length}
              />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
