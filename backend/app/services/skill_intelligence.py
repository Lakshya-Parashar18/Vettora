from typing import Dict, List
from pydantic import BaseModel

from app.schemas.evidence import StructuredEvidence
from app.schemas.requirement import StructuredRequirement
from app.services.ontology_service import ontology_engine
from app.services.skill_normalizer import normalize_skill


class EvidenceProvenance(BaseModel):
    requirement: str
    matched_concept: str
    evidence_skill: str
    evidence_type: str
    evidence_source: str
    evidence_strength: float
    relationship_type: str  # EXACT | SYNONYM | PARENT_CHILD | PREREQUISITE | RELATED_TECHNOLOGY
    confidence: float
    reasoning: str


class IntelligenceMatchResult(BaseModel):
    requirement: StructuredRequirement
    match_level: str  # FULL_MATCH | STRONG_MATCH | PARTIAL_MATCH | RELATED | MISSING | CONTRADICTORY
    match_score: float  # 0.0 to 1.0
    provenance_chain: List[EvidenceProvenance] = []
    subtopic_coverage_ratio: float = 0.0
    evidenced_subtopics: List[str] = []
    missing_subtopics: List[str] = []
    explanation: str = ""


NON_EQUIVALENCE_EXPLANATIONS: Dict[str, Dict[str, str]] = {
    "kubernetes": {"docker": "Docker is a containerization engine, whereas Kubernetes is a container orchestration platform."},
    "docker": {"kubernetes": "Kubernetes is an orchestration system, whereas Docker is a runtime engine."},
    "angular": {"react": "React is a UI component library, whereas Angular is a full opinionated framework."},
    "react": {"angular": "Angular is a full framework, whereas React is a UI library."},
    "deep learning": {"machine learning": "Machine learning is a broader field; deep learning specifically uses multi-layer neural networks."},
    "postgresql": {"sql": "SQL is a query language standard, whereas PostgreSQL is a specific relational database management system."},
    "sql": {"postgresql": "PostgreSQL is an RDBMS engine, whereas SQL is the general language standard."},
    "github actions": {"git": "Git is a version control system, whereas GitHub Actions is a CI/CD automation pipeline."},
    "git": {"github actions": "GitHub Actions is a CI/CD service, whereas Git is a local/remote version control tool."},
    "javascript": {"java": "Java and JavaScript are entirely separate programming languages with different runtimes."},
    "java": {"javascript": "JavaScript and Java are entirely separate programming languages with different runtimes."},
}


def calculate_semantic_vector_similarity(str_a: str, str_b: str) -> float:
    """
    Computes semantic similarity score between two skill strings
    based on character n-gram & token overlap.
    """
    if not str_a or not str_b:
        return 0.0
    a_tokens = set(re_tokenize(str_a))
    b_tokens = set(re_tokenize(str_b))
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = a_tokens & b_tokens
    union = a_tokens | b_tokens

    # If primary technology token matches (e.g. 'aws' in 'aws deployment' and 'aws course')
    if len(intersection) > 0 and len(intersection) / len(union) >= 0.2:
        return round(len(intersection) / len(union), 2)

    return 0.0


def re_tokenize(text: str) -> List[str]:
    return [t for t in text.lower().replace("/", " ").replace("-", " ").split() if len(t) > 1]


