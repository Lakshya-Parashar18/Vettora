from typing import List, Dict, Set, Tuple

from app.schemas.evidence import StructuredEvidence
from app.schemas.matching import MatchResult, MatchType
from app.schemas.requirement import StructuredRequirement
from app.schemas.resume import StructuredResume
from app.services.skill_normalizer import normalize_skill


# Non-Equivalence Pairs (Requirement Skill -> Candidate Skill -> Relationship Reason)
# Guardrail rule: These skills are related, but NOT equivalent.
NON_EQUIVALENCE_MAP: Dict[str, Dict[str, str]] = {
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


# Known Conceptual Decompositions for Umbrella/Broad Requirements
CONCEPTUAL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "computer science fundamentals": {
        "category": "cs_fundamentals",
        "concepts": [
            "Data Structures",
            "Algorithms",
            "Object-Oriented Programming",
            "Database Management Systems",
            "Operating Systems",
            "Computer Networks",
            "Design & Analysis of Algorithms",
        ],
        "aliases": [
            "cs fundamentals",
            "core cs",
            "computer science core",
            "computer science principles",
            "fundamentals in computer science",
            "fundamentals in cs",
            "computer science, it",
            "computer science",
        ],
    },
    "it fundamentals": {
        "category": "cs_fundamentals",
        "concepts": [
            "Computer Networks",
            "Operating Systems",
            "Hardware & Systems",
            "Troubleshooting",
            "System Administration",
            "IT Infrastructure",
        ],
        "aliases": ["it principles", "information technology fundamentals"],
    },
    "problem-solving mindset": {
        "category": "soft_skill",
        "concepts": [
            "Data Structures & Algorithms",
            "Debugging & Troubleshooting",
            "System & Project Logic",
            "Analytical Thinking",
        ],
        "aliases": ["problem solving", "problem-solving skills", "analytical skills", "troubleshooting skills"],
    },
    "good communication and interpersonal skills": {
        "category": "soft_skill",
        "concepts": [
            "Client Engagement",
            "Technical Presentation",
            "Teamwork",
            "Cross-functional Collaboration",
            "Documentation",
            "Communication",
        ],
        "aliases": ["communication skills", "interpersonal skills", "communication & interpersonal skills", "soft skills"],
    },
    "outgoing personality / customer engagement": {
        "category": "soft_skill",
        "concepts": [
            "Client Engagement",
            "Customer Facing",
            "Stakeholder Management",
            "Presentation",
            "Communication",
        ],
        "aliases": ["customer engagement", "client facing", "outgoing personality"],
    },
    "curiosity and adaptability to emerging technologies": {
        "category": "domain",
        "concepts": [
            "AI/ML",
            "FastAPI",
            "React",
            "OpenCV",
            "Learning New Frameworks",
            "Self-taught Projects",
        ],
        "aliases": ["adaptability to emerging technologies", "adaptability", "fast learner", "emerging technologies"],
    },
    "full-stack development": {
        "category": "technical",
        "concepts": [
            "Frontend (React/Vue/HTML/CSS)",
            "Backend (Node/Python/Java/FastAPI)",
            "REST APIs",
            "Databases (MongoDB/PostgreSQL/SQL)",
        ],
        "aliases": ["fullstack", "full stack", "full-stack engineer"],
    },
}


# Direct Concept Synonyms
SYNONYM_MAP: Dict[str, str] = {
    "dsa": "Data Structures",
    "data structures & algorithms": "Data Structures",
    "data structures and algorithms": "Data Structures",
    "oop": "Object-Oriented Programming",
    "oops": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "dbms": "Database Management Systems",
    "rdbms": "Database Management Systems",
    "database management system": "Database Management Systems",
    "os": "Operating Systems",
    "operating system": "Operating Systems",
    "cn": "Computer Networks",
    "computer network": "Computer Networks",
    "daa": "Design & Analysis of Algorithms",
    "design and analysis of algorithms": "Design & Analysis of Algorithms",
    "ai": "Artificial Intelligence",
    "ml": "Machine Learning",
    "ai & ml": "Artificial Intelligence & Machine Learning",
    "ai/ml": "Artificial Intelligence & Machine Learning",
}


