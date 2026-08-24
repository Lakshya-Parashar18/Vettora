# Vettora

Vettora is an AI-assisted resume screening platform that extracts structured candidate information, analyzes job descriptions, evaluates candidate-job fit, and produces explainable rankings.

The platform combines deterministic Python scoring rules with LLM semantic evaluation to evaluate candidates objectively against role requirements.

---

## Key Features

- **Multi-Format Resume Processing**: Native PDF and plain text extraction (`pdfplumber`) with OCR fallback (`pytesseract`) for scanned image resumes.
- **Structured Resume Extraction**: Extracts candidate contact info, skills, experience timeline, education, projects, and certifications into validated Pydantic schemas.
- **Job Description Structuring**: Structures raw job descriptions, explicitly separating mandatory required skills from preferred skills.
- **Technology Skill Normalization**: Shared normalization dictionary maps technology aliases (e.g. `ReactJS` → `React`, `NodeJS` → `Node.js`) while preserving distinct skills (`Java` vs `JavaScript`).
- **Explainable Scoring Engine**: Weighted mathematical scoring model in Python. The LLM provides semantic fit analysis, but Python remains the sole source of truth for final scores and candidate rankings.
- **MongoDB Persistence**: Stores structured resumes, job descriptions, and candidate evaluation records with indexed database queries.
- **Recruiter Workspace & Dashboard**: Multi-view frontend providing Job Description structuring, batch resume uploads, ranked results dashboard, and candidate evaluation detail reports.
- **Dark & Light Mode**: Built with semantic CSS variables supporting dynamic theme switching and responsive layouts across desktop, tablet, and mobile viewports.

---

## Architecture Overview

```text
Resume Document
      ↓
File Validation & Native Text Extraction / OCR Fallback
      ↓
Text Normalization & Deterministic Email/Phone Extraction
      ↓
LLM Structured Data Extraction (Pydantic Schema)
      ↓
MongoDB Persistence (resumes collection) ─────────────────┐
                                                         │
Job Description Text                                     │
      ↓                                                  │
LLM Job Structuring (Required vs Preferred Skills)        │
      ↓                                                  │
MongoDB Persistence (jobs collection) ───────────────────┼──> Python Matching & Scoring Engine
                                                         │        - Skill Match (40%)
Candidate Resume + Job Description                       │        - Experience Match (25%)
      ↓                                                  │        - Education Match (15%)
LLM Semantic Fit Evaluation (Context & Evidence) ────────┘        - Required Criteria (10%)
      ↓                                                           - Semantic Fit (10%)
MongoDB Persistence (evaluations collection)                          ↓
      ↓                                                  Deterministic Score & Ranking
Ranked Candidate Results Dashboard & Detail View                      ↓
                                                         Recommend: Strong / Good / Partial / Weak
```

---

## Scoring Methodology

Vettora uses a hybrid evaluation model designed for mathematical transparency and explainability.

### Weight Distribution (100% Total)

| Component | Weight | Description |
| --- | --- | --- |
| **Skills Match** | **40%** | Weighted combination of matched required skills (70%) and preferred skills (30%). |
| **Experience Match** | **25%** | Ratio of candidate years of experience against minimum required years (caps at 100%). |
| **Education Match** | **15%** | Degree level hierarchy evaluation (PhD = 4, Master's = 3, Bachelor's = 2, Diploma = 1). |
| **Required Criteria** | **10%** | Percentage of mandatory required skills satisfied. |
| **Semantic Fit** | **10%** | LLM contextual relevance evaluation score (0 to 100). |

### Final Score & Recommendation Thresholds

- **Final Score**: Calculated as `Total Percentage / 10.0` (Scale: `0.0` to `10.0`).
- **Recommendation Categories**:
  - `Strong Match`: Score >= 8.0
  - `Good Match`: 6.5 <= Score < 8.0
  - `Partial Match`: 5.0 <= Score < 6.5
  - `Weak Match`: Score < 5.0

### Matching Methodology

Vettora employs a two-step **decomposition-based conceptual matching engine** for requirement evaluation:

1. **DECOMPOSE**: For each job description requirement, the LLM uses software domain knowledge to decompose umbrella or broad requirements (e.g., *"Computer Science fundamentals"*) into standard core sub-topics (e.g., Data Structures, Algorithms, Operating Systems, Computer Networks, DBMS).
2. **MATCH**: The candidate's resume is searched for direct textual evidence of those decomposed sub-topics (e.g., *"OS, CN, DAA"*) rather than searching for literal requirement phrases.

