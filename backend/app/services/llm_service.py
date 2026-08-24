import json
import re
from typing import Optional

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.config import settings
from app.prompts.job_extraction_prompt import (
    SYSTEM_PROMPT as JOB_SYSTEM_PROMPT,
    build_job_extraction_prompt,
)
from app.prompts.resume_extraction_prompt import (
    SYSTEM_PROMPT as RESUME_SYSTEM_PROMPT,
    build_extraction_prompt,
)
from app.prompts.semantic_matching_prompt import (
    SYSTEM_PROMPT as SEMANTIC_SYSTEM_PROMPT,
    build_semantic_matching_prompt,
)
from app.schemas.evaluation import ConceptualRequirementMatch, EvidenceItem, SemanticEvaluation
from app.schemas.job import (
    EducationRequirement,
    ExperienceRequirement,
    JobDescription,
)
from app.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeCandidate,
    ResumeMetadata,
    StructuredResume,
)
from app.services.skill_normalizer import normalize_skills
from app.services.ontology_service import SkillOntology


class LLMExtractionError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def _get_client() -> genai.Client:
    if not settings.llm_api_key:
        raise LLMExtractionError(
            code="llm_not_configured",
            message="LLM API key is not configured.",
        )
    return genai.Client(api_key=settings.llm_api_key)


def _call_llm(client: genai.Client, user_prompt: str, system_instruction: str, model: Optional[str] = None) -> str:
    model_name = model or settings.llm_model
    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    return response.text or ""


def _parse_and_validate(raw_json: str) -> dict:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        stripped = raw_json.strip()
        if stripped.startswith("```"):
            stripped = stripped.split("\n", 1)[-1].rsplit("```", 1)[0]
        data = json.loads(stripped)
    return data


def _build_structured_resume(
    data: dict,
    extraction_method: str,
    det_email: Optional[str],
    det_phone: Optional[str],
) -> StructuredResume:
    llm_candidate = data.get("candidate") or {}

    final_email = det_email or llm_candidate.get("email")
    final_phone = det_phone or llm_candidate.get("phone")
    final_name = llm_candidate.get("name")

    candidate = ResumeCandidate(
        name=final_name if final_name else None,
        email=final_email,
        phone=final_phone,
    )

    raw_skills = [str(s) for s in data.get("skills", []) if s]
    skills = normalize_skills(raw_skills)

    education = [
        EducationEntry(**{k: v for k, v in e.items() if k in EducationEntry.model_fields})
        for e in data.get("education", [])
        if isinstance(e, dict)
    ]

    experience = [
        ExperienceEntry(**{k: v for k, v in e.items() if k in ExperienceEntry.model_fields})
        for e in data.get("experience", [])
        if isinstance(e, dict)
    ]

    projects = []
    for p in data.get("projects", []):
        if isinstance(p, dict):
            raw_techs = [str(t) for t in p.get("technologies", []) if t]
            projects.append(
                ProjectEntry(
                    name=p.get("name"),
                    description=p.get("description"),
                    technologies=normalize_skills(raw_techs),
                )
            )

    certifications = [str(c) for c in data.get("certifications", []) if c]

    return StructuredResume(
        candidate=candidate,
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        metadata=ResumeMetadata(extraction_method=extraction_method, llm_structured=True),
    )


def _fallback_deterministic_resume(
    normalized_text: str,
    extraction_method: str,
    det_email: Optional[str] = None,
    det_phone: Optional[str] = None,
) -> StructuredResume:
    lines = [line.strip() for line in normalized_text.split("\n") if line.strip()]
    first_line = lines[0] if lines else "Candidate"

    cand_name = None
    if len(first_line) < 40 and not any(k in first_line.lower() for k in ["resume", "curriculum", "summary", "email", "phone"]):
        cand_name = first_line

    skills = normalize_skills(normalized_text.split())

    candidate = ResumeCandidate(
        name=cand_name,
        email=det_email,
        phone=det_phone,
    )

    return StructuredResume(
        candidate=candidate,
        skills=skills,
        education=[],
        experience=[],
        projects=[],
        certifications=[],
        metadata=ResumeMetadata(extraction_method=extraction_method, llm_structured=False),
    )


