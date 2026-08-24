from datetime import datetime, timezone
from typing import List, Union
from fastapi import APIRouter, HTTPException

from app.db.mongodb import (
    get_evaluations_collection,
    get_jobs_collection,
    get_resumes_collection,
    parse_object_id,
)
from app.schemas.evaluation import (
    BatchScreenRequest,
    BatchScreenResponse,
    CandidateResult,
    CandidateSummary,
    CandidatesListResponse,
    ConceptualRequirementMatch,
    EvaluationDetailResponse,
    EvidenceItem,
    MongoScreenRequest,
    MongoScreenResponse,
    ScoreBreakdown,
    ScreenRequest,
    ScreenResponse,
)
from app.schemas.job import JobDescription
from app.schemas.resume import StructuredResume
from app.services.llm_service import evaluate_semantic_fit_with_llm
from app.services.scoring_service import evaluate_batch, evaluate_candidate

router = APIRouter()


@router.post(
    "/screen",
    response_model=Union[MongoScreenResponse, ScreenResponse],
)
async def screen_candidate(payload: Union[MongoScreenRequest, ScreenRequest]):
    if isinstance(payload, ScreenRequest):
        sem_fit = evaluate_semantic_fit_with_llm(payload.resume, payload.job)
        evaluation = evaluate_candidate(payload.resume, payload.job, sem_fit)
        return ScreenResponse(evaluation=evaluation)

    job_obj_id = parse_object_id(payload.job_id)

    if not payload.resume_ids:
        exc = HTTPException(
            status_code=400,
            detail="At least one resume_id must be provided for screening.",
        )
        setattr(exc, "error_code", "empty_resume_ids")
        raise exc

    jobs_col = get_jobs_collection()
    resumes_col = get_resumes_collection()
    evals_col = get_evaluations_collection()

    if jobs_col is None or resumes_col is None or evals_col is None:
        exc = HTTPException(status_code=503, detail="Database service unavailable.")
        setattr(exc, "error_code", "database_unavailable")
        raise exc

    job_doc = jobs_col.find_one({"_id": job_obj_id})
    if not job_doc:
        exc = HTTPException(
            status_code=404,
            detail=f"Job description with ID {payload.job_id} not found.",
        )
        setattr(exc, "error_code", "job_not_found")
        raise exc

    job = JobDescription.model_validate(job_doc["job"])

    unique_resume_ids = []
    seen = set()
    for rid in payload.resume_ids:
        if rid not in seen:
            seen.add(rid)
            unique_resume_ids.append(rid)

    results: List[CandidateResult] = []

    for r_str in unique_resume_ids:
        try:
            r_obj_id = parse_object_id(r_str)
        except HTTPException as e:
            results.append(
                CandidateResult(
                    resume_id=r_str,
                    status="failed",
                    error={"code": getattr(e, "error_code", "invalid_id"), "message": e.detail},
                )
            )
            continue

        resume_doc = resumes_col.find_one({"_id": r_obj_id})
        if not resume_doc:
            results.append(
                CandidateResult(
                    resume_id=r_str,
                    status="failed",
                    error={
                        "code": "resume_not_found",
                        "message": f"Resume with ID {r_str} not found.",
                    },
                )
            )
            continue

        try:
            resume = StructuredResume.model_validate(resume_doc["resume"])
            cand_info = resume.candidate
            cand_summary = CandidateSummary(
                name=cand_info.name if cand_info else None,
                email=cand_info.email if cand_info else None,
            )

            sem_fit = evaluate_semantic_fit_with_llm(resume, job)
            evaluation = evaluate_candidate(resume, job, sem_fit)

            now = datetime.now(timezone.utc)
            existing_eval = evals_col.find_one({"job_id": job_obj_id, "resume_id": r_obj_id})

            eval_dict = {
                "job_id": job_obj_id,
                "resume_id": r_obj_id,
                "candidate": cand_summary.model_dump(),
                "score": evaluation.score,
                "recommendation": evaluation.recommendation,
                "score_breakdown": evaluation.score_breakdown.model_dump(),
                "matched_required_skills": evaluation.matched_required_skills,
                "missing_required_skills": evaluation.missing_required_skills,
                "matched_preferred_skills": evaluation.matched_preferred_skills,
                "missing_preferred_skills": evaluation.missing_preferred_skills,
                "strengths": evaluation.strengths,
                "concerns": evaluation.concerns,
                "justification": evaluation.justification or "",
                "evidence": [e.model_dump() for e in evaluation.evidence],
                "conceptual_matches": [cm.model_dump() for cm in evaluation.conceptual_matches],
                "updated_at": now,
            }

            if existing_eval:
                evals_col.update_one({"_id": existing_eval["_id"]}, {"$set": eval_dict})
                eval_id_str = str(existing_eval["_id"])
            else:
                eval_dict["created_at"] = now
                res = evals_col.insert_one(eval_dict)
                eval_id_str = str(res.inserted_id)

            results.append(
                CandidateResult(
                    resume_id=r_str,
                    evaluation_id=eval_id_str,
                    status="processed",
                    candidate=cand_summary,
                    score=evaluation.score,
                    recommendation=evaluation.recommendation,
                    score_breakdown=evaluation.score_breakdown,
                    matched_required_skills=evaluation.matched_required_skills,
                    missing_required_skills=evaluation.missing_required_skills,
                    matched_preferred_skills=evaluation.matched_preferred_skills,
                    missing_preferred_skills=evaluation.missing_preferred_skills,
                    strengths=evaluation.strengths,
                    concerns=evaluation.concerns,
                    justification=evaluation.justification or "",
                    evidence=evaluation.evidence,
                    conceptual_matches=evaluation.conceptual_matches,
                )
            )
        except Exception as err:
            results.append(
                CandidateResult(
                    resume_id=r_str,
                    status="failed",
                    error={
                        "code": "evaluation_failed",
                        "message": f"Failed to evaluate resume {r_str}: {str(err)}",
                    },
                )
            )

    processed_candidates = [c for c in results if c.status == "processed"]
    failed_candidates = [c for c in results if c.status != "processed"]

    processed_candidates.sort(
        key=lambda c: (
            -(c.score if c.score is not None else -1.0),
            (c.candidate.name.lower() if c.candidate and c.candidate.name else ""),
            c.resume_id,
        )
    )

    ranked = processed_candidates + failed_candidates
    return MongoScreenResponse(job_id=payload.job_id, candidates=ranked)


