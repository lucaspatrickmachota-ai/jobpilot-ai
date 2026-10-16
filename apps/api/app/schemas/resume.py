from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    filename: str
    content: str
    created_at: datetime


class JobAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    application_id: UUID
    match_score: int = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    breakdown: dict[str, int]
    analysis: str
    created_at: datetime


class JobRequirementsRead(BaseModel):
    job_title: str | None
    seniority: str | None
    required_skills: list[str]
    preferred_skills: list[str]
    technologies: list[str]
    years_experience: int | None
    education_requirements: list[str]
    languages: list[str]
    responsibilities: list[str]
    extraction_method: str


class JobDescriptionRequest(BaseModel):
    description: str = Field(min_length=30, max_length=30000)


class ResumeQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class ResumeEvidence(BaseModel):
    chunk_id: UUID
    content: str


class ResumeAnswer(BaseModel):
    answer: str
    evidence: list[ResumeEvidence]
    grounded: bool
