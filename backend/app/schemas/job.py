from typing import List, Optional
from pydantic import BaseModel


class ExperienceRequirement(BaseModel):
    minimum_years: Optional[float] = None
    maximum_years: Optional[float] = None


class EducationRequirement(BaseModel):
    required: bool = False
    degrees: List[str] = []
    fields: List[str] = []


class JobDescription(BaseModel):
    title: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience: ExperienceRequirement = ExperienceRequirement()
    education: EducationRequirement = EducationRequirement()
    responsibilities: List[str] = []
    preferred_qualifications: List[str] = []
    location: Optional[str] = None
    employment_type: Optional[str] = None


class JobCreateRequest(BaseModel):
    text: str


class JobError(BaseModel):
    code: str
    message: str


class JobPostResponse(BaseModel):
    job_id: Optional[str] = None
    status: str
    job: Optional[JobDescription] = None
    error: Optional[JobError] = None


class JobGetResponse(BaseModel):
    job_id: str
    status: str = "processed"
    job: JobDescription
    created_at: Optional[str] = None

