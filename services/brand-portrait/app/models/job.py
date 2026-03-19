from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[JobStatus] = mapped_column(
        SqlEnum(JobStatus, name="job_status"),
        default=JobStatus.QUEUED,
        nullable=False,
    )
    brand_profile: Mapped[str] = mapped_column(String(120), nullable=False)
    brand_profile_version: Mapped[str] = mapped_column(String(120), nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(10), nullable=False)
    preprocessing_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    input_path: Mapped[str] = mapped_column(String(255), nullable=False)
    quality_score: Mapped[float | None] = mapped_column(nullable=True)
    precheck_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    identity_threshold: Mapped[float] = mapped_column(nullable=False)
    brand_threshold: Mapped[float] = mapped_column(nullable=False)
    approved_variant_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    model_version: Mapped[str] = mapped_column(String(120), nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    variants = relationship(
        "Variant",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    approvals = relationship(
        "JobApproval",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    audit_events = relationship(
        "AuditEvent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
