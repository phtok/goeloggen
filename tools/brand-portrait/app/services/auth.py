from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from fastapi import HTTPException, status

from app.core.settings import Settings


@dataclass(frozen=True)
class Actor:
    actor_id: str
    role: str


ALLOWED_ROLES = {"editor", "brand_owner", "admin", "system"}


def resolve_actor_from_api_key(settings: Settings, api_key: str | None) -> Actor:
    if not settings.auth_enabled:
        return Actor(actor_id="auth-disabled", role="admin")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing API key",
        )

    role = settings.api_keys.get(api_key)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid API key",
        )
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"configured role '{role}' is not supported",
        )
    key_fingerprint = hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]
    return Actor(actor_id=f"key:{key_fingerprint}", role=role)


def require_roles(actor: Actor, allowed_roles: Iterable[str]) -> None:
    allowed = set(allowed_roles)
    if actor.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"required roles: {sorted(allowed)}",
        )