def extract_structured_resume_with_llm(
    normalized_text: str,
    extraction_method: str,
    det_email: Optional[str] = None,
    det_phone: Optional[str] = None,
) -> StructuredResume:
    client = _get_client()
    user_prompt = build_extraction_prompt(normalized_text, det_email, det_phone)

    try:
        raw = _call_llm(client, user_prompt, RESUME_SYSTEM_PROMPT)
        data = _parse_and_validate(raw)
    except (json.JSONDecodeError, Exception):
        try:
            retry_prompt = user_prompt + "\n\nRespond with ONLY valid JSON matching the schema. No markdown."
            raw = _call_llm(client, retry_prompt, RESUME_SYSTEM_PROMPT)
            data = _parse_and_validate(raw)
        except Exception:
            raise LLMExtractionError(
                code="llm_extraction_failed",
                message="Could not extract structured data from this resume after retry.",
            )

    try:
        return _build_structured_resume(data, extraction_method, det_email, det_phone)
    except (ValidationError, Exception):
        raise LLMExtractionError(
            code="llm_extraction_failed",
            message="Resume structured data failed validation.",
        )


def _build_job_description(data: dict) -> JobDescription:
    raw_req_skills = [str(s) for s in data.get("required_skills", []) if s]
    raw_pref_skills = [str(s) for s in data.get("preferred_skills", []) if s]

    exp_data = data.get("experience") or {}
    min_yrs = exp_data.get("minimum_years")
    max_yrs = exp_data.get("maximum_years")
    exp_req = ExperienceRequirement(
        minimum_years=float(min_yrs) if min_yrs is not None else None,
        maximum_years=float(max_yrs) if max_yrs is not None else None,
    )

    edu_data = data.get("education") or {}
    edu_req = EducationRequirement(
        required=bool(edu_data.get("required", False)),
        degrees=[str(d) for d in edu_data.get("degrees", []) if d],
        fields=[str(f) for f in edu_data.get("fields", []) if f],
    )

    responsibilities = [str(r) for r in data.get("responsibilities", []) if r]
    pref_quals = [str(pq) for pq in data.get("preferred_qualifications", []) if pq]

    return JobDescription(
        title=data.get("title"),
        required_skills=normalize_skills(raw_req_skills),
        preferred_skills=normalize_skills(raw_pref_skills),
        experience=exp_req,
        education=edu_req,
        responsibilities=responsibilities,
        preferred_qualifications=pref_quals,
        location=data.get("location"),
        employment_type=data.get("employment_type"),
    )


def _fallback_deterministic_job_description(jd_text: str) -> JobDescription:
    lines = [line.strip() for line in jd_text.split("\n") if line.strip()]
    first_line = lines[0] if lines else "Software Engineer"

    title = (
        first_line
        if len(first_line) < 60
        and not any(k in first_line.lower() for k in ["overview", "responsibilities", "qualifications"])
        else "Software Engineer"
    )

    ontology = SkillOntology()
    found_skills = []
    seen = set()

    for word in re.findall(r"\b[A-Za-z0-9.#+-]+\b", jd_text):
        cid = ontology.resolve_concept_id(word)
        if cid:
            concept = ontology.get_concept(cid)
            name = concept["name"] if concept else word
            if name.lower() not in seen:
                seen.add(name.lower())
                found_skills.append(name)

    common_techs = [
        "React", "Python", "TypeScript", "JavaScript", "FastAPI", "MongoDB",
        "PostgreSQL", "Docker", "Kubernetes", "AWS", "Terraform", "Helm",
        "Redis", "Node.js", "REST APIs", "Django", "Flask", "Next.js",
        "Tailwind CSS", "Linux", "Git", "CI/CD", "PyTorch", "LLMs", "RAG",
        "Pandas", "SQL", "Microservices"
    ]

    for tech in common_techs:
        if re.search(r"\b" + re.escape(tech) + r"\b", jd_text, re.IGNORECASE):
            if tech.lower() not in seen:
                seen.add(tech.lower())
                found_skills.append(tech)

    min_years = None
    exp_match = re.search(r"(\d+)\+?\s*(?:-\s*(\d+))?\s*(?:years?|yrs?)", jd_text, re.IGNORECASE)
    if exp_match:
        try:
            min_years = float(exp_match.group(1))
        except ValueError:
            pass

    exp_req = ExperienceRequirement(minimum_years=min_years, maximum_years=None)
    edu_req = EducationRequirement(required=False, degrees=[], fields=[])

    return JobDescription(
        title=title,
        required_skills=normalize_skills(found_skills),
        preferred_skills=[],
        experience=exp_req,
        education=edu_req,
        responsibilities=[line for line in lines if line.startswith("-") or line.startswith("•")],
        preferred_qualifications=[],
        location=None,
        employment_type=None,
    )


