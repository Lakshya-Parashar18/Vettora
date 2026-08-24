import re
from datetime import datetime
from typing import List, Optional, Tuple

from app.schemas.evaluation import (
    CandidateEvaluation,
    ConceptualRequirementMatch,
    EvidenceItem,
    ScoreBreakdown,
    SubScoresModel,
    SemanticEvaluation,
)
from app.schemas.job import EducationRequirement, JobDescription
from app.schemas.resume import EducationEntry, ExperienceEntry, StructuredResume
from app.services.evidence_miner import mine_structured_evidence
from app.services.matching_engine import (
    decompose_job_requirement,
    extract_evidence_from_resume,
    match_requirement_against_evidence,
    MatchType,
)
from app.services.scoring_engine import evaluate_candidate_deterministically
from app.services.skill_normalizer import normalize_skills


DEGREE_LEVELS = {
    "phd": 4,
    "doctorate": 4,
    "master": 3,
    "m.tech": 3,
    "m.e.": 3,
    "m.s.": 3,
    "mca": 3,
    "mba": 3,
    "bachelor": 2,
    "b.tech": 2,
    "b.e.": 2,
    "b.s.": 2,
    "b.a.": 2,
    "bca": 2,
    "diploma": 1,
}


def _parse_date_string(date_str: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    if not date_str or not date_str.strip():
        return None, None

    cleaned = date_str.strip().lower()
    if cleaned in {"present", "current", "now", "ongoing"}:
        now = datetime.now()
        return now.year, now.month

    # Search for YYYY-MM or YYYY/MM
    match_ym = re.search(r"(\d{4})[-/](\d{1,2})", cleaned)
    if match_ym:
        year = int(match_ym.group(1))
        month = max(1, min(12, int(match_ym.group(2))))
        return year, month

    # Search for Month YYYY (e.g. July 2022)
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    for idx, m in enumerate(months, 1):
        if m in cleaned:
            match_y = re.search(r"\b(19\d\d|20\d\d)\b", cleaned)
            if match_y:
                return int(match_y.group(1)), idx

    # Search for standalone 4-digit year
    match_y = re.search(r"\b(19\d\d|20\d\d)\b", cleaned)
    if match_y:
        return int(match_y.group(1)), 1

    return None, None


def calculate_experience_years(experience_list: List[ExperienceEntry]) -> float:
    intervals = []

    for exp in experience_list:
        start_y, start_m = _parse_date_string(exp.start_date)
        end_y, end_m = _parse_date_string(exp.end_date)

        if not start_y:
            continue
        if not end_y:
            end_y, end_m = datetime.now().year, datetime.now().month

        start_total = start_y * 12 + (start_m or 1)
        end_total = end_y * 12 + (end_m or 12)

        if end_total >= start_total:
            intervals.append((start_total, end_total))

    if not intervals:
        return 0.0

    # Merge overlapping date intervals to avoid double counting
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev_start, prev_end = merged[-1]
        if current[0] <= prev_end:
            merged[-1] = (prev_start, max(prev_end, current[1]))
        else:
            merged.append(current)

    total_months = sum(end - start + 1 for start, end in merged)
    return round(total_months / 12.0, 1)


def calculate_skill_score(
    resume_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
) -> Tuple[float, float, List[str], List[str], List[str], List[str]]:
    """Legacy skill score calculator provided for backward compatibility."""
    c_skills = set(normalize_skills(resume_skills))
    r_skills = normalize_skills(required_skills)
    p_skills = normalize_skills(preferred_skills)

    matched_req = [s for s in r_skills if s in c_skills]
    missing_req = [s for s in r_skills if s not in c_skills]

    matched_pref = [s for s in p_skills if s in c_skills]
    missing_pref = [s for s in p_skills if s not in c_skills]

    req_score = (len(matched_req) / len(r_skills) * 100.0) if r_skills else 100.0
    pref_score = (len(matched_pref) / len(p_skills) * 100.0) if p_skills else 100.0

    if r_skills and p_skills:
        skills_score = req_score * 0.70 + pref_score * 0.30
    elif r_skills:
        skills_score = req_score
    elif p_skills:
        skills_score = pref_score
    else:
        skills_score = 100.0

    return (
        round(skills_score, 1),
        round(req_score, 1),
        matched_req,
        missing_req,
        matched_pref,
        missing_pref,
    )


def calculate_conceptual_skill_score(
    resume: StructuredResume,
    job: JobDescription,
) -> Tuple[float, float, List[str], List[str], List[str], List[str], List[ConceptualRequirementMatch]]:
    """
    Enhanced conceptual skill score calculator using multi-tier matching engine.
    Inspects coursework, projects, experience, skills, and certifications across all sections.
    """
    evidences = mine_structured_evidence(resume)
    if not evidences:
        evidences = extract_evidence_from_resume(resume)

    conceptual_matches: List[ConceptualRequirementMatch] = []
    matched_req: List[str] = []
    missing_req: List[str] = []

    matched_pref: List[str] = []
    missing_pref: List[str] = []

    req_weighted_sum = 0.0
    req_total_weight = 0.0

    for req_text in (job.required_skills or []):
        req_model = decompose_job_requirement(req_text, is_required=True)
        res = match_requirement_against_evidence(req_model, evidences)

        ev_found_labels = [ev.skill for ev in res.matched_evidences]
        cov = res.match_score
        match_lvl = "full" if cov >= 0.8 else "partial" if cov >= 0.4 else "weak" if cov > 0.0 else "missing"

        if res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT:
            match_lvl = "weak"

        conceptual_matches.append(
            ConceptualRequirementMatch(
                requirement=req_text,
                requirement_type="required",
                conceptual_scope=req_model.concepts,
                evidence_found=res.evidenced_concepts if res.evidenced_concepts else ev_found_labels,
                critical_subtopics_missing=res.missing_concepts,
                coverage_ratio=cov,
                match_level=match_lvl,
                reasoning=res.explanation,
            )
        )

        w = req_model.weight
        req_weighted_sum += cov * w
        req_total_weight += w

        if cov >= 0.4:
            matched_req.append(req_text)
        else:
            missing_req.append(req_text)

    req_score = (req_weighted_sum / req_total_weight * 100.0) if req_total_weight > 0 else 100.0

    pref_weighted_sum = 0.0
    pref_total_weight = 0.0

    for pref_text in (job.preferred_skills or []):
        pref_model = decompose_job_requirement(pref_text, is_required=False)
        res = match_requirement_against_evidence(pref_model, evidences)

        ev_found_labels = [ev.skill for ev in res.matched_evidences]
        cov = res.match_score
        match_lvl = "full" if cov >= 0.8 else "partial" if cov >= 0.4 else "weak" if cov > 0.0 else "missing"

        conceptual_matches.append(
            ConceptualRequirementMatch(
                requirement=pref_text,
                requirement_type="preferred",
                conceptual_scope=pref_model.concepts,
                evidence_found=res.evidenced_concepts if res.evidenced_concepts else ev_found_labels,
                critical_subtopics_missing=res.missing_concepts,
                coverage_ratio=cov,
                match_level=match_lvl,
                reasoning=res.explanation,
            )
        )

        w = pref_model.weight
        pref_weighted_sum += cov * w
        pref_total_weight += w

        if cov >= 0.4:
            matched_pref.append(pref_text)
        else:
            missing_pref.append(pref_text)

    pref_score = (pref_weighted_sum / pref_total_weight * 100.0) if pref_total_weight > 0 else 100.0

    if job.required_skills and job.preferred_skills:
        skills_score = req_score * 0.70 + pref_score * 0.30
    elif job.required_skills:
        skills_score = req_score
    elif job.preferred_skills:
        skills_score = pref_score
    else:
        skills_score = 100.0

    return (
        round(skills_score, 1),
        round(req_score, 1),
        matched_req,
        missing_req,
        matched_pref,
        missing_pref,
        conceptual_matches,
    )


def calculate_experience_score(candidate_years: float, minimum_years: Optional[float]) -> float:
    if minimum_years is None or minimum_years <= 0:
        return 100.0

    if candidate_years >= minimum_years:
        return 100.0

    score = (candidate_years / minimum_years) * 100.0
    return round(max(0.0, min(100.0, score)), 1)


def _get_degree_level(degree_name: Optional[str]) -> int:
    if not degree_name:
        return 0
    d_lower = degree_name.lower()
    for key, level in DEGREE_LEVELS.items():
        if key in d_lower:
            return level
    return 1


def calculate_education_score(
    candidate_education: List[EducationEntry],
    job_education: EducationRequirement,
) -> float:
    if not job_education.required and not job_education.degrees:
        return 100.0

    if not candidate_education:
        return 50.0 if job_education.required else 80.0

    req_level = max([_get_degree_level(d) for d in job_education.degrees], default=2)
    cand_level = max([_get_degree_level(e.degree) for e in candidate_education], default=0)

    if cand_level >= req_level:
        return 100.0
    elif cand_level > 0:
        return 70.0 if job_education.required else 85.0
    else:
        return 50.0 if job_education.required else 75.0


def calculate_recommendation_label(final_score: float) -> str:
    if final_score >= 8.0:
        return "Strong Match"
    elif final_score >= 6.5:
        return "Good Match"
    elif final_score >= 5.0:
        return "Partial Match"
    else:
        return "Weak Match"


def evaluate_candidate(
    resume: StructuredResume,
    job: JobDescription,
    semantic_fit: SemanticEvaluation,
) -> CandidateEvaluation:
    (
        skills_score,
        req_score,
        matched_req,
        missing_req,
        matched_pref,
        missing_pref,
        det_conceptual_matches,
    ) = calculate_conceptual_skill_score(resume=resume, job=job)

    # Merge deterministic conceptual matches with LLM conceptual matches if present
    llm_conceptual = semantic_fit.conceptual_matches or []
    if llm_conceptual:
        merged_conceptual_matches: List[ConceptualRequirementMatch] = list(llm_conceptual)
    else:
        merged_conceptual_matches: List[ConceptualRequirementMatch] = list(det_conceptual_matches)

    # Recalculate req_score and skills_score from merged conceptual matches
    if merged_conceptual_matches:
        req_items = [cm for cm in merged_conceptual_matches if (cm.requirement_type or "").lower() != "preferred"]
        pref_items = [cm for cm in merged_conceptual_matches if (cm.requirement_type or "").lower() == "preferred"]

        if req_items:
            req_sum = sum(((cm.coverage_ratio ** 1.5 if cm.coverage_ratio < 0.5 else cm.coverage_ratio) * 2.0) for cm in req_items)
            req_tot = len(req_items) * 2.0
            req_score = round((req_sum / req_tot) * 100.0, 1)

        if pref_items:
            pref_sum = sum(cm.coverage_ratio * 1.0 for cm in pref_items)
            pref_tot = len(pref_items) * 1.0
            pref_score = round((pref_sum / pref_tot) * 100.0, 1)
        else:
            pref_score = 100.0

        if req_items and pref_items:
            skills_score = round(req_score * 0.70 + pref_score * 0.30, 1)
        elif req_items:
            skills_score = req_score
        elif pref_items:
            skills_score = pref_score

    cand_years = calculate_experience_years(resume.experience)
    min_years = job.experience.minimum_years if job.experience else None
    exp_score = calculate_experience_score(cand_years, min_years)

    edu_score = calculate_education_score(resume.education, job.education)
    sem_score = max(0.0, min(100.0, semantic_fit.semantic_score))

    # Python Weighted Scoring Math (100% Total)
    # Skills: 40%, Experience: 25%, Education: 15%, Required Criteria: 10%, Semantic Fit: 10%
    percentage = (
        skills_score * 0.40
        + exp_score * 0.25
        + edu_score * 0.15
        + req_score * 0.10
        + sem_score * 0.10
    )

    final_score = round(percentage / 10.0, 1)
    recommendation = calculate_recommendation_label(final_score)

    breakdown = ScoreBreakdown(
        skills=skills_score,
        experience=exp_score,
        education=edu_score,
        required_criteria=req_score,
        semantic_fit=sem_score,
    )

    strengths = list(semantic_fit.semantic_strengths)
    if cand_years >= (min_years or 0) and min_years:
        strengths.append(f"Meets stated experience requirement ({cand_years} yrs demonstrated).")
    if matched_req:
        strengths.append(f"Demonstrates core required skills: {', '.join(matched_req[:4])}.")

    concerns = list(semantic_fit.semantic_concerns)
    if missing_req:
        concerns.append(f"Missing required skills: {', '.join(missing_req[:4])}.")
    if min_years and cand_years < min_years:
        concerns.append(f"Below required experience: {cand_years} yrs vs {min_years} yrs requested.")

    justification = (
        semantic_fit.justification
        or f"Candidate scores {final_score}/10 ({recommendation}). Demonstrates conceptual fit across {len(matched_req)}/{len(job.required_skills or [1])} required skills and {cand_years} years experience."
    )

    # Build evidence map
    evidence_items: List[EvidenceItem] = []
    for cm in merged_conceptual_matches:
        if cm.evidence_found:
            evidence_items.append(
                EvidenceItem(
                    requirement=cm.requirement,
                    evidence=f"Evidenced via: {', '.join(cm.evidence_found)}. {cm.reasoning}",
                )
            )

    det_eval = evaluate_candidate_deterministically(resume, job)
    sub_scores_model = SubScoresModel(
        technical_fit=det_eval.sub_scores.technical_fit,
        cs_fundamentals=det_eval.sub_scores.cs_fundamentals,
        problem_solving=det_eval.sub_scores.problem_solving,
        experience_alignment=det_eval.sub_scores.experience_alignment,
        education_fit=det_eval.sub_scores.education_fit,
        soft_skills_evidence=det_eval.sub_scores.soft_skills_evidence,
        technology_fit=det_eval.sub_scores.technology_fit,
        role_alignment=det_eval.sub_scores.role_alignment,
        adaptability=det_eval.sub_scores.adaptability,
    )

    return CandidateEvaluation(
        candidate_name=resume.candidate.name,
        score=final_score,
        score_confidence=det_eval.score_confidence,
        match_tier=det_eval.match_tier,
        recommendation=recommendation,
        score_breakdown=breakdown,
        sub_scores=sub_scores_model,
        matched_required_skills=matched_req,
        missing_required_skills=missing_req,
        matched_preferred_skills=matched_pref,
        missing_preferred_skills=missing_pref,
        strengths=strengths,
        concerns=concerns,
        justification=justification,
        evidence=evidence_items,
        conceptual_matches=merged_conceptual_matches,
    )


def evaluate_batch(
    resumes: List[StructuredResume],
    job: JobDescription,
    semantic_fits: List[SemanticEvaluation],
) -> List[CandidateEvaluation]:
    evaluations = []
    for idx, resume in enumerate(resumes):
        sem_fit = semantic_fits[idx] if idx < len(semantic_fits) else SemanticEvaluation()
        ev = evaluate_candidate(resume, job, sem_fit)
        evaluations.append(ev)

    evaluations.sort(key=lambda x: x.score, reverse=True)
    return evaluations