#### Rationale: Why Conceptual Decomposition over Keyword or Embedding Matching?
- **Overcomes Keyword Brittleness**: Broad requirements are often penalised as "missing" under exact keyword matching simply because candidates list specific underlying subjects or tools instead of umbrella terms.
- **Superior to Dense Vector Embeddings**: Vector embeddings collapse domain nuances into opaque spatial similarity scores, which often hallucinate high similarity for superficially related buzzwords (false positives) while failing to provide explicit evidence tracing.
- **Explainable & Auditable**: Decomposition maps explicit resume text to specific sub-topic evidence (`evidence_found` vs `critical_subtopics_missing`), enabling a transparent graduated match level (`full`, `partial`, `weak`, `missing`) and exact `coverage_ratio` calculation.

*Note: The LLM does NOT directly determine final scores or candidate rankings. All final scores, score breakdowns, recommendation labels, and rank orderings are executed deterministically in Python.*

---

## Technology Stack

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS v4 + Vanilla CSS Custom Properties
- **Scrolling & Icons**: Locomotive Scroll + Lucide React

### Backend
- **Framework**: FastAPI + Python 3.13
- **Validation**: Pydantic v2
- **Database Client**: PyMongo
- **Text & PDF Extraction**: `pdfplumber`, `pytesseract` (Tesseract OCR), `python-multipart`

### Database
- **Database**: MongoDB 6+

---

## Project Structure

```text
Vettora/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CandidateDetailHeader.jsx
│   │   │   ├── CandidateDetailSkeleton.jsx
│   │   │   ├── CandidateDetailView.jsx
│   │   │   ├── CandidateEvaluationSection.jsx
│   │   │   ├── CandidateResultCard.jsx
│   │   │   ├── CandidateResumeTimeline.jsx
│   │   │   ├── CandidateSkeletonCard.jsx
│   │   │   ├── FileList.jsx
│   │   │   ├── JobDescriptionInput.jsx
│   │   │   ├── JobSummaryCard.jsx
│   │   │   ├── ProcessingState.jsx
│   │   │   ├── ResultsControls.jsx
│   │   │   ├── ResultsEmptyState.jsx
│   │   │   ├── ResultsSummary.jsx
│   │   │   ├── ResultsView.jsx
│   │   │   ├── ResumeUploader.jsx
│   │   │   └── WorkflowSteps.jsx
│   │   ├── pages/
│   │   │   └── ScreeningDashboard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── jobs.py
│   │   │       ├── resumes.py
│   │   │       └── screening.py
│   │   ├── db/
│   │   │   └── mongodb.py
│   │   ├── prompts/
│   │   │   ├── job_extraction_prompt.py
│   │   │   ├── resume_extraction_prompt.py
│   │   │   └── semantic_matching_prompt.py
│   │   ├── schemas/
│   │   │   ├── evaluation.py
│   │   │   ├── health.py
│   │   │   ├── job.py
│   │   │   └── resume.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── resume_parser.py
│   │   │   ├── scoring_service.py
│   │   │   └── skill_normalizer.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_jobs.py
│   │   ├── test_llm_service.py
│   │   ├── test_mongodb_workflow.py
│   │   ├── test_resume_parser.py
│   │   └── test_scoring.py
│   ├── .env.example
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## Local Setup

### Prerequisites

- **Node.js**: v18.0 or higher
- **Python**: v3.11 or higher
- **MongoDB**: Local MongoDB instance running on `mongodb://localhost:27017` or a remote MongoDB Atlas URI
- **Tesseract OCR (Optional)**: Required only if running OCR fallback on scanned image PDFs.

---

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `backend/.env` to configure your settings:
   ```env
   APP_ENV=development
   FRONTEND_URL=http://localhost:5173
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=vettora
   LLM_API_KEY=your_gemini_api_key_here
   LLM_MODEL=gemini-2.5-flash
   LLM_PROVIDER=google
   ```

5. Start the backend development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   The backend API will run at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Ensure `frontend/.env` contains:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. Start the frontend development server:
   ```bash
   npm run dev
   ```
   The application UI will run at `http://localhost:5173`.

---

## Environment Variables

### Backend Environment Variables (`backend/.env.example`)

