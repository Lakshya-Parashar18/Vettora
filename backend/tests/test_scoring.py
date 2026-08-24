import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.evaluation import ConceptualRequirementMatch, SemanticEvaluation
from app.schemas.job import EducationRequirement, ExperienceRequirement, JobDescription
from app.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    ResumeCandidate,
    ResumeMetadata,
    StructuredResume,
)
from app.services.scoring_service import (
    calculate_education_score,
    calculate_experience_score,
    calculate_experience_years,
    calculate_recommendation_label,
    calculate_skill_score,
    evaluate_candidate,
)

client = TestClient(app)


def _sample_resume(
    name="Jane Dev",
    skills=None,
    exp_years=4,
    degree="B.Tech",
) -> StructuredResume:
    skills = skills or ["Python", "FastAPI", "React", "PostgreSQL"]
    return StructuredResume(
        candidate=ResumeCandidate(name=name, email="jane@dev.io", phone="+91 99999 88888"),
        skills=skills,
        education=[EducationEntry(degree=degree, field="Computer Science", institution="IIT Bombay")],
        experience=[
            ExperienceEntry(
                job_title="Software Engineer",
                company="TechCorp",
                start_date=f"{2026 - exp_years}-01",
                end_date="Present",
                description="Built REST APIs.",
            )
        ],
        projects=[],
        certifications=[],
        metadata=ResumeMetadata(extraction_method="native", llm_structured=True),
    )


def _sample_job(
    required_skills=None,
    preferred_skills=None,
    min_exp=3.0,
    req_edu=True,
) -> JobDescription:
    required_skills = required_skills or ["Python", "FastAPI", "PostgreSQL"]
    preferred_skills = preferred_skills or ["Docker", "MongoDB"]
    return JobDescription(
        title="Backend Developer",
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience=ExperienceRequirement(minimum_years=min_exp),
        education=EducationRequirement(required=req_edu, degrees=["Bachelor's"]),
    )


def test_exact_skill_match():
    r_skills = ["Python", "FastAPI", "PostgreSQL"]
    j_req = ["Python", "FastAPI", "PostgreSQL"]
    score, req_s, m_req, miss_req, m_pref, miss_pref = calculate_skill_score(r_skills, j_req, [])
    assert req_s == 100.0
    assert len(miss_req) == 0


def test_partial_skill_match():
    r_skills = ["Python", "FastAPI"]
    j_req = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    score, req_s, m_req, miss_req, m_pref, miss_pref = calculate_skill_score(r_skills, j_req, [])
    assert req_s == 50.0
    assert "PostgreSQL" in miss_req
    assert "Docker" in miss_req


def test_preferred_skill_match():
    r_skills = ["Python", "FastAPI", "Docker"]
    j_req = ["Python", "FastAPI"]
    j_pref = ["Docker", "MongoDB"]
    score, req_s, m_req, miss_req, m_pref, miss_pref = calculate_skill_score(r_skills, j_req, j_pref)
    assert req_s == 100.0
    assert m_pref == ["Docker"]
    assert miss_pref == ["MongoDB"]


def test_experience_years_calculation():
    exps = [
        ExperienceEntry(job_title="Dev", company="A", start_date="2022-01", end_date="2024-01"),
        ExperienceEntry(job_title="Senior Dev", company="B", start_date="2024-01", end_date="Present"),
    ]
    years = calculate_experience_years(exps)
    assert years >= 2.0


def test_experience_scoring():
    assert calculate_experience_score(candidate_years=4.0, minimum_years=3.0) == 100.0
    assert calculate_experience_score(candidate_years=1.5, minimum_years=3.0) == 50.0
    assert calculate_experience_score(candidate_years=5.0, minimum_years=None) == 100.0


def test_education_scoring():
    edu = [EducationEntry(degree="B.Tech in Computer Science")]
    job_req = EducationRequirement(required=True, degrees=["Bachelor's"])
    assert calculate_education_score(edu, job_req) == 100.0

    job_master = EducationRequirement(required=True, degrees=["Master's"])
    assert calculate_education_score(edu, job_master) < 100.0


def test_recommendation_label_thresholds():
    assert calculate_recommendation_label(8.5) == "Strong Match"
    assert calculate_recommendation_label(7.2) == "Good Match"
    assert calculate_recommendation_label(5.8) == "Partial Match"
    assert calculate_recommendation_label(4.2) == "Weak Match"


def test_final_weighted_mathematical_calculation():
    # Candidate with 100% skills, 100% exp, 100% edu, 100% req, 100% sem -> score 10.0
    res = _sample_resume(skills=["Python", "FastAPI", "PostgreSQL", "Docker", "MongoDB"], exp_years=4)
    job = _sample_job(min_exp=3.0)
    sem = SemanticEvaluation(semantic_score=100.0)

    ev = evaluate_candidate(res, job, sem)
    # Skills: 100*0.40=40, Exp: 100*0.25=25, Edu: 100*0.15=15, Req: 100*0.10=10, Sem: 100*0.10=10 -> Total 100 -> 10.0
    assert ev.score == 10.0
    assert ev.recommendation == "Strong Match"


def test_candidate_below_experience_penalty():
    res = _sample_resume(exp_years=1)
    job = _sample_job(min_exp=4.0)
    sem = SemanticEvaluation(semantic_score=80.0)

    ev = evaluate_candidate(res, job, sem)
    assert ev.score < 8.0
    assert any("Below required experience" in c for c in ev.concerns)


