from typing import List
from pydantic import BaseModel


class StructuredRequirement(BaseModel):
    requirement: str
    category: str = "technical"  # technical | cs_fundamentals | soft_skill | experience | education | technology | domain | other
    importance: str = "core"  # critical | core | supporting | nice_to_have
    weight: float = 1.0
    concepts: List[str] = []
    aliases: List[str] = []
    related_skills: List[str] = []
    evidence_rules: List[str] = []
    confidence: float = 1.0
