from typing import List, Optional
from pydantic import BaseModel


class ResumeCandidate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EducationEntry(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None


class ExperienceEntry(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []


class ResumeMetadata(BaseModel):
    extraction_method: str = "native"
    llm_structured: bool = False


class StructuredResume(BaseModel):
    candidate: ResumeCandidate
    skills: List[str] = []
    education: List[EducationEntry] = []
    experience: List[ExperienceEntry] = []
    projects: List[ProjectEntry] = []
    certifications: List[str] = []
    metadata: ResumeMetadata


class ResumeError(BaseModel):
    code: str
    message: str


class ResumeUploadItem(BaseModel):
    resume_id: Optional[str] = None
    filename: str
    status: str
    extraction_method: Optional[str] = "native"
    candidate: Optional[ResumeCandidate] = None
    resume: Optional[StructuredResume] = None
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    error: Optional[ResumeError] = None


class ResumeUploadResponse(BaseModel):
    resumes: List[ResumeUploadItem]


class ResumeGetResponse(BaseModel):
    resume_id: str
    filename: str
    status: str = "processed"
    resume: StructuredResume
    created_at: Optional[str] = None