@patch("app.services.llm_service._get_client")
def test_post_screen_endpoint(mock_get_client):
    mock_client = MagicMock()
    sem_resp = {
        "semantic_score": 85.0,
        "matched_requirements": ["FastAPI API design"],
        "semantic_strengths": ["Strong Python experience"],
        "semantic_concerns": [],
        "evidence": [{"requirement": "FastAPI", "evidence": "Built REST APIs using FastAPI."}],
        "justification": "Candidate has solid API experience.",
    }
    mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(sem_resp))
    mock_get_client.return_value = mock_client

    payload = {
        "resume": _sample_resume().model_dump(),
        "job": _sample_job().model_dump(),
    }

    response = client.post("/screen", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "evaluation" in data
    assert data["evaluation"]["score"] >= 8.0
    assert data["evaluation"]["recommendation"] == "Strong Match"
    assert "skills" in data["evaluation"]["score_breakdown"]


@patch("app.services.llm_service._get_client")
def test_post_screen_batch_endpoint_sorting(mock_get_client):
    mock_client = MagicMock()
    sem_resp = {"semantic_score": 80.0}
    mock_client.models.generate_content.return_value = MagicMock(text=json.dumps(sem_resp))
    mock_get_client.return_value = mock_client

    cand_strong = _sample_resume(name="Strong Candidate", skills=["Python", "FastAPI", "PostgreSQL", "Docker"], exp_years=5)
    cand_weak = _sample_resume(name="Weak Candidate", skills=["HTML"], exp_years=0)
    job = _sample_job()

    payload = {
        "resumes": [cand_weak.model_dump(), cand_strong.model_dump()],
        "job": job.model_dump(),
    }

    response = client.post("/screen/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "evaluations" in data
    assert len(data["evaluations"]) == 2
    # Verify sorted score descending
    assert data["evaluations"][0]["score"] >= data["evaluations"][1]["score"]
    assert data["evaluations"][0]["candidate_name"] == "Strong Candidate"


def test_conceptual_matching_scoring_logic():
    res = _sample_resume(skills=["Python"])
    job = _sample_job()
    
    # 2 required matches: one with full coverage, one with partial coverage
    conceptual_matches = [
        ConceptualRequirementMatch(
            requirement="Python programming",
            requirement_type="required",
            conceptual_scope=["Syntax", "OOP"],
            evidence_found=["Syntax", "OOP"],
            critical_subtopics_missing=[],
            coverage_ratio=1.0,
            match_level="full",
            reasoning="Strong evidence found."
        ),
        ConceptualRequirementMatch(
            requirement="FastAPI experience",
            requirement_type="required",
            conceptual_scope=["Routing", "Dependency Injection"],
            evidence_found=["Routing"],
            critical_subtopics_missing=["Dependency Injection"],
            coverage_ratio=0.5,
            match_level="partial",
            reasoning="Found routing but missing DI."
        ),
        ConceptualRequirementMatch(
            requirement="Docker containers",
            requirement_type="preferred",
            conceptual_scope=["Dockerfile", "Docker Compose"],
            evidence_found=["Dockerfile"],
            critical_subtopics_missing=["Docker Compose"],
            coverage_ratio=0.5,
            match_level="partial",
            reasoning="Dockerfile found."
        )
    ]
    sem = SemanticEvaluation(semantic_score=80.0, conceptual_matches=conceptual_matches)
    ev = evaluate_candidate(res, job, sem)
    
    # Required calculation:
    # Match 1: coverage 1.0 (no penalty) -> effective = 1.0. Weight = 2.0
    # Match 2: coverage 0.5 (no penalty since >= 0.5) -> effective = 0.5. Weight = 2.0
    # req_weighted_sum = (1.0 * 2.0) + (0.5 * 2.0) = 3.0
    # req_total_weight = 4.0
    # req_score = 3.0 / 4.0 * 100 = 75.0
    # Preferred calculation:
    # Match 3: coverage 0.5 -> effective = 0.5. Weight = 1.0
    # pref_score = 0.5 / 1.0 * 100 = 50.0
    # Skills score = 75.0 * 0.70 + 50.0 * 0.30 = 52.5 + 15.0 = 67.5
    assert ev.score_breakdown.required_criteria == 75.0
    assert ev.score_breakdown.skills == 67.5


def test_conceptual_matching_scoring_penalty():
    res = _sample_resume(skills=["Python"])
    job = _sample_job()
    
    # Required match with low coverage (< 0.5) to test penalty
    conceptual_matches = [
        ConceptualRequirementMatch(
            requirement="CS Fundamentals",
            requirement_type="required",
            conceptual_scope=["OS", "CN", "DAA", "DBMS"],
            evidence_found=["OS"],
            critical_subtopics_missing=["CN", "DAA", "DBMS"],
            coverage_ratio=0.25, # < 0.5
            match_level="weak",
            reasoning="Only OS is mentioned."
        )
    ]
    sem = SemanticEvaluation(semantic_score=80.0, conceptual_matches=conceptual_matches)
    ev = evaluate_candidate(res, job, sem)
    
    # Required calculation:
    # Match 1: coverage 0.25 < 0.5 -> effective = 0.25 ** 1.5 = 0.125. Weight = 2.0
    # req_score = 0.125 / 1.0 * 100 = 12.5 (rounded to 12.5)
    # Skills score = 12.5
    assert ev.score_breakdown.required_criteria == 12.5
    assert ev.score_breakdown.skills == 12.5