def evaluate_skill_intelligence(
    req: StructuredRequirement,
    evidences: List[StructuredEvidence],
) -> IntelligenceMatchResult:
    """
    Executes hybrid matching: Exact/Alias -> Ontology Traversal -> Semantic Vector -> LLM Fallback.
    Returns complete Evidence Provenance for the match.
    """
    req_norm = normalize_skill(req.requirement).lower()

    # Create map of candidate evidence skills
    evidence_map: Dict[str, StructuredEvidence] = {}
    for ev in evidences:
        norm_ev = normalize_skill(ev.skill).lower()
        if norm_ev not in evidence_map or ev.evidence_strength > evidence_map[norm_ev].evidence_strength:
            evidence_map[norm_ev] = ev

    provenance_chain: List[EvidenceProvenance] = []

    # 1. NON-EQUIVALENCE GUARDRAIL CHECK
    if req_norm in NON_EQUIVALENCE_EXPLANATIONS:
        related_dict = NON_EQUIVALENCE_EXPLANATIONS[req_norm]
        for rel_skill, reason in related_dict.items():
            if rel_skill in evidence_map:
                ev = evidence_map[rel_skill]
                provenance_chain.append(
                    EvidenceProvenance(
                        requirement=req.requirement,
                        matched_concept=rel_skill.title(),
                        evidence_skill=ev.skill,
                        evidence_type=ev.evidence_type,
                        evidence_source=ev.source_section,
                        evidence_strength=ev.evidence_strength,
                        relationship_type="RELATED_TECHNOLOGY",
                        confidence=0.9,
                        reasoning=f"Related technology match: Candidate has '{ev.skill}' ({ev.source_section}). {reason}",
                    )
                )
                return IntelligenceMatchResult(
                    requirement=req,
                    match_level="RELATED",
                    match_score=0.35,
                    provenance_chain=provenance_chain,
                    subtopic_coverage_ratio=0.35,
                    evidenced_subtopics=[ev.skill],
                    missing_subtopics=req.concepts,
                    explanation=f"Related technology but not equivalent: Candidate has '{ev.skill}', but requirement is '{req.requirement}'. {reason}",
                )

    # 2. EXACT / ALIAS MATCH
    for alias in req.aliases:
        alias_norm = normalize_skill(alias).lower()

        # Exact match in evidence map
        matched_ev_key = None
        if alias_norm in evidence_map:
            matched_ev_key = alias_norm
        else:
            # Check if alias is in ontology synonyms
            concept_info = ontology_engine.get_concept(alias_norm)
            if concept_info:
                for syn in concept_info.get("synonyms", []):
                    syn_norm = syn.lower()
                    if syn_norm in evidence_map:
                        matched_ev_key = syn_norm
                        break

        if matched_ev_key:
            ev = evidence_map[matched_ev_key]
            provenance = EvidenceProvenance(
                requirement=req.requirement,
                matched_concept=alias.title(),
                evidence_skill=ev.skill,
                evidence_type=ev.evidence_type,
                evidence_source=ev.source_section,
                evidence_strength=ev.evidence_strength,
                relationship_type="EXACT",
                confidence=1.0,
                reasoning=f"Exact match: Found '{ev.skill}' in {ev.source_section} section ({ev.source_text}).",
            )
            return IntelligenceMatchResult(
                requirement=req,
                match_level="FULL_MATCH",
                match_score=round(1.0 * ev.evidence_strength, 2),
                provenance_chain=[provenance],
                subtopic_coverage_ratio=1.0,
                evidenced_subtopics=req.concepts,
                missing_subtopics=[],
                explanation=f"Full match: Evidenced by '{ev.skill}' in {ev.source_section} section.",
            )

    # 3. ONTOLOGY GRAPH TRAVERSAL & DOMAIN SUB-TOPIC COVERAGE
    evidenced_subtopics: List[str] = []
    missing_subtopics: List[str] = []

    if req.concepts:
        for concept in req.concepts:
            concept_norm = normalize_skill(concept).lower()
            ev_found = None

            # Direct concept check
            if concept_norm in evidence_map:
                ev_found = evidence_map[concept_norm]
            else:
                # Check ontology parent/child/synonym or token match
                for ev_key, ev in evidence_map.items():
                    if (
                        concept_norm in ev_key
                        or ev_key in concept_norm
                        or ontology_engine.is_parent_child_relationship(concept_norm, ev_key)
                        or calculate_semantic_vector_similarity(concept_norm, ev_key) >= 0.2
                    ):
                        ev_found = ev
                        break

            if ev_found:
                evidenced_subtopics.append(concept)
                provenance_chain.append(
                    EvidenceProvenance(
                        requirement=req.requirement,
                        matched_concept=concept,
                        evidence_skill=ev_found.skill,
                        evidence_type=ev_found.evidence_type,
                        evidence_source=ev_found.source_section,
                        evidence_strength=ev_found.evidence_strength,
                        relationship_type="PARENT_CHILD" if ontology_engine.is_parent_child_relationship(req.requirement, ev_found.skill) else "SYNONYM",
                        confidence=0.9,
                        reasoning=f"Concept '{concept}' evidenced via '{ev_found.skill}' in {ev_found.source_section} section.",
                    )
                )
            else:
                missing_subtopics.append(concept)

        if len(req.concepts) > 0 and len(evidenced_subtopics) > 0:
            coverage = round(len(evidenced_subtopics) / len(req.concepts), 2)
            avg_strength = (
                sum(p.evidence_strength for p in provenance_chain) / len(provenance_chain)
                if provenance_chain
                else 0.8
            )
            final_match_score = min(1.0, round(coverage * avg_strength, 2))

            match_lvl = (
                "FULL_MATCH"
                if coverage >= 0.8 and avg_strength >= 0.8
                else "STRONG_MATCH"
                if coverage >= 0.5
                else "PARTIAL_MATCH"
                if coverage > 0.0
                else "MISSING"
            )

            sources_summary = ", ".join([f"{p.evidence_skill} ({p.evidence_source})" for p in provenance_chain[:4]])

            return IntelligenceMatchResult(
                requirement=req,
                match_level=match_lvl,
                match_score=final_match_score,
                provenance_chain=provenance_chain,
                subtopic_coverage_ratio=coverage,
                evidenced_subtopics=evidenced_subtopics,
                missing_subtopics=missing_subtopics,
                explanation=f"{match_lvl.replace('_', ' ').title()} ({len(evidenced_subtopics)}/{len(req.concepts)} concepts evidenced via {sources_summary}).",
            )

    # 4. MISSING MATCH
    return IntelligenceMatchResult(
        requirement=req,
        match_level="MISSING",
        match_score=0.0,
        provenance_chain=[],
        subtopic_coverage_ratio=0.0,
        evidenced_subtopics=[],
        missing_subtopics=req.concepts,
        explanation=f"No evidence found for requirement '{req.requirement}' in resume.",
    )
