from typing import List, Set, Tuple
from app.schemas.evidence import StructuredEvidence
from app.schemas.resume import StructuredResume
from app.services.skill_normalizer import normalize_skill


EVIDENCE_TYPE_WEIGHTS = {
    "work_experience": 1.00,
    "certification": 0.95,
    "coursework": 0.90,
    "project": 0.85,
    "leadership": 0.80,
    "skill_list": 0.70,
    "bare_mention": 0.50,
    "inferred": 0.40,
}

CORE_CS_KEYWORDS = [
    "data structures & algorithms", "data structures and algorithms", "data structures", "algorithms",
    "object-oriented programming", "object oriented programming", "oop", "oops",
    "dbms", "database management systems", "database management", "operating systems", "computer networks",
    "dsa", "os", "cn", "daa", "design & analysis of algorithms"
]


def mine_structured_evidence(resume: StructuredResume) -> List[StructuredEvidence]:
    """
    Extracts structured evidence across all sections of a StructuredResume
    and categorizes into 8 explicit evidence types with section traceability.
    """
    evidences: List[StructuredEvidence] = []
    seen: Set[Tuple[str, str]] = set()

    def add_evidence(skill: str, ev_type: str, text: str, section: str):
        norm = normalize_skill(skill)
        if not norm:
            norm = skill.strip()
        key = (norm.lower(), section.lower())
        if key not in seen:
            seen.add(key)
            strength = EVIDENCE_TYPE_WEIGHTS.get(ev_type, 0.70)
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

    # 1. Work-experience & Leadership evidence (F. Work-experience / G. Leadership)
    for exp in resume.experience:
        role_title = exp.job_title or "Role"
        comp = exp.company or "Company"
        desc = exp.description or ""
        text = f"Experience: {role_title} at {comp}. {desc}"

        role_lower = role_title.lower()
        if any(kw in role_lower for kw in ["lead", "manager", "head", "president", "director", "core member"]):
            add_evidence(role_title, "leadership", f"Leadership role: {role_title} at {comp}", "experience")
        else:
            add_evidence(role_title, "work_experience", text, "experience")

    # 2. Certification evidence (D. Certification)
    for cert in resume.certifications:
        add_evidence(cert, "certification", f"Certification: {cert}", "certifications")
        # Extract sub-subjects after colon or within comma-separated lists
        cert_text = cert.split(":", 1)[1] if ":" in cert else cert
        cert_lower = cert_text.lower()
        for kw in CORE_CS_KEYWORDS:
            if kw in cert_lower:
                add_evidence(kw.title(), "coursework", f"Subject in certification: {cert}", "certifications")

    # 3. Coursework / Education evidence (C. Coursework)
    for edu in resume.education:
        deg = edu.degree or ""
        fld = edu.field or ""
        inst = edu.institution or ""
        text = f"Education: {deg} {fld} at {inst}".strip()

        if deg:
            add_evidence(deg, "coursework", text, "education")
        if fld:
            add_evidence(fld, "coursework", text, "education")

        combined = f"{deg} {fld}".lower()
        for course in CORE_CS_KEYWORDS:
            if course in combined:
                add_evidence(course.title(), "coursework", f"Coursework in {text}", "education")

    # 4. Project evidence (E. Project)
    for proj in resume.projects:
        name = proj.name or "Project"
        desc = proj.description or ""
        text = f"Project '{name}': {desc}"

        for tech in proj.technologies:
            add_evidence(tech, "project", text, "projects")

        desc_lower = desc.lower()
        for kw in ["rest api", "full-stack", "machine learning", "deep learning", "python", "react", "fastapi", "aws", "docker"]:
            if kw in desc_lower:
                add_evidence(kw.title(), "project", text, "projects")

    # 5. Skill-list evidence (B. Skill-list)
    for s in resume.skills:
        add_evidence(s, "skill_list", f"Listed in skills section: {s}", "skills")

    return evidences
