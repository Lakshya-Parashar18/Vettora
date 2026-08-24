import asyncio
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.mongodb import get_resumes_collection, parse_object_id
from app.schemas.resume import (
    ResumeGetResponse,
    ResumeUploadItem,
    ResumeUploadResponse,
    StructuredResume,
)
from app.services.resume_parser import parse_resume_file

router = APIRouter()


@router.post("/resumes/upload", response_model=ResumeUploadResponse)
async def upload_resumes(files: List[UploadFile] = File(...)):
    if not files:
        exc = HTTPException(status_code=400, detail="No resume files were provided.")
        setattr(exc, "error_code", "no_files_provided")
        raise exc

    collection = get_resumes_collection()
    results = []

    for idx, file in enumerate(files):
        if idx > 0:
            await asyncio.sleep(0.15)
        filename = file.filename or "uploaded_resume"
        content = await file.read()
        item: ResumeUploadItem = parse_resume_file(filename, content)

        if item.status == "processed" and item.resume is not None:
            if collection is not None:
                now = datetime.now(timezone.utc)
                doc = {
                    "filename": filename,
                    "resume": item.resume.model_dump(),
                    "raw_text": item.raw_text,
                    "metadata": item.resume.metadata.model_dump()
                    if item.resume and item.resume.metadata
                    else {
                        "extraction_method": item.extraction_method or "native",
                        "llm_structured": True,
                    },
                    "created_at": now,
                }
                insert_result = collection.insert_one(doc)
                item.resume_id = str(insert_result.inserted_id)

        item.raw_text = None
        item.normalized_text = None
        results.append(item)

    return ResumeUploadResponse(resumes=results)


@router.get("/resumes/{resume_id}", response_model=ResumeGetResponse)
async def get_resume(resume_id: str):
    obj_id = parse_object_id(resume_id)
    collection = get_resumes_collection()

    if collection is None:
        exc = HTTPException(status_code=503, detail="Database service unavailable.")
        setattr(exc, "error_code", "database_unavailable")
        raise exc

    doc = collection.find_one({"_id": obj_id})
    if not doc:
        exc = HTTPException(status_code=404, detail=f"Resume with ID {resume_id} not found.")
        setattr(exc, "error_code", "resume_not_found")
        raise exc

    created_at_str = None
    if doc.get("created_at"):
        created_at_str = (
            doc["created_at"].isoformat()
            if isinstance(doc["created_at"], datetime)
            else str(doc["created_at"])
        )

    return ResumeGetResponse(
        resume_id=str(doc["_id"]),
        filename=doc.get("filename", "resume"),
        status="processed",
        resume=StructuredResume.model_validate(doc["resume"]),
        created_at=created_at_str,
    )

