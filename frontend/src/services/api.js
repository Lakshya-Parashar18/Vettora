const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined ? import.meta.env.VITE_API_URL : (import.meta.env.DEV ? 'http://localhost:8000' : '');

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch {
    return { status: 'error', service: 'vettora-api' };
  }
}

export async function submitJobDescriptionToApi(text) {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'job_submission_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }

  return await response.json();
}

export async function uploadJobDescriptionFileToApi(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/jobs/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'upload_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }

  return await response.json();
}

export async function uploadResumesToApi(files) {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'upload_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }

  return await response.json();
}

export async function screenCandidatesApi(jobId, resumeIds) {
  const response = await fetch(`${API_BASE_URL}/screen`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ job_id: jobId, resume_ids: resumeIds }),
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'screening_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }

  return await response.json();
}

export async function getCandidatesApi(jobId) {
  const response = await fetch(`${API_BASE_URL}/candidates/${jobId}`);
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'get_candidates_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }
  return await response.json();
}

export async function getEvaluationApi(evaluationId) {
  const response = await fetch(`${API_BASE_URL}/evaluations/${evaluationId}`);
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'get_evaluation_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }
  return await response.json();
}

export async function getResumeApi(resumeId) {
  const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}`);
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'get_resume_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }
  return await response.json();
}

export async function getJobApi(jobId) {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { error: 'get_job_failed', message: `Server error HTTP ${response.status}` };
    }
    throw errorData;
  }
  return await response.json();
}


