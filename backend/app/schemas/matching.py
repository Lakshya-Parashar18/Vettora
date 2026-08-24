from enum import Enum
from typing import List
from pydantic import BaseModel, Field

from app.schemas.evidence import StructuredEvidence
from app.schemas.requirement import StructuredRequirement


class MatchType(str, Enum):
    DIRECT_MATCH = "DIRECT_MATCH"
    SEMANTIC_MATCH = "SEMANTIC_MATCH"
    HIERARCHICAL_CONCEPTUAL_MATCH = "HIERARCHICAL_CONCEPTUAL_MATCH"
    RELATED_BUT_NOT_EQUIVALENT = "RELATED_BUT_NOT_EQUIVALENT"
    NO_EVIDENCE = "NO_EVIDENCE"


class MatchResult(BaseModel):
    requirement: StructuredRequirement
    match_type: MatchType = MatchType.NO_EVIDENCE
    match_score: float = Field(0.0, ge=0.0, le=1.0)
    evidenced_concepts: List[str] = []
    missing_concepts: List[str] = []
    matched_evidences: List[StructuredEvidence] = []
    explanation: str = ""
