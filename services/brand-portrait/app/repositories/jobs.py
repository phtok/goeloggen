from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditEvent, Job, JobApproval, Variant


def get_job(session: Session, job_id: str) -> Job | None:
    statement = select(Job).where(Job.id == job_id)
    return session.scalar(statement)


def get_variant(session: Session, variant_id: str) -> Variant | None:
    statement = select(Variant).where(Variant.id == variant_id)
    return session.scalar(statement)


def list_variants(session: Session, job_id: str) -> list[Variant]:
    statement = select(Variant).where(Variant.job_id == job_id).order_by(Variant.variant_index)
    return list(session.scalars(statement))


def clear_job_variants(session: Session, job_id: str) -> None:
    variants = list_variants(session, job_id)
    for variant in variants:
        session.delete(variant)


def list_approvals(session: Session, job_id: str) -> list[JobApproval]:
    statement = (
        select(JobApproval)
        .where(JobApproval.job_id == job_id)
        .order_by(JobApproval.created_at.asc())
    )
    return list(session.scalars(statement))


def get_actor_approval(session: Session, job_id: str, actor_id: str) -> JobApproval | None:
    statement = select(JobApproval).where(
        JobApproval.job_id == job_id,
        JobApproval.actor_id == actor_id,
    )
    return session.scalar(statement)


def list_audit_events(session: Session, job_id: str) -> list[AuditEvent]:
    statement = (
        select(AuditEvent)
        .where(AuditEvent.job_id == job_id)
        .order_by(AuditEvent.created_at.asc())
    )
    return list(session.scalars(statement))
