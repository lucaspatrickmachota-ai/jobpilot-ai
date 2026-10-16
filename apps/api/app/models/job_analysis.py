from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import Base


class JobAnalysis(Base):
    __tablename__ = "job_analyses"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    matched_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    analysis: Mapped[str] = mapped_column(Text, nullable=False)
    breakdown: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    application: Mapped["Application"] = relationship(back_populates="analyses")
