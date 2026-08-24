import pytest
from app.schemas.job import EducationRequirement, ExperienceRequirement, JobDescription
from app.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeCandidate,
    ResumeMetadata,
    StructuredResume,
)
from app.services.scoring_engine import (
    determine_match_tier,
    evaluate_candidate_deterministically,
)


def _sample_job():
    return JobDescription(
        title="Senior Software Engineer",
        required_skills=[
            "Python",
            "Data Structures & Algorithms",
            "Communication Skills",
        ],
        preferred_skills=[
            "Docker",
        ],
        experience=ExperienceRequirement(minimum_years=2.0),
        education=EducationRequirement(required=True, degrees=["B.Tech"], fields=["Computer Science"]),
    )


def _sample_resume():
    return StructuredResume(
        candidate=ResumeCandidate(name="Alice Developer", email="alice@test.com"),
        skills=["Python", "C++", "SQL"],
        education=[
            EducationEntry(degree="B.Tech", field="Computer Science", institution="Tech Uni", start_year="2020", end_year="2024")
        ],
        experience=[
            ExperienceEntry(job_title="Software Developer", company="Tech Corp", start_date="2024", end_date="2026", description="Developed Python microservices and algorithms.")
        ],
        projects=[
            ProjectEntry(name="Web App", description="Built Python backend with Data Structures", technologies=["Python"])
        ],
        certifications=["Core CS Coursework: Data Structures & Algorithms, Object-Oriented Programming, DBMS"],
        metadata=ResumeMetadata(extraction_method="native"),
    )


def test_score_reproducibility_100_percent_stable():
    """Verify that processing the same JD and resume 10 times yields 100% identical numerical results."""
    job = _sample_job()
    resume = _sample_resume()

    res1 = evaluate_candidate_deterministically(resume, job)

    for i in range(9):
        res_next = evaluate_candidate_deterministically(resume, job)
        assert res_next.overall_score == res1.overall_score
        assert res_next.score_10 == res1.score_10
        assert res_next.score_confidence == res1.score_confidence
        assert res_next.match_tier == res1.match_tier
        assert res_next.sub_scores.technical_fit == res1.sub_scores.technical_fit
        assert res_next.sub_scores.cs_fundamentals == res1.sub_scores.cs_fundamentals
        assert len(res_next.assessments) == len(res1.assessments)


def test_soft_skill_proof_of_absence_safeguard():
    """Verify missing soft skill (Communication) is tagged as interview validation, NOT proof of absence."""
    job = _sample_job()
    resume = _sample_resume()

    res = evaluate_candidate_deterministically(resume, job)
    comm_asm = next((a for a in res.assessments if "communication" in a.requirement.lower()), None)

    assert comm_asm is not None
    assert comm_asm.is_soft_skill_gap is True
    assert "validated during interview" in comm_asm.assessment_text.lower()
    assert "proof of absence" in comm_asm.assessment_text.lower()


def test_evidence_deduplication():
    """Verify 5 repeated mentions of Python in project do not artificially inflate score."""
    job = _sample_job()

    resume_single = _sample_resume()

    # Create resume with 5 repeated project mentions of Python
    resume_repeated = _sample_resume()
    resume_repeated.projects.append(
        ProjectEntry(name="Proj 2", description="Python Python Python Python Python", technologies=["Python", "Python"])
    )

    res_single = evaluate_candidate_deterministically(resume_single, job)
    res_repeated = evaluate_candidate_deterministically(resume_repeated, job)

    python_asm_1 = next((a for a in res_single.assessments if "python" in a.requirement.lower()), None)
    python_asm_2 = next((a for a in res_repeated.assessments if "python" in a.requirement.lower()), None)

    assert python_asm_1 is not None and python_asm_2 is not None
    # Score should be deduplicated and equal (100.0)
    assert python_asm_2.score == python_asm_1.score


def test_match_tier_classification():
    """Verify Match Tier thresholds: Excellent, Strong, Moderate, Weak, Insufficient Evidence."""
    assert determine_match_tier(90.0, 90.0) == "Excellent Match"
    assert determine_match_tier(80.0, 85.0) == "Strong Match"
    assert determine_match_tier(65.0, 80.0) == "Moderate Match"
    assert determine_match_tier(50.0, 70.0) == "Weak Match"
    assert determine_match_tier(40.0, 80.0) == "Insufficient Evidence"
    assert determine_match_tier(90.0, 20.0) == "Insufficient Evidence"
