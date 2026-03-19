from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.services.auth import Actor


def log_audit_event(
    session: Session,
    *,
    action: str,
    actor: Actor,
    details: dict[str, Any] | None = None,
    job_id: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        id=str(uuid.uuid4()),
        job_id=job_id,
        actor_id=actor.actor_id,
        actor_role=actor.role,
        action=action,
        details=details or {},
    )
    session.add(event)
    return event
