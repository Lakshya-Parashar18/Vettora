from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job import JobDescription
from app.schemas.resume import StructuredResume


class ScoreBreakdown(BaseModel):
    skills: float = Field(..., ge=0.0, le=100.0)
    experience: float = Field(..., ge=0.0, le=100.0)
    education: float = Field(..., ge=0.0, le=100.0)
    required_criteria: float = Field(..., ge=0.0, le=100.0)
    semantic_fit: float = Field(..., ge=0.0, le=100.0)


class EvidenceItem(BaseModel):
    requirement: str
    evidence: str


class ConceptualRequirementMatch(BaseModel):
    requirement: str
    requirement_type: str = "required"
    conceptual_scope: List[str] = []
    evidence_found: List[str] = []
    critical_subtopics_missing: List[str] = []
    coverage_ratio: float = Field(0.0, ge=0.0, le=1.0)
    match_level: str = "missing"
    reasoning: str = ""


class SubScoresModel(BaseModel):
    technical_fit: float = 80.0
    cs_fundamentals: float = 85.0
    problem_solving: float = 75.0
    experience_alignment: float = 75.0
    education_fit: float = 90.0
    soft_skills_evidence: float = 70.0
    technology_fit: float = 80.0
    role_alignment: float = 80.0
    adaptability: float = 80.0


class SemanticEvaluation(BaseModel):
    semantic_score: float = Field(80.0, ge=0.0, le=100.0)
    matched_requirements: List[str] = []
    semantic_strengths: List[str] = []
    semantic_concerns: List[str] = []
    evidence: List[EvidenceItem] = []
    justification: Optional[str] = None
    conceptual_matches: List[ConceptualRequirementMatch] = []


class CandidateEvaluation(BaseModel):
    candidate_id: Optional[str] = None
    candidate_name: Optional[str] = None
    score: float = Field(..., ge=0.0, le=10.0)
    score_confidence: float = 85.0  # 0.0 to 100.0%
    match_tier: str = "Strong Match"
    recommendation: str
    score_breakdown: ScoreBreakdown
    sub_scores: SubScoresModel = SubScoresModel()
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    strengths: List[str] = []
    concerns: List[str] = []
    justification: str = ""
    evidence: List[EvidenceItem] = []
    conceptual_matches: List[ConceptualRequirementMatch] = []


class ScreenRequest(BaseModel):
    resume: StructuredResume
    job: JobDescription


class BatchScreenRequest(BaseModel):
    resumes: List[StructuredResume]
    job: JobDescription


class ScreenResponse(BaseModel):
    evaluation: CandidateEvaluation


class BatchScreenResponse(BaseModel):
    evaluations: List[CandidateEvaluation]


class MongoScreenRequest(BaseModel):
    job_id: str
    resume_ids: List[str]


class CandidateSummary(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class CandidateResult(BaseModel):
    resume_id: str
    evaluation_id: Optional[str] = None
    status: str = "processed"
    candidate: CandidateSummary = CandidateSummary()
    score: Optional[float] = None
    score_confidence: Optional[float] = 85.0
    match_tier: Optional[str] = "Strong Match"
    recommendation: Optional[str] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    sub_scores: Optional[SubScoresModel] = SubScoresModel()
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    strengths: List[str] = []
    concerns: List[str] = []
    justification: Optional[str] = ""
    evidence: List[EvidenceItem] = []
    conceptual_matches: List[ConceptualRequirementMatch] = []
    error: Optional[dict] = None


class MongoScreenResponse(BaseModel):
    job_id: str
    candidates: List[CandidateResult]


class CandidatesListResponse(BaseModel):
    job_id: str
    candidates: List[CandidateResult]


class EvaluationDetailResponse(BaseModel):
    evaluation_id: str
    job_id: str
    resume_id: str
    candidate: CandidateSummary = CandidateSummary()
    score: float
    score_confidence: float = 85.0
    match_tier: str = "Strong Match"
    recommendation: str
    score_breakdown: ScoreBreakdown
    sub_scores: SubScoresModel = SubScoresModel()
    matched_required_skills: List[str] = []
    missing_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_preferred_skills: List[str] = []
    strengths: List[str] = []
    concerns: List[str] = []
    justification: str = ""
    evidence: List[EvidenceItem] = []
    conceptual_matches: List[ConceptualRequirementMatch] = []
    created_at: Optional[str] = None
