from pydantic import BaseModel


class StructuredEvidence(BaseModel):
    skill: str
    evidence_type: str = "explicit_skill"  # explicit_skill | coursework | project | experience | certification | education | inferred
    evidence_strength: float = 1.0  # 0.0 to 1.0
    source_text: str = ""
    source_section: str = "skills"  # skills | education | experience | projects | certifications
    confidence: float = 1.0
