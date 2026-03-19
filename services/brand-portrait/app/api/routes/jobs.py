from __future__ import annotations

import io
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_artifact_store,
    get_current_actor,
    get_face_detector,
    get_queue_client,
    get_runtime_settings,
    require_actor_roles,
)
from app.core.settings import Settings
from app.db.session import get_db_session
from app.models import Job, JobApproval, JobStatus
from app.repositories.jobs import (
    get_actor_approval,
    get_job,
    get_variant,
    list_approvals,
    list_audit_events,
    list_variants,
)
from app.schemas.jobs import (
    ApprovalStateRead,
    ApproveVariantRequest,
    ApproveVariantResponse,
    AuditEventRead,
    ExportResponse,
    JobApprovalRead,
    JobCreateResponse,
    JobRead,
    VariantRead,
)
from app.services.audit import log_audit_event
from app.services.auth import Actor
from app.services.brand_profile import list_brand_profiles
from app.services.face_detection import BaseFaceDetector
from app.services.precheck import analyze_portrait
from app.services.queue import QueueClient
from app.services.storage import ArtifactStore

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _normalize_aspect_ratio(value: str, fallback: str) -> str:
    raw = (value or fallback).strip()
    parts = raw.split(":")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="aspect_ratio must have format '<width>:<height>', e.g. 4:5",
        )
    try:
        width = int(parts[0])
        height = int(parts[1])
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="aspect_ratio must contain integer values",
        ) from exc

    if width <= 0 or height <= 0:
        raise HTTPException(
            status_code=400,
            detail="aspect_ratio values must be greater than zero",
        )
    return f"{width}:{height}"


def _approval_required_roles(settings: Settings) -> list[str]:
    mode = settings.approval_mode.strip().lower()
    if mode == "double":
        return ["editor", "brand_owner"]
    return ["editor"]


def _is_variant_fully_approved(
    *,
    settings: Settings,
    approvals: list[JobApproval],
    variant_id: str,
    actor: Actor,
) -> bool:
    if actor.role == "admin":
        return True
    relevant_roles = {
        approval.actor_role
        for approval in approvals
        if approval.variant_id == variant_id
    }
    if settings.approval_mode.strip().lower() == "double":
        return "editor" in relevant_roles and "brand_owner" in relevant_roles
    return bool(relevant_roles.intersection({"editor", "brand_owner"}))