def extract_evidence_from_resume(resume: StructuredResume) -> List[StructuredEvidence]:
    """
    Extracts structured evidence items across all resume sections
    (skills, education coursework, projects, experience, certifications).
    """
    evidences: List[StructuredEvidence] = []
    seen: Set[Tuple[str, str]] = set()

    def add_ev(skill: str, ev_type: str, strength: float, text: str, section: str):
        norm = normalize_skill(skill)
        if not norm:
            return
        key = (norm.lower(), section.lower())
        if key not in seen:
            seen.add(key)
            evidences.append(
                StructuredEvidence(
                    skill=norm,
                    evidence_type=ev_type,
                    evidence_strength=strength,
                    source_text=text[:120],
                    source_section=section,
                    confidence=1.0,
                )
            )

    # 1. Explicit Skills Section
    for s in resume.skills:
        add_ev(s, "explicit_skill", 0.9, f"Listed in skills section: {s}", "skills")

    # 2. Education & Coursework Section
    for edu in resume.education:
        degree_text = f"{edu.degree or ''} {edu.field or ''} {edu.institution or ''}".strip()
        if degree_text:
            add_ev(
                edu.degree or edu.field or "Degree",
                "education",
                1.0,
                f"Education: {degree_text}",
                "education",
            )

        # Check for core subjects in education text
        full_text = f"{edu.degree or ''} {edu.field or ''}".lower()
        if "cs" in full_text or "computer science" in full_text or "engineering" in full_text:
            add_ev("Computer Science", "education", 1.0, f"Degree in CS: {degree_text}", "education")

    # 3. Projects Section
    for proj in resume.projects:
        proj_name = proj.name or "Project"
        proj_desc = proj.description or ""
        for tech in proj.technologies:
            add_ev(
                tech,
                "project",
                0.85,
                f"Used in project '{proj_name}': {proj_desc[:80]}",
                "projects",
            )
        # Extract skills from project text
        proj_full_text = f"{proj_name} {proj_desc}".lower()
        for kw in ["rest api", "full-stack", "machine learning", "python", "react", "fastapi", "opencv", "sql", "mongodb", "linux"]:
            if kw in proj_full_text:
                add_ev(kw.title(), "project", 0.8, f"Mentioned in project '{proj_name}'", "projects")

    # 4. Experience Section
    for exp in resume.experience:
        role_text = f"{exp.job_title or ''} at {exp.company or ''}".strip()
        desc_text = exp.description or ""
        add_ev(
            exp.job_title or "Experience",
            "experience",
            1.0,
            f"Role: {role_text}",
            "experience",
        )
        exp_full_text = f"{role_text} {desc_text}".lower()
        for kw in ["troubleshooting", "communication", "client", "python", "java", "react", "agile", "leadership"]:
            if kw in exp_full_text:
                add_ev(kw.title(), "experience", 0.9, f"Role evidence in {role_text}", "experience")

    # 5. Certifications Section
    for cert in resume.certifications:
        add_ev(cert, "certification", 0.95, f"Certified in: {cert}", "certifications")

    return evidences


def decompose_job_requirement(req_text: str, is_required: bool = True) -> StructuredRequirement:
    """
    Decomposes a raw job requirement string into a StructuredRequirement model.
    """
    clean_req = req_text.strip()
    req_lower = clean_req.lower()

    category = "technical"
    importance = "critical" if is_required else "nice_to_have"
    weight = 2.0 if is_required else 1.0
    concepts: List[str] = []
    aliases: List[str] = [clean_req]

    # Check if requirement matches a known taxonomy concept
    for key, tax_data in CONCEPTUAL_TAXONOMY.items():
        if key in req_lower or any(alias in req_lower for alias in tax_data.get("aliases", [])):
            category = tax_data.get("category", "technical")
            concepts = list(tax_data.get("concepts", []))
            aliases.extend(tax_data.get("aliases", []))
            break

    if not concepts:
        # Fallback single-concept requirement
        concepts = [clean_req]

    return StructuredRequirement(
        requirement=clean_req,
        category=category,
        importance=importance,
        weight=weight,
        concepts=concepts,
        aliases=list(set(aliases)),
        confidence=1.0,
    )