@router.post("/screen/batch", response_model=BatchScreenResponse)
async def screen_batch_candidates(payload: BatchScreenRequest):
    sem_fits = []
    for resume in payload.resumes:
        sem = evaluate_semantic_fit_with_llm(resume, payload.job)
        sem_fits.append(sem)

    evaluations = evaluate_batch(payload.resumes, payload.job, sem_fits)
    return BatchScreenResponse(evaluations=evaluations)


@router.get("/candidates/{job_id}", response_model=CandidatesListResponse)
async def get_candidates_for_job(job_id: str):
    job_obj_id = parse_object_id(job_id)
    jobs_col = get_jobs_collection()
    evals_col = get_evaluations_collection()

    if jobs_col is None or evals_col is None:
        exc = HTTPException(status_code=503, detail="Database service unavailable.")
        setattr(exc, "error_code", "database_unavailable")
        raise exc

    job_doc = jobs_col.find_one({"_id": job_obj_id})
    if not job_doc:
        exc = HTTPException(
            status_code=404,
            detail=f"Job description with ID {job_id} not found.",
        )
        setattr(exc, "error_code", "job_not_found")
        raise exc

    cursor = evals_col.find({"job_id": job_obj_id})
    candidates: List[CandidateResult] = []

    for doc in cursor:
        cand_dict = doc.get("candidate", {})
        cand_summary = CandidateSummary(
            name=cand_dict.get("name"),
            email=cand_dict.get("email"),
        )
        sb_dict = doc.get("score_breakdown", {})
        score_breakdown = ScoreBreakdown.model_validate(sb_dict) if sb_dict else None
        evidence_list = [EvidenceItem.model_validate(e) for e in doc.get("evidence", [])]
        conceptual_matches_list = [
            ConceptualRequirementMatch.model_validate(cm) for cm in doc.get("conceptual_matches", [])
        ]

        candidates.append(
            CandidateResult(
                resume_id=str(doc["resume_id"]),
                evaluation_id=str(doc["_id"]),
                status="processed",
                candidate=cand_summary,
                score=doc.get("score"),
                recommendation=doc.get("recommendation"),
                score_breakdown=score_breakdown,
                matched_required_skills=doc.get("matched_required_skills", []),
                missing_required_skills=doc.get("missing_required_skills", []),
                matched_preferred_skills=doc.get("matched_preferred_skills", []),
                missing_preferred_skills=doc.get("missing_preferred_skills", []),
                strengths=doc.get("strengths", []),
                concerns=doc.get("concerns", []),
                justification=doc.get("justification", ""),
                evidence=evidence_list,
                conceptual_matches=conceptual_matches_list,
            )
        )

    candidates.sort(
        key=lambda c: (
            -(c.score if c.score is not None else -1.0),
            (c.candidate.name.lower() if c.candidate and c.candidate.name else ""),
            c.resume_id,
        )
    )

    return CandidatesListResponse(job_id=job_id, candidates=candidates)


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationDetailResponse)
async def get_evaluation(evaluation_id: str):
    eval_obj_id = parse_object_id(evaluation_id)
    evals_col = get_evaluations_collection()

    if evals_col is None:
        exc = HTTPException(status_code=503, detail="Database service unavailable.")
        setattr(exc, "error_code", "database_unavailable")
        raise exc

    doc = evals_col.find_one({"_id": eval_obj_id})
    if not doc:
        exc = HTTPException(
            status_code=404,
            detail=f"Evaluation with ID {evaluation_id} not found.",
        )
        setattr(exc, "error_code", "evaluation_not_found")
        raise exc

    cand_dict = doc.get("candidate", {})
    cand_summary = CandidateSummary(
        name=cand_dict.get("name"),
        email=cand_dict.get("email"),
    )
    score_breakdown = ScoreBreakdown.model_validate(doc.get("score_breakdown", {}))
    evidence_list = [EvidenceItem.model_validate(e) for e in doc.get("evidence", [])]
    conceptual_matches_list = [
        ConceptualRequirementMatch.model_validate(cm) for cm in doc.get("conceptual_matches", [])
    ]

    created_at_str = None
    if doc.get("created_at"):
        created_at_str = (
            doc["created_at"].isoformat()
            if isinstance(doc["created_at"], datetime)
            else str(doc["created_at"])
        )

    return EvaluationDetailResponse(
        evaluation_id=str(doc["_id"]),
        job_id=str(doc["job_id"]),
        resume_id=str(doc["resume_id"]),
        candidate=cand_summary,
        score=doc.get("score", 0.0),
        recommendation=doc.get("recommendation", ""),
        score_breakdown=score_breakdown,
        matched_required_skills=doc.get("matched_required_skills", []),
        missing_required_skills=doc.get("missing_required_skills", []),
        matched_preferred_skills=doc.get("matched_preferred_skills", []),
        missing_preferred_skills=doc.get("missing_preferred_skills", []),
        strengths=doc.get("strengths", []),
        concerns=doc.get("concerns", []),
        justification=doc.get("justification", ""),
        evidence=evidence_list,
        conceptual_matches=conceptual_matches_list,
        created_at=created_at_str,
    )

