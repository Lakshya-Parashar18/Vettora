# Vettora Backend API

FastAPI backend for candidate resume screening, deterministic parsing, and OCR processing.

## Prerequisites
- Python 3.10+
- (Optional for scanned PDF OCR) **Tesseract OCR Engine**

### Optional Local OCR Setup (Tesseract)
- **Windows**: Download installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add `C:\Program Files\Tesseract-OCR` to System PATH.
- **macOS**: `brew install tesseract`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install tesseract-ocr`

> **Note**: Native PDF text extraction (`pdfplumber`) runs by default without Tesseract. OCR fallback is invoked automatically only for scanned/image-based PDF pages. If Tesseract is not installed on the server, scanned PDFs return a graceful `ocr_unavailable` error response without crashing the application.

## Setup & Local Development

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate virtual environment:
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Environment configuration:
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

5. Run the FastAPI development server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Available Endpoints & Documentation
- **Health Check**: `GET http://localhost:8000/health`
- **Resume Upload & Parsing**: `POST http://localhost:8000/resumes/upload`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## Running Backend Tests
```bash
pytest
```

## Matching Methodology

Vettora uses a **Decomposition-Based Conceptual Matching** pipeline to align candidate resumes against job description requirements.

### Why Conceptual Decomposition?
Traditional resume matchers suffer from high false-negative rates due to:
- **Keyword Matching:** Fails to align equivalent domain concepts under different terminology (e.g. marking a candidate who lists "OS, CN, DAA" as missing "Computer Science fundamentals").
- **Vector Embeddings (Semantic Search):** Often dilutes specific skill granularities, suffers from retrieval noise, and cannot explain exactly *why* a match is partial or weak.

### How it Works:
1. **Decompose:** The reasoning engine decomposes broad or umbrella job requirements into a taxonomy of industry-standard sub-topics (e.g., decomposing "Database Design" into Relational Databases, Schema Normalization, Query Indexing, and Transaction Isolation).
2. **Match:** The engine inspects the structured resume for direct textual evidence of any of the decomposed sub-topics.
3. **Score:** Calculates a graduated `coverage_ratio` (0.0 to 1.0) and translates it to a `match_level` (`full`, `partial`, `weak`, or `missing`).
4. **Deterministic Weighting:** The mathematical scoring logic applies `coverage_ratio × requirement_weight` per requirement, with a non-linear penalty for low coverage on required criteria (`coverage_ratio ** 1.5`).
