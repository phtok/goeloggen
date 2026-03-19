from functools import lru_cache

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from app.core.settings import Settings, get_settings
from app.services.auth import Actor, require_roles, resolve_actor_from_api_key
from app.services.face_detection import BaseFaceDetector, build_face_detector
from app.services.inference import BaseInferenceAdapter, build_inference_adapter
from app.services.queue import QueueClient
from app.services.storage import ArtifactStore

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_runtime_settings() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_queue_client() -> QueueClient:
    settings = get_settings()
    return QueueClient(redis_url=settings.redis_url, queue_name=settings.queue_name)


@lru_cache(maxsize=1)
def get_artifact_store() -> ArtifactStore:
    settings = get_settings()
    return ArtifactStore(
        root=settings.storage_root,
        public_base_url=settings.storage_public_base_url,
        backend=settings.storage_backend,
        r2_bucket=settings.r2_bucket,
        r2_endpoint_url=settings.r2_endpoint_url,
        r2_region=settings.r2_region,
        r2_access_key_id=settings.r2_access_key_id,
        r2_secret_access_key=settings.r2_secret_access_key,
        r2_prefix=settings.r2_prefix,
        r2_public_base_url=settings.r2_public_base_url,
        r2_signed_url_expiry_seconds=settings.r2_signed_url_expiry_seconds,
    )


@lru_cache(maxsize=1)
def get_face_detector() -> BaseFaceDetector:
    settings = get_settings()
    return build_face_detector(settings)


@lru_cache(maxsize=1)
def get_inference_adapter() -> BaseInferenceAdapter:
    settings = get_settings()
    return build_inference_adapter(settings)


def get_current_actor(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_runtime_settings),
) -> Actor:
    return resolve_actor_from_api_key(settings, api_key)


def require_actor_roles(*roles: str):
    def dependency(actor: Actor = Depends(get_current_actor)) -> Actor:
        require_roles(actor, roles)
        return actor

    return dependency
