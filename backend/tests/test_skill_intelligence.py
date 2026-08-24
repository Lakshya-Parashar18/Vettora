import pytest
from app.schemas.evidence import StructuredEvidence
from app.schemas.job import EducationRequirement, ExperienceRequirement, JobDescription
from app.schemas.resume import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeCandidate,
    ResumeMetadata,
    StructuredResume,
)
from app.services.evidence_miner import mine_structured_evidence
from app.services.ontology_service import ontology_engine
from app.services.requirement_decomposer import decompose_compound_requirement
from app.services.skill_intelligence import evaluate_skill_intelligence, IntelligenceMatchResult


def test_1_cs_fundamentals_subtopic_coverage():
    """CS fundamentals ← DSA + OOP + DBMS + OS + CN"""
    req = decompose_compound_requirement("Computer Science Fundamentals")[0]
    evidences = [
        StructuredEvidence(skill="Data Structures", evidence_type="coursework", evidence_strength=0.9, source_section="education"),
        StructuredEvidence(skill="Object-Oriented Programming", evidence_type="coursework", evidence_strength=0.9, source_section="education"),
        StructuredEvidence(skill="Database Management Systems", evidence_type="coursework", evidence_strength=0.9, source_section="education"),
        StructuredEvidence(skill="Operating Systems", evidence_type="coursework", evidence_strength=0.9, source_section="education"),
        StructuredEvidence(skill="Computer Networks", evidence_type="coursework", evidence_strength=0.9, source_section="education"),
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.subtopic_coverage_ratio >= 0.7
    assert len(res.provenance_chain) >= 5


def test_2_kubernetes_vs_docker():
    """Kubernetes ← Docker (related, NOT full match!)"""
    req = decompose_compound_requirement("Kubernetes")[0]
    evidences = [
        StructuredEvidence(skill="Docker", evidence_type="explicit_skill", evidence_strength=0.7, source_section="skills")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level == "RELATED"
    assert res.match_score < 0.5
    assert "Docker is a containerization engine" in res.explanation


def test_3_deep_learning_vs_machine_learning():
    """Deep Learning ← Machine Learning (related, NOT full match!)"""
    req = decompose_compound_requirement("Deep Learning")[0]
    evidences = [
        StructuredEvidence(skill="Machine Learning", evidence_type="project", evidence_strength=0.85, source_section="projects")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level == "RELATED"
    assert res.match_score < 0.5
    assert "Machine learning is a broader field" in res.explanation


def test_4_sql_vs_mysql():
    """SQL ← MySQL (child technology -> strong match)"""
    req = decompose_compound_requirement("SQL")[0]
    evidences = [
        StructuredEvidence(skill="MySQL", evidence_type="explicit_skill", evidence_strength=0.7, source_section="skills")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.match_score >= 0.7


def test_5_postgresql_vs_sql():
    """PostgreSQL ← SQL (SQL standard -> related, missing engine specifics)"""
    req = decompose_compound_requirement("PostgreSQL")[0]
    evidences = [
        StructuredEvidence(skill="SQL", evidence_type="explicit_skill", evidence_strength=0.7, source_section="skills")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"RELATED", "PARTIAL_MATCH"}
    assert res.match_score < 0.8


def test_6_react_vs_angular():
    """React ← Angular (related UI framework, NOT equal!)"""
    req = decompose_compound_requirement("React")[0]
    evidences = [
        StructuredEvidence(skill="Angular", evidence_type="explicit_skill", evidence_strength=0.7, source_section="skills")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level == "RELATED"
    assert res.match_score < 0.5
    assert "Angular is a full framework" in res.explanation


def test_7_rest_api_vs_fastapi_rest_api():
    """REST API ← FastAPI REST API (strong/full match)"""
    req = decompose_compound_requirement("REST API")[0]
    evidences = [
        StructuredEvidence(skill="FastAPI REST API", evidence_type="project", evidence_strength=0.85, source_section="projects")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.match_score >= 0.7


def test_8_python_project_evidence_strength():
    """Python ← Python project (project evidence strength = 0.85)"""
    req = decompose_compound_requirement("Python")[0]
    evidences = [
        StructuredEvidence(skill="Python", evidence_type="project", evidence_strength=0.85, source_section="projects")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.match_score == 0.85


def test_9_aws_certification_evidence_strength():
    """AWS ← AWS certification (certification evidence strength = 0.95)"""
    req = decompose_compound_requirement("AWS")[0]
    evidences = [
        StructuredEvidence(skill="AWS Certified Solutions Architect", evidence_type="certification", evidence_strength=0.95, source_section="certifications")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.match_score >= 0.90


def test_10_aws_production_deployment_vs_coursework():
    """AWS production deployment ← AWS course only (coursework evidence vs production)"""
    req = decompose_compound_requirement("AWS Production Deployment")[0]
    evidences = [
        StructuredEvidence(skill="AWS Course", evidence_type="coursework", evidence_strength=0.5, source_section="education")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"PARTIAL_MATCH", "STRONG_MATCH", "RELATED"}
    assert res.match_score <= 0.85


def test_11_communication_no_evidence():
    """Communication ← no evidence (missing)"""
    req = decompose_compound_requirement("Communication Skills")[0]
    evidences = [
        StructuredEvidence(skill="Python", evidence_type="explicit_skill", evidence_strength=0.7, source_section="skills")
    ]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level == "MISSING"
    assert res.match_score == 0.0


def test_12_leadership_gdsc_core_member():
    """Leadership ← GDSC core member (leadership evidence match)"""
    resume = StructuredResume(
        candidate=ResumeCandidate(name="Student Lead"),
        skills=["Python"],
        education=[],
        experience=[
            ExperienceEntry(
                job_title="GDSC Core Member",
                company="Google Developer Student Club",
                start_date="2024",
                end_date="Present",
                description="Lead technical workshops and community events.",
            )
        ],
        projects=[],
        certifications=[],
        metadata=ResumeMetadata(extraction_method="native"),
    )

    evidences = mine_structured_evidence(resume)
    req = decompose_compound_requirement("Leadership")[0]
    res = evaluate_skill_intelligence(req, evidences)

    assert res.match_level in {"FULL_MATCH", "STRONG_MATCH"}
    assert res.match_score >= 0.70
    assert any(p.evidence_type == "leadership" for p in res.provenance_chain)
