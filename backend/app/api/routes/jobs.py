from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, File, UploadFile

from app.config import settings
from app.db.mongodb import get_jobs_collection, parse_object_id
from app.schemas.job import (
    JobCreateRequest,
    JobDescription,
    JobError,
    JobGetResponse,
    JobPostResponse,
)
from app.services.llm_service import (
    LLMExtractionError,
    _fallback_deterministic_job_description,
    extract_job_description_with_llm,
)
from app.services.resume_parser import (
    validate_file,
    extract_pdf_pages_with_fallback,
    extract_txt_text,
    extract_docx_text,
    ResumeParsingError,
)

router = APIRouter()


@router.post("/jobs", response_model=JobPostResponse)
async def create_job(request: JobCreateRequest):
    raw_text = request.text
    if not raw_text or not raw_text.strip():
        exc = HTTPException(status_code=400, detail="Job description text cannot be empty.")
        setattr(exc, "error_code", "empty_job_text")
        raise exc

    if len(raw_text.encode("utf-8")) > settings.max_jd_size_bytes:
        exc = HTTPException(
            status_code=400,
            detail=f"Job description exceeds maximum allowed limit of {settings.max_jd_size_bytes} bytes.",
        )
        setattr(exc, "error_code", "oversized_job_text")
        raise exc

    try:
        try:
            job_data = extract_job_description_with_llm(raw_text)
        except LLMExtractionError:
            job_data = _fallback_deterministic_job_description(raw_text)

        collection = get_jobs_collection()
        job_id = None

        if collection is not None:
            now = datetime.now(timezone.utc)
            doc = {
                "raw_text": raw_text,
                "job": job_data.model_dump(),
                "created_at": now,
            }
            insert_result = collection.insert_one(doc)
            job_id = str(insert_result.inserted_id)

        return JobPostResponse(job_id=job_id, status="processed", job=job_data)
    except Exception:
        return JobPostResponse(
            status="failed",
            error=JobError(
                code="extraction_failed",
                message="An unexpected error occurred while processing the Job Description.",
            ),
        )


@router.post("/jobs/upload", response_model=JobPostResponse)
async def upload_job_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        exc = HTTPException(status_code=400, detail="No file was uploaded.")
        setattr(exc, "error_code", "missing_file")
        raise exc

    try:
        content = await file.read()
        ext = validate_file(file.filename, content)

        if ext == ".pdf":
            raw_text, _ = extract_pdf_pages_with_fallback(content)
        elif ext in {".doc", ".docx"}:
            raw_text = extract_docx_text(content)
        else:
            raw_text = extract_txt_text(content)

        if not raw_text or not raw_text.strip():
            raise ResumeParsingError(
                code="empty_job_file",
                message="Could not extract readable text from the uploaded file.",
            )

        if len(raw_text.encode("utf-8")) > settings.max_jd_size_bytes:
            raise ResumeParsingError(
                code="oversized_job_text",
                message=f"Extracted job text exceeds limit of {settings.max_jd_size_bytes} bytes.",
            )

        try:
            job_data = extract_job_description_with_llm(raw_text)
        except LLMExtractionError:
            job_data = _fallback_deterministic_job_description(raw_text)
        collection = get_jobs_collection()
        job_id = None

        if collection is not None:
            now = datetime.now(timezone.utc)
            doc = {
                "raw_text": raw_text,
                "filename": file.filename,
                "job": job_data.model_dump(),
                "created_at": now,
            }
            insert_result = collection.insert_one(doc)
            job_id = str(insert_result.inserted_id)

        return JobPostResponse(job_id=job_id, status="processed", job=job_data)

    except ResumeParsingError as e:
        return JobPostResponse(
            status="failed",
            error=JobError(code=e.code, message=e.message),
        )
    except LLMExtractionError as e:
        return JobPostResponse(
            status="failed",
            error=JobError(code=e.code, message=e.message),
        )
    except Exception:
        return JobPostResponse(
            status="failed",
            error=JobError(
                code="extraction_failed",
                message="An unexpected error occurred while processing the Job Description file.",
            ),
        )



@router.get("/jobs/{job_id}", response_model=JobGetResponse)
async def get_job(job_id: str):
    obj_id = parse_object_id(job_id)
    collection = get_jobs_collection()

    if collection is None:
        exc = HTTPException(status_code=503, detail="Database service unavailable.")
        setattr(exc, "error_code", "database_unavailable")
        raise exc

    doc = collection.find_one({"_id": obj_id})
    if not doc:
        exc = HTTPException(status_code=404, detail=f"Job with ID {job_id} not found.")
        setattr(exc, "error_code", "job_not_found")
        raise exc

    created_at_str = None
    if doc.get("created_at"):
        created_at_str = (
            doc["created_at"].isoformat()
            if isinstance(doc["created_at"], datetime)
            else str(doc["created_at"])
        )

    return JobGetResponse(
        job_id=str(doc["_id"]),
        status="processed",
        job=JobDescription.model_validate(doc["job"]),
        created_at=created_at_str,
    )

