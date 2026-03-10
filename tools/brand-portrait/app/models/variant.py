from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Variant(Base, TimestampMixin):
    __tablename__ = "variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    variant_index: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    seed: Mapped[int | None] = mapped_column(nullable=True)
    generation_meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    identity_score: Mapped[float] = mapped_column(nullable=False)
    brand_score: Mapped[float] = mapped_column(nullable=False)
    quality_flags: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)

    job = relationship("Job", back_populates="variants")