| Variable | Description | Default / Example |
| --- | --- | --- |
| `APP_ENV` | Application execution environment (`development`, `production`). | `development` |
| `FRONTEND_URL` | Allowed CORS origin for frontend client requests. | `http://localhost:5173` |
| `MONGODB_URI` | MongoDB connection URI string. | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Target MongoDB database name. | `vettora` |
| `LLM_API_KEY` | Private API key for Google Gemini / LLM provider. | `your_api_key` |
| `LLM_MODEL` | Target Gemini model identifier. | `gemini-2.5-flash` |
| `LLM_PROVIDER` | Provider type (`google`). | `google` |

*Note: Private API keys and database credentials belong exclusively in `backend/.env` and are never exposed to client browsers.*

### Frontend Environment Variables (`frontend/.env.example`)

| Variable | Description | Default / Example |
| --- | --- | --- |
| `VITE_API_URL` | Backend base HTTP API URL endpoint (browser-visible). | `http://localhost:8000` |

---

## Database & OCR Setup Notes

### MongoDB Persistence
- If `MONGODB_URI` is provided, Vettora connects via PyMongo during application lifespan startup.
- If MongoDB is offline, `/health` reports `database: "disconnected"` and database operations return controlled HTTP 503 errors.
- Indexes are automatically created on startup for `resumes.created_at`, `jobs.created_at`, unique `evaluations.(job_id, resume_id)`, and `evaluations.(job_id, score)`.

### OCR Fallback Behavior
- Text-based PDFs use native extraction via `pdfplumber`.
- If a scanned PDF page contains fewer than 20 characters of text, the system checks for Tesseract OCR.
- If Tesseract is missing on the host OS, the file returns a controlled status badge (`ocr_unavailable` / "Scanned PDF detected, but OCR engine is not installed...") without failing other resumes in the batch.

---

## API Overview

| Endpoint | Method | Description |
| --- | --- | --- |
| `/health` | `GET` | Health check endpoint returning API service and database connectivity status. |
| `/jobs` | `POST` | Structures raw job description text via LLM and stores in MongoDB (`job_id`). |
| `/jobs/{job_id}` | `GET` | Retrieves a structured job description record by ID. |
| `/resumes/upload` | `POST` | Uploads PDF/TXT resumes, parses text, structures data via LLM, and persists (`resume_id`). |
| `/resumes/{resume_id}` | `GET` | Retrieves a structured candidate resume record by ID. |
| `/screen` | `POST` | Runs deterministic matching and LLM semantic fit on candidate resumes against a job. |
| `/candidates/{job_id}` | `GET` | Retrieves ranked candidate evaluations for a specific job session. |
| `/evaluations/{id}` | `GET` | Retrieves detailed candidate evaluation report record by evaluation ID. |

---

## Testing

### Backend Test Suite
Run unit and service tests using `pytest`:
```bash
cd backend
pytest
```
**Status**: 87 passed out of 87 unit tests.

### Frontend Build Check
Run the production build using Vite:
```bash
cd frontend
npm run build
```
**Status**: Production build completes with 0 errors (`dist/assets/index.js` generated cleanly).

---

## Demo Workflow

1. **Open Recruiter Workspace**: Open `http://localhost:5173` in a web browser.
2. **Structure Job Description**: Paste a job description into the input box and click **Save & Structure Job**. The structured job card will display title, required skills, preferred skills, and experience requirements.
3. **Upload Candidate Resumes**: Drag and drop or browse PDF/TXT resumes into the resume uploader card.
4. **Analyze Candidates**: Click **Analyze Candidates**. The visual processing indicator will step through preparing, requirement evaluation, criteria scoring, and candidate ranking.
5. **Review Ranked Dashboard**: Vettora routes to `#results/:jobId`. Inspect summary metric cards, search by name/email, filter by recommendation category, or sort by match score.
6. **Inspect Candidate Evaluation Report**: Click **View Evaluation** on a candidate card. Review score breakdown progress bars, mandatory required vs preferred skill matches, key strengths, concerns, evidence mapping, and structured work experience timeline.
7. **Toggle Theme**: Click the theme switch in the top header to toggle between Dark Mode and Light Mode.

---

## Known Scope & Limitations

- **Numerical Experience Parsing**: Experience calculation relies on explicit numerical indicators in the resume text (e.g. `2021 - 2024` or `July 2022 - Present`). Vague dates (e.g. "recent years") are omitted rather than guessed.
- **Tesseract Host Dependency**: Scanned image PDFs require Tesseract installed on the host OS. Text PDFs do not require Tesseract.
- **Synchronous Screening**: Screening operates synchronously per API request for predictable batch processing without complex background queues.
- **Unit Test Mocking**: Unit tests mock database connections and LLM API responses for offline deterministic test execution.
