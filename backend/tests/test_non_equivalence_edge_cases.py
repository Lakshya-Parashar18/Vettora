import pytest
from app.schemas.evidence import StructuredEvidence
from app.schemas.requirement import StructuredRequirement
from app.services.matching_engine import (
    decompose_job_requirement,
    match_requirement_against_evidence,
    MatchType,
)


def test_docker_vs_kubernetes_non_equivalence():
    req = decompose_job_requirement("Kubernetes", is_required=True)
    evidences = [
        StructuredEvidence(
            skill="Docker",
            evidence_type="explicit_skill",
            evidence_strength=0.9,
            source_text="Docker containerization",
            source_section="skills",
        )
    ]
    res = match_requirement_against_evidence(req, evidences)

    assert res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT
    assert res.match_score == 0.3
    assert "Docker is a containerization engine" in res.explanation


def test_react_vs_angular_non_equivalence():
    req = decompose_job_requirement("Angular", is_required=True)
    evidences = [
        StructuredEvidence(
            skill="React",
            evidence_type="explicit_skill",
            evidence_strength=0.9,
            source_text="React frontend UI",
            source_section="skills",
        )
    ]
    res = match_requirement_against_evidence(req, evidences)

    assert res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT
    assert res.match_score == 0.3
    assert "React is a UI component library" in res.explanation


def test_machine_learning_vs_deep_learning_non_equivalence():
    req = decompose_job_requirement("Deep Learning", is_required=True)
    evidences = [
        StructuredEvidence(
            skill="Machine Learning",
            evidence_type="explicit_skill",
            evidence_strength=0.9,
            source_text="Machine Learning models",
            source_section="skills",
        )
    ]
    res = match_requirement_against_evidence(req, evidences)

    assert res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT
    assert res.match_score == 0.3
    assert "Machine learning is a broader field" in res.explanation


def test_sql_vs_postgresql_non_equivalence():
    req = decompose_job_requirement("PostgreSQL", is_required=True)
    evidences = [
        StructuredEvidence(
            skill="SQL",
            evidence_type="explicit_skill",
            evidence_strength=0.9,
            source_text="SQL queries",
            source_section="skills",
        )
    ]
    res = match_requirement_against_evidence(req, evidences)

    assert res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT
    assert res.match_score == 0.3
    assert "SQL is a query language standard" in res.explanation


def test_git_vs_github_actions_non_equivalence():
    req = decompose_job_requirement("GitHub Actions", is_required=True)
    evidences = [
        StructuredEvidence(
            skill="Git",
            evidence_type="explicit_skill",
            evidence_strength=0.9,
            source_text="Git version control",
            source_section="skills",
        )
    ]
    res = match_requirement_against_evidence(req, evidences)

    assert res.match_type == MatchType.RELATED_BUT_NOT_EQUIVALENT
    assert res.match_score == 0.3
    assert "Git is a version control system" in res.explanation