def extract_job_description_with_llm(jd_text: str) -> JobDescription:
    client = _get_client()
    user_prompt = build_job_extraction_prompt(jd_text)

    try:
        raw = _call_llm(client, user_prompt, JOB_SYSTEM_PROMPT)
        data = _parse_and_validate(raw)
    except (json.JSONDecodeError, Exception):
        try:
            retry_prompt = user_prompt + "\n\nRespond with ONLY valid JSON matching the schema. No markdown."
            raw = _call_llm(client, retry_prompt, JOB_SYSTEM_PROMPT)
            data = _parse_and_validate(raw)
        except Exception:
            raise LLMExtractionError(
                code="llm_extraction_failed",
                message="Could not extract structured data from this Job Description after retry.",
            )

    try:
        return _build_job_description(data)
    except (ValidationError, Exception):
        raise LLMExtractionError(
            code="llm_extraction_failed",
            message="Job description structured data failed validation.",
        )


def _build_semantic_evaluation(data: dict) -> SemanticEvaluation:
    raw_score = data.get("semantic_score", 80.0)
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        score = 80.0
    bounded_score = max(0.0, min(100.0, score))

    matched_reqs = [str(m) for m in data.get("matched_requirements", []) if m]
    strengths = [str(s) for s in data.get("semantic_strengths", []) if s]
    concerns = [str(c) for c in data.get("semantic_concerns", []) if c]

    evidence_items = []
    for item in data.get("evidence", []):
        if isinstance(item, dict) and item.get("requirement") and item.get("evidence"):
            evidence_items.append(
                EvidenceItem(
                    requirement=str(item["requirement"]),
                    evidence=str(item["evidence"]),
                )
            )

    conceptual_matches = []
    for cm in data.get("conceptual_matches", []):
        if isinstance(cm, dict) and cm.get("requirement"):
            raw_cov = cm.get("coverage_ratio", 0.0)
            try:
                cov = float(raw_cov)
            except (TypeError, ValueError):
                cov = 0.0
            cov_bounded = max(0.0, min(1.0, cov))
            match_lvl = str(cm.get("match_level", "missing")).lower()
            if match_lvl not in {"full", "partial", "weak", "missing"}:
                match_lvl = "partial" if cov_bounded >= 0.5 else "missing"

            conceptual_matches.append(
                ConceptualRequirementMatch(
                    requirement=str(cm["requirement"]),
                    requirement_type=str(cm.get("requirement_type", "required")),
                    conceptual_scope=[str(s) for s in cm.get("conceptual_scope", []) if s],
                    evidence_found=[str(e) for e in cm.get("evidence_found", []) if e],
                    critical_subtopics_missing=[str(m) for m in cm.get("critical_subtopics_missing", []) if m],
                    coverage_ratio=cov_bounded,
                    match_level=match_lvl,
                    reasoning=str(cm.get("reasoning", "")),
                )
            )

    justification = str(data["justification"]) if data.get("justification") else None

    return SemanticEvaluation(
        semantic_score=bounded_score,
        matched_requirements=matched_reqs,
        semantic_strengths=strengths,
        semantic_concerns=concerns,
        evidence=evidence_items,
        justification=justification,
        conceptual_matches=conceptual_matches,
    )


def evaluate_semantic_fit_with_llm(
    resume: StructuredResume,
    job: JobDescription,
) -> SemanticEvaluation:
    try:
        client = _get_client()
    except LLMExtractionError:
        # Fallback neutral evaluation if LLM is not configured
        return SemanticEvaluation(
            semantic_score=80.0,
            justification="Neutral semantic score applied (LLM API key not configured).",
        )

    resume_json_str = resume.model_dump_json(indent=2)
    job_json_str = job.model_dump_json(indent=2)
    user_prompt = build_semantic_matching_prompt(resume_json_str, job_json_str)

    model_to_use = getattr(settings, "llm_matching_model", "gemini-2.5-pro")

    try:
        raw = _call_llm(client, user_prompt, SEMANTIC_SYSTEM_PROMPT, model=model_to_use)
        data = _parse_and_validate(raw)
    except (json.JSONDecodeError, Exception):
        try:
            retry_prompt = user_prompt + "\n\nRespond with ONLY valid JSON matching the schema. No markdown."
            raw = _call_llm(client, retry_prompt, SEMANTIC_SYSTEM_PROMPT, model=model_to_use)
            data = _parse_and_validate(raw)
        except Exception:
            return SemanticEvaluation(
                semantic_score=70.0,
                justification="Default semantic evaluation applied after retry timeout.",
            )

    try:
        return _build_semantic_evaluation(data)
    except (ValidationError, Exception):
        return SemanticEvaluation(
            semantic_score=70.0,
            justification="Default semantic evaluation applied after validation failure.",
        )