def match_requirement_against_evidence(
    req: StructuredRequirement,
    evidences: List[StructuredEvidence],
) -> MatchResult:
    """
    Evaluates evidence against a StructuredRequirement using a multi-tier matching strategy:
    1. NON_EQUIVALENCE_MAP Guardrail check
    2. DIRECT_MATCH
    3. SEMANTIC_MATCH
    4. HIERARCHICAL_CONCEPTUAL_MATCH
    5. NO_EVIDENCE
    """
    req_norm = normalize_skill(req.requirement).lower()

    # Create lookup map of candidate evidence skills
    evidence_map: Dict[str, StructuredEvidence] = {}
    for ev in evidences:
        norm_ev = normalize_skill(ev.skill).lower()
        if norm_ev not in evidence_map or ev.evidence_strength > evidence_map[norm_ev].evidence_strength:
            evidence_map[norm_ev] = ev

    matched_evidences: List[StructuredEvidence] = []

    # 1. NON-EQUIVALENCE GUARDRAIL CHECK (Check first so non-equivalent skills are NOT false matched!)
    if req_norm in NON_EQUIVALENCE_MAP:
        related_dict = NON_EQUIVALENCE_MAP[req_norm]
        for rel_skill, reason in related_dict.items():
            if rel_skill in evidence_map:
                ev = evidence_map[rel_skill]
                return MatchResult(
                    requirement=req,
                    match_type=MatchType.RELATED_BUT_NOT_EQUIVALENT,
                    match_score=0.3,  # Partial relation score, NOT equivalence!
                    evidenced_concepts=[],
                    missing_concepts=req.concepts,
                    matched_evidences=[ev],
                    explanation=f"Related but not equivalent: Candidate has '{ev.skill}', but requirement is '{req.requirement}'. {reason}",
                )

    # 2. DIRECT MATCH
    for alias in req.aliases:
        alias_norm = normalize_skill(alias).lower()
        if alias_norm in evidence_map:
            ev = evidence_map[alias_norm]
            return MatchResult(
                requirement=req,
                match_type=MatchType.DIRECT_MATCH,
                match_score=1.0,
                evidenced_concepts=req.concepts,
                missing_concepts=[],
                matched_evidences=[ev],
                explanation=f"Direct match: Found '{ev.skill}' in {ev.source_section} section ({ev.source_text}).",
            )

    # 3. SEMANTIC MATCH (Synonym resolution)
    for alias in req.aliases:
        alias_norm = normalize_skill(alias).lower()
        synonym = SYNONYM_MAP.get(alias_norm)
        if synonym and synonym.lower() in evidence_map:
            ev = evidence_map[synonym.lower()]
            return MatchResult(
                requirement=req,
                match_type=MatchType.SEMANTIC_MATCH,
                match_score=0.95,
                evidenced_concepts=req.concepts,
                missing_concepts=[],
                matched_evidences=[ev],
                explanation=f"Semantic synonym match: '{alias}' resolved to '{ev.skill}' in {ev.source_section} section.",
            )

    # 4. HIERARCHICAL / CONCEPTUAL MATCH (Umbrella requirements)
    evidenced_concepts: List[str] = []
    missing_concepts: List[str] = []

    if req.concepts:
        for concept in req.concepts:
            concept_norm = normalize_skill(concept).lower()

            # Search if concept or its synonyms/acronyms are present in evidence
            ev_found = None
            for ev_key, ev in evidence_map.items():
                if concept_match_is_valid(concept_norm, ev_key):
                    ev_found = ev
                    break

            if ev_found:
                evidenced_concepts.append(concept)
                if ev_found not in matched_evidences:
                    matched_evidences.append(ev_found)
            else:
                missing_concepts.append(concept)

        if len(req.concepts) > 0 and len(evidenced_concepts) > 0:
            coverage_score = round(len(evidenced_concepts) / len(req.concepts), 2)
            # Boost score slightly if majority of key sub-concepts are present
            effective_score = min(1.0, round(coverage_score * 1.1, 2)) if coverage_score >= 0.5 else coverage_score
            ev_sources = ", ".join([f"{ev.skill} ({ev.source_section})" for ev in matched_evidences[:4]])

            return MatchResult(
                requirement=req,
                match_type=MatchType.HIERARCHICAL_CONCEPTUAL_MATCH,
                match_score=effective_score,
                evidenced_concepts=evidenced_concepts,
                missing_concepts=missing_concepts,
                matched_evidences=matched_evidences,
                explanation=f"Hierarchical concept match ({len(evidenced_concepts)}/{len(req.concepts)} concepts evidenced via {ev_sources}).",
            )

    # 5. NO EVIDENCE FOUND
    return MatchResult(
        requirement=req,
        match_type=MatchType.NO_EVIDENCE,
        match_score=0.0,
        evidenced_concepts=[],
        missing_concepts=req.concepts,
        matched_evidences=[],
        explanation=f"No evidence found for requirement '{req.requirement}' in candidate resume.",
    )


def concept_match_is_valid(concept_norm: str, ev_key: str) -> bool:
    """Helper to check if concept and evidence key match via exact equality, word-boundary, or synonym."""
    if concept_norm == ev_key:
        return True
    
    # Check synonym dictionary
    syn_concept = SYNONYM_MAP.get(concept_norm, "").lower()
    syn_ev = SYNONYM_MAP.get(ev_key, "").lower()
    if syn_concept and syn_concept == ev_key:
        return True
    if syn_ev and syn_ev == concept_norm:
        return True
    if syn_concept and syn_ev and syn_concept == syn_ev:
        return True

    # Word boundary match for multi-word concepts (avoid raw substring errors like "sql" in "postgresql")
    if len(concept_norm) >= 4 and len(ev_key) >= 4:
        if concept_norm in ev_key or ev_key in concept_norm:
            return True

    return False
