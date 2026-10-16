from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    job_url: HttpUrl | None = None
    description: str | None = Field(default=None, max_length=30000)
    status: ApplicationStatus = ApplicationStatus.SAVED


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, min_length=1, max_length=200)
    job_url: HttpUrl | None = None
    description: str | None = Field(default=None, max_length=30000)
    status: ApplicationStatus | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company: str
    position: str
    job_url: str | None
    description: str | None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    total: int
    saved: int
    applied: int
    interviews: int
    offers: int
    rejected: int
    interview_conversion_percent: float
