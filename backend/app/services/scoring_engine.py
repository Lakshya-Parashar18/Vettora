from typing import Dict, List, Tuple
from pydantic import BaseModel

from app.schemas.job import JobDescription
from app.schemas.requirement import StructuredRequirement
from app.schemas.resume import StructuredResume
from app.services.evidence_miner import mine_structured_evidence
from app.services.requirement_decomposer import decompose_job_description
from app.services.skill_intelligence import (
    EvidenceProvenance,
    IntelligenceMatchResult,
    evaluate_skill_intelligence,
)


class SubScores(BaseModel):
    technical_fit: float = 0.0
    cs_fundamentals: float = 0.0
    problem_solving: float = 0.0
    experience_alignment: float = 0.0
    education_fit: float = 0.0
    soft_skills_evidence: float = 0.0
    technology_fit: float = 0.0
    role_alignment: float = 0.0
    adaptability: float = 0.0


class RequirementAssessment(BaseModel):
    requirement: str
    category: str
    importance: str  # critical | core | supporting | nice_to_have | contextual
    score: float  # 0 to 100
    coverage_ratio: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    evidenced_subtopics: List[str] = []
    missing_subtopics: List[str] = []
    evidence_summary: List[str] = []
    assessment_text: str = ""
    is_soft_skill_gap: bool = False


class DeterministicEvaluationResult(BaseModel):
    overall_score: float  # 0.0 to 100.0 (or 0.0 to 10.0)
    score_10: float  # 0.0 to 10.0 scale
    score_confidence: float  # 0.0 to 100.0%
    match_tier: str  # Excellent Match | Strong Match | Moderate Match | Weak Match | Insufficient Evidence
    sub_scores: SubScores
    assessments: List[RequirementAssessment] = []
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []


IMPORTANCE_WEIGHTS = {
    "critical": 3.0,
    "core": 2.0,
    "supporting": 1.5,
    "nice_to_have": 1.0,
    "contextual": 0.5,
}


def deduplicate_provenance(chain: List[EvidenceProvenance]) -> List[EvidenceProvenance]:
    """
    Deduplicates evidence to prevent artificial 5x score inflation for repeated mentions of the same skill.
    """
    unique_map: Dict[Tuple[str, str], EvidenceProvenance] = {}
    for item in chain:
        key = (item.evidence_skill.lower(), item.evidence_source.lower())
        if key not in unique_map or item.evidence_strength > unique_map[key].evidence_strength:
            unique_map[key] = item
    return list(unique_map.values())


def evaluate_requirement_assessment(
    req: StructuredRequirement,
    intel: IntelligenceMatchResult,
) -> RequirementAssessment:
    """
    Calculates deterministic requirement score (0-100) and constructs explanation assessment.
    """
    dedup_chain = deduplicate_provenance(intel.provenance_chain)

    # 1. Coverage (0.0 to 1.0)
    coverage = intel.subtopic_coverage_ratio if req.concepts else (1.0 if intel.match_level in {"FULL_MATCH", "STRONG_MATCH"} else 0.35 if intel.match_level == "RELATED" else 0.0)

    # 2. Average Evidence Strength (0.0 to 1.0)
    avg_strength = (
        sum(p.evidence_strength for p in dedup_chain) / len(dedup_chain)
        if dedup_chain
        else 0.5
    )

    # 3. Confidence (0.0 to 1.0)
    confidence = 0.95 if intel.match_level == "FULL_MATCH" else 0.85 if intel.match_level in {"STRONG_MATCH", "RELATED"} else 0.70 if intel.match_level == "PARTIAL_MATCH" else 0.50

    # 4. Requirement Score Calculation (0-100)
    base_score = coverage * avg_strength * confidence * 100.0
    final_req_score = round(min(100.0, base_score), 1)

    # Evidence Summary Lines
    evidence_lines = [f"{p.evidence_skill} ({p.evidence_source})" for p in dedup_chain]

    # Soft Skill Safeguard Check
    is_soft_skill = req.category == "soft_skill" or any(kw in req.requirement.lower() for kw in ["communication", "interpersonal", "customer", "outgoing", "leadership"])
    is_soft_skill_gap = is_soft_skill and coverage == 0.0

    if is_soft_skill_gap:
        assessment = f"No direct resume evidence for '{req.requirement}'. This should be validated during interview rather than treated as proof of absence."
    elif final_req_score >= 80:
        assessment = f"Strong evidence found for '{req.requirement}' via {', '.join(evidence_lines[:3])}."
    elif final_req_score >= 40:
        assessment = f"Partial coverage for '{req.requirement}'. Subtopics evidenced: {', '.join(intel.evidenced_subtopics)}."
    elif intel.match_level == "RELATED":
        assessment = f"Related technology found: {intel.explanation}"
    else:
        assessment = f"No direct resume evidence for requirement '{req.requirement}'."

    return RequirementAssessment(
        requirement=req.requirement,
        category=req.category,
        importance=req.importance,
        score=final_req_score,
        coverage_ratio=coverage,
        confidence=confidence,
        evidenced_subtopics=intel.evidenced_subtopics,
        missing_subtopics=intel.missing_subtopics,
        evidence_summary=evidence_lines,
        assessment_text=assessment,
        is_soft_skill_gap=is_soft_skill_gap,
    )


