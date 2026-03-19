import pytest
from fastapi import HTTPException

from app.core.settings import Settings
from app.services.auth import resolve_actor_from_api_key


def test_resolve_actor_from_api_key_success() -> None:
    settings = Settings(auth_enabled=True, api_keys={"abc123": "editor"})
    actor = resolve_actor_from_api_key(settings, "abc123")
    assert actor.role == "editor"
    assert actor.actor_id.startswith("key:")


def test_resolve_actor_from_api_key_invalid_key() -> None:
    settings = Settings(auth_enabled=True, api_keys={"abc123": "editor"})
    with pytest.raises(HTTPException) as exc:
        resolve_actor_from_api_key(settings, "wrong")
    assert exc.value.status_code == 401