def _build_approval_state(
    *,
    settings: Settings,
    job: Job,
    variant_id: str,
    approvals: list[JobApproval],
) -> ApprovalStateRead:
    filtered = [approval for approval in approvals if approval.variant_id == variant_id]
    return ApprovalStateRead(
        mode=settings.approval_mode,
        required_roles=_approval_required_roles(settings),
        approvals=[JobApprovalRead.model_validate(approval) for approval in filtered],
        is_fully_approved=job.approved_variant_id == variant_id,
        approved_variant_id=job.approved_variant_id,
    )


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    image: UploadFile = File(...),
    brand_profile: str = Form("goe_brand_v1"),
    aspect_ratio: str = Form("4:5"),
    enable_preprocessing: bool = Form(True),
    actor: Actor = Depends(require_actor_roles("editor", "admin")),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_runtime_settings),
    queue: QueueClient = Depends(get_queue_client),
    store: ArtifactStore = Depends(get_artifact_store),
    face_detector: BaseFaceDetector = Depends(get_face_detector),
) -> JobCreateResponse:
    if not image.filename:
        raise HTTPException(status_code=400, detail="image filename is required")

    suffix = Path(image.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"unsupported image type: {suffix}. allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    payload = await image.read()
    if not payload:
        raise HTTPException(status_code=400, detail="empty upload payload")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(payload) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"file too large. max {settings.max_upload_mb} MB",
        )

    available_profiles = list_brand_profiles(settings)
    if brand_profile not in available_profiles:
        raise HTTPException(
            status_code=400,
            detail=f"unknown brand_profile '{brand_profile}'. available: {available_profiles}",
        )

    try:
        with Image.open(io.BytesIO(payload)) as loaded:
            source = loaded.convert("RGB")
            precheck = analyze_portrait(
                source,
                face_detector=face_detector,
                min_confidence=settings.face_detector_min_confidence,
            )
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="invalid image file") from exc

    if precheck.face_count != 1:
        raise HTTPException(
            status_code=422,
            detail=(
                f"expected exactly one face, got {precheck.face_count} "
                f"(detector={precheck.face_detector_provider})"
            ),
        )

    if min(precheck.width, precheck.height) < 512:
        raise HTTPException(
            status_code=422,
            detail="input image too small. minimum edge is 512 pixels",
        )

    normalized_aspect_ratio = _normalize_aspect_ratio(
        aspect_ratio,
        settings.default_aspect_ratio,
    )

    job_id = str(uuid.uuid4())
    input_path = store.save_input(job_id, image.filename, payload)

    job = Job(
        id=job_id,
        status=JobStatus.QUEUED,
        brand_profile=brand_profile,
        brand_profile_version=settings.brand_profile_version,
        aspect_ratio=normalized_aspect_ratio,
        preprocessing_enabled=enable_preprocessing,
        input_path=input_path,
        quality_score=precheck.score,
        precheck_data=precheck.as_dict(),
        identity_threshold=settings.identity_threshold_default,
        brand_threshold=settings.brand_threshold_default,
        approved_variant_id=None,
        model_version=settings.model_version,
        error_message=None,
        started_at=None,
        finished_at=None,
    )
    session.add(job)
    log_audit_event(
        session,
        action="job_created",
        actor=actor,
        details={
            "job_id": job.id,
            "brand_profile": brand_profile,
            "aspect_ratio": normalized_aspect_ratio,
            "preprocessing_enabled": enable_preprocessing,
            "face_detector_provider": precheck.face_detector_provider,
            "face_count": precheck.face_count,
        },
        job_id=job.id,
    )
    session.commit()
    session.refresh(job)

    try:
        queue.enqueue_job(job.id)
    except Exception as exc:  # pragma: no cover - infrastructure failure branch
        job.status = JobStatus.FAILED
        job.error_message = f"queue enqueue failed: {exc}"
        log_audit_event(
            session,
            action="job_queue_failed",
            actor=actor,
            details={"job_id": job.id, "error": str(exc)[:500]},
            job_id=job.id,
        )
        session.commit()
        raise HTTPException(
            status_code=503,
            detail="job was created but could not be queued",
        ) from exc

    log_audit_event(
        session,
        action="job_queued",
        actor=actor,
        details={"job_id": job.id, "queue": settings.queue_name},
        job_id=job.id,
    )
    session.commit()
    return JobCreateResponse(
        job=JobRead.model_validate(job),
        queue_name=settings.queue_name,
        message="job queued",
    )


@router.get("/{job_id}", response_model=JobRead)
def get_job_status(
    job_id: str,
    _: Actor = Depends(require_actor_roles("editor", "brand_owner", "admin")),
    session: Session = Depends(get_db_session),
) -> JobRead:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobRead.model_validate(job)


@router.get("/{job_id}/variants", response_model=list[VariantRead])
def get_job_variants(
    job_id: str,
    _: Actor = Depends(require_actor_roles("editor", "brand_owner", "admin")),
    session: Session = Depends(get_db_session),
) -> list[VariantRead]:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return [VariantRead.model_validate(variant) for variant in list_variants(session, job_id)]