def calculate_subscores(
    resume: StructuredResume,
    assessments: List[RequirementAssessment],
) -> SubScores:
    """
    Calculates 9 deterministic sub-scores (0-100 scale).
    """
    cat_scores: Dict[str, List[float]] = {}
    for a in assessments:
        cat_scores.setdefault(a.category, []).append(a.score)

    def avg_cat(cat_name: str, fallback: float = 75.0) -> float:
        scores = cat_scores.get(cat_name, [])
        return round(sum(scores) / len(scores), 1) if scores else fallback

    # Education fit calculation
    has_degree = len(resume.education) > 0
    edu_score = 90.0 if has_degree else 60.0

    # Experience alignment calculation
    exp_years = len(resume.experience) * 1.5
    exp_score = min(100.0, round(60.0 + exp_years * 10.0, 1))

    # Soft skills score (safeguarded against false zero penalties)
    soft_assessments = [a for a in assessments if a.category == "soft_skill"]
    if soft_assessments:
        soft_scores = [a.score for a in soft_assessments if not a.is_soft_skill_gap]
        soft_score = round(sum(soft_scores) / len(soft_scores), 1) if soft_scores else 70.0
    else:
        soft_score = 75.0

    return SubScores(
        technical_fit=avg_cat("technical", 80.0),
        cs_fundamentals=avg_cat("cs_fundamentals", 85.0),
        problem_solving=avg_cat("soft_skill", 75.0),
        experience_alignment=exp_score,
        education_fit=edu_score,
        soft_skills_evidence=soft_score,
        technology_fit=avg_cat("technical", 80.0),
        role_alignment=round((exp_score + avg_cat("technical", 80.0)) / 2.0, 1),
        adaptability=avg_cat("domain", 80.0),
    )


def determine_match_tier(overall_score_100: float, confidence: float) -> str:
    """
    Classifies candidate into match tiers:
    - Excellent Match (>= 85)
    - Strong Match (75-84)
    - Moderate Match (60-74)
    - Weak Match (45-59)
    - Insufficient Evidence (< 45 or low confidence)
    """
    if confidence < 35.0:
        return "Insufficient Evidence"
    elif overall_score_100 >= 85.0:
        return "Excellent Match"
    elif overall_score_100 >= 75.0:
        return "Strong Match"
    elif overall_score_100 >= 60.0:
        return "Moderate Match"
    elif overall_score_100 >= 45.0:
        return "Weak Match"
    return "Insufficient Evidence"


def evaluate_candidate_deterministically(
    resume: StructuredResume,
    job: JobDescription,
) -> DeterministicEvaluationResult:
    """
    100% Deterministic Evidence-Based Scoring Engine.
    Processes JD & resume, computes importance-weighted requirement scores, overall match,
    confidence %, sub-scores, and assessments.
    """
    evidences = mine_structured_evidence(resume)
    structured_reqs = decompose_job_description(job)

    assessments: List[RequirementAssessment] = []
    matched_req: List[str] = []
    missing_req: List[str] = []
    matched_pref: List[str] = []
    missing_pref: List[str] = []

    weighted_score_sum = 0.0
    total_weight = 0.0
    confidence_sum = 0.0

    for req in structured_reqs:
        intel = evaluate_skill_intelligence(req, evidences)
        asm = evaluate_requirement_assessment(req, intel)
        assessments.append(asm)

        weight = IMPORTANCE_WEIGHTS.get(req.importance, 1.0)

        # Apply mandatory critical requirement missing penalty (if not a soft skill gap)
        score_val = asm.score
        if req.importance == "critical" and asm.coverage_ratio == 0.0 and not asm.is_soft_skill_gap:
            score_val = 0.0  # Controlled missing penalty for mandatory technical skills

        weighted_score_sum += score_val * weight
        total_weight += weight
        confidence_sum += asm.confidence

        if req.importance in {"critical", "core"}:
            if asm.coverage_ratio >= 0.4:
                matched_req.append(req.requirement)
            else:
                missing_req.append(req.requirement)
        else:
            if asm.coverage_ratio >= 0.4:
                matched_pref.append(req.requirement)
            else:
                missing_pref.append(req.requirement)

    overall_score_100 = round(weighted_score_sum / total_weight, 1) if total_weight > 0 else 100.0
    score_10 = round(overall_score_100 / 10.0, 1)

    avg_confidence = round((confidence_sum / len(structured_reqs)) * 100.0, 1) if structured_reqs else 85.0
    match_tier = determine_match_tier(overall_score_100, avg_confidence)
    sub_scores = calculate_subscores(resume, assessments)

    return DeterministicEvaluationResult(
        overall_score=overall_score_100,
        score_10=score_10,
        score_confidence=avg_confidence,
        match_tier=match_tier,
        sub_scores=sub_scores,
        assessments=assessments,
        matched_required_skills=matched_req,
        missing_required_skills=missing_req,
        matched_preferred_skills=matched_pref,
        missing_preferred_skills=missing_pref,
    )
