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
from app.schemas.evaluation import SemanticEvaluation
from app.services.scoring_service import evaluate_candidate, calculate_conceptual_skill_score


def test_presidio_associate_engineer_evaluation():
    """
    Regression test for the Presidio Associate Engineer candidate failure.
    Candidate: B.Tech Computer Science Engineering (AI & ML) student.
    Core CS: DSA, OOP, DBMS, OS, Computer Networks.
    Skills/Tech: Java, Python, JavaScript, C++, SQL, React, FastAPI, Node.js, Express.js, MongoDB, Firebase, MySQL, Git/GitHub, OpenCV.
    Projects: Full-stack development, REST APIs, stock analytics, machine learning, traffic prediction, Python, Linux, secure data erasure.
    """
    job = JobDescription(
        title="Presidio Associate Engineer",
        required_skills=[
            "Strong fundamentals in computer science, IT, or related fields",
            "Problem-solving mindset",
            "Good communication and interpersonal skills",
            "Outgoing personality / customer engagement",
            "Curiosity and adaptability to emerging technologies",
        ],
        preferred_skills=[
            "Full-stack development",
            "REST APIs",
        ],
        experience=ExperienceRequirement(minimum_years=0.0),
        education=EducationRequirement(required=True, degrees=["B.Tech"], fields=["Computer Science"]),
    )

    resume = StructuredResume(
        candidate=ResumeCandidate(
            name="Presidio Candidate",
            email="candidate@presidio.test",
            phone="+91 98765 43210",
        ),
        skills=[
            "Java", "Python", "JavaScript", "C++", "SQL", "React", "FastAPI",
            "Node.js", "Express.js", "MongoDB", "Firebase", "MySQL", "Git/GitHub", "OpenCV",
        ],
        education=[
            EducationEntry(
                degree="B.Tech",
                field="Computer Science Engineering (AI & ML)",
                institution="Engineering College",
                start_year="2022",
                end_year="2026",
            )
        ],
        experience=[
            ExperienceEntry(
                job_title="Software Engineering Intern",
                company="Tech Solutions",
                start_date="2025-05",
                end_date="2025-08",
                description="Troubleshooting, engaging clients, and leveraging AI tools for software delivery.",
            )
        ],
        projects=[
            ProjectEntry(
                name="Stock Analytics & Traffic Prediction",
                description="Built full-stack web app with REST APIs using Python, React, FastAPI, and machine learning models.",
                technologies=["Python", "React", "FastAPI", "Machine Learning", "OpenCV"],
            ),
            ProjectEntry(
                name="Secure Data Erasure Tool",
                description="System tool for Linux data sanitization and troubleshooting.",
                technologies=["C++", "Linux"],
            ),
        ],
        certifications=["Core CS Coursework: Data Structures & Algorithms, Object-Oriented Programming, DBMS, Operating Systems, Computer Networks"],
        metadata=ResumeMetadata(extraction_method="native", llm_structured=True),
    )

    # 1. Test skill score calculation
    skills_score, req_score, matched_req, missing_req, m_pref, miss_pref, conceptual_matches = (
        calculate_conceptual_skill_score(resume=resume, job=job)
    )

    # Assert CS fundamentals requirement was NOT scored as 0% missing
    cs_match = next((cm for cm in conceptual_matches if "computer science" in cm.requirement.lower()), None)
    assert cs_match is not None
    assert cs_match.coverage_ratio >= 0.7
    assert cs_match.match_level in {"full", "partial"}

    # Assert problem solving requirement matched
    ps_match = next((cm for cm in conceptual_matches if "problem-solving" in cm.requirement.lower()), None)
    assert ps_match is not None
    assert ps_match.coverage_ratio >= 0.20

    # 2. Test overall candidate evaluation
    eval_result = evaluate_candidate(
        resume=resume,
        job=job,
        semantic_fit=SemanticEvaluation(semantic_score=85.0),
    )

    # Overall score must be high (>= 7.0/10) and recommendation Good or Strong Match
    assert eval_result.score >= 7.0
    assert eval_result.recommendation in {"Strong Match", "Good Match"}
    assert "Strong fundamentals in computer science, IT, or related fields" in eval_result.matched_required_skills