@router.post("/{job_id}/approve", response_model=ApproveVariantResponse)
def approve_variant(
    job_id: str,
    payload: ApproveVariantRequest,
    actor: Actor = Depends(require_actor_roles("editor", "brand_owner", "admin")),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_runtime_settings),
) -> ApproveVariantResponse:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")

    variant = get_variant(session, payload.variant_id)
    if variant is None or variant.job_id != job_id:
        raise HTTPException(status_code=404, detail="variant not found for this job")

    approval = get_actor_approval(session, job_id=job.id, actor_id=actor.actor_id)
    if approval is None:
        approval = JobApproval(
            id=str(uuid.uuid4()),
            job_id=job.id,
            variant_id=variant.id,
            actor_id=actor.actor_id,
            actor_role=actor.role,
        )
        session.add(approval)
    else:
        approval.variant_id = variant.id
        approval.actor_role = actor.role

    session.flush()
    approvals = list_approvals(session, job.id)
    fully_approved = _is_variant_fully_approved(
        settings=settings,
        approvals=approvals,
        variant_id=variant.id,
        actor=actor,
    )
    if fully_approved:
        for candidate in list_variants(session, job_id):
            candidate.is_approved = candidate.id == variant.id
        job.approved_variant_id = variant.id
    else:
        if job.approved_variant_id is None:
            for candidate in list_variants(session, job_id):
                candidate.is_approved = False

    log_audit_event(
        session,
        action="variant_approval_submitted",
        actor=actor,
        details={
            "job_id": job.id,
            "variant_id": variant.id,
            "approval_mode": settings.approval_mode,
            "fully_approved_after_submission": fully_approved,
        },
        job_id=job.id,
    )
    if fully_approved:
        log_audit_event(
            session,
            action="variant_fully_approved",
            actor=actor,
            details={
                "job_id": job.id,
                "variant_id": variant.id,
                "approval_mode": settings.approval_mode,
            },
            job_id=job.id,
        )

    session.commit()
    session.refresh(variant)
    approvals = list_approvals(session, job.id)
    return ApproveVariantResponse(
        variant=VariantRead.model_validate(variant),
        approval_state=_build_approval_state(
            settings=settings,
            job=job,
            variant_id=variant.id,
            approvals=approvals,
        ),
    )


@router.get("/{job_id}/audit", response_model=list[AuditEventRead])
def get_job_audit_events(
    job_id: str,
    _: Actor = Depends(require_actor_roles("admin", "editor")),
    session: Session = Depends(get_db_session),
) -> list[AuditEventRead]:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return [AuditEventRead.model_validate(event) for event in list_audit_events(session, job_id)]


@router.get("/{job_id}/export", response_model=ExportResponse)
def export_job(
    job_id: str,
    actor: Actor = Depends(get_current_actor),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_runtime_settings),
    store: ArtifactStore = Depends(get_artifact_store),
) -> ExportResponse:
    job = get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.approved_variant_id is None:
        raise HTTPException(status_code=409, detail="approve a variant before export")

    approved = get_variant(session, job.approved_variant_id)
    if approved is None:
        raise HTTPException(status_code=409, detail="approved variant is missing")

    export_paths = store.build_exports(
        job_id=job.id,
        source_relative_path=approved.image_path,
        web_size=settings.export_web_size,
        print_size=settings.export_print_size,
    )

    metadata = {
        "job_id": job.id,
        "seed": approved.seed,
        "model_version": job.model_version,
        "brand_profile_version": job.brand_profile_version,
        "created_at": job.created_at.isoformat(),
        "approved_variant_id": approved.id,
        "generation_meta": approved.generation_meta,
    }
    log_audit_event(
        session,
        action="job_exported",
        actor=actor,
        details={
            "job_id": job.id,
            "approved_variant_id": approved.id,
            "web_path": export_paths["web_path"],
            "print_path": export_paths["print_path"],
        },
        job_id=job.id,
    )
    session.commit()
    return ExportResponse(
        job_id=job.id,
        approved_variant_id=approved.id,
        web_url=store.to_public_url(export_paths["web_path"]),
        print_url=store.to_public_url(export_paths["print_path"]),
        metadata=metadata,
    )
