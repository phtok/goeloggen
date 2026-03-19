from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: JobStatus
    brand_profile: str
    brand_profile_version: str
    aspect_ratio: str
    preprocessing_enabled: bool
    input_path: str
    quality_score: float | None
    precheck_data: dict[str, Any]
    identity_threshold: float
    brand_threshold: float
    approved_variant_id: str | None
    model_version: str
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class JobCreateResponse(BaseModel):
    job: JobRead
    queue_name: str
    message: str


class VariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    variant_index: int
    image_path: str
    seed: int | None
    generation_meta: dict[str, Any]
    identity_score: float
    brand_score: float
    quality_flags: dict[str, Any]
    is_approved: bool
    created_at: datetime
    updated_at: datetime


class ApproveVariantRequest(BaseModel):
    variant_id: str = Field(min_length=36, max_length=36)


class JobApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    variant_id: str
    actor_id: str
    actor_role: str
    created_at: datetime
    updated_at: datetime


class ApprovalStateRead(BaseModel):
    mode: str
    required_roles: list[str]
    approvals: list[JobApprovalRead]
    is_fully_approved: bool
    approved_variant_id: str | None


class ApproveVariantResponse(BaseModel):
    variant: VariantRead
    approval_state: ApprovalStateRead


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str | None
    actor_id: str
    actor_role: str
    action: str
    details: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ExportResponse(BaseModel):
    job_id: str
    approved_variant_id: str
    web_url: str
    print_url: str
    metadata: dict[str, Any]
