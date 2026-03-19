from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portrait Brand Generator API"
    app_env: str = "dev"
    api_port: int = 8000

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/portrait_generator"
    )
    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "portrait_jobs"

    storage_backend: str = "local"
    storage_root: Path = Field(default=Path("data/storage"))
    storage_public_base_url: str = "/artifacts"
    r2_bucket: str = ""
    r2_endpoint_url: str = ""
    r2_region: str = "auto"
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_prefix: str = "portrait-generator"
    r2_public_base_url: str = ""
    r2_signed_url_expiry_seconds: int = 3600
    max_upload_mb: int = 20
    raw_image_retention_days: int = 30
    default_aspect_ratio: str = "4:5"
    variants_per_job: int = 3

    identity_threshold_default: float = 0.80
    brand_threshold_default: float = 0.85
    approval_mode: str = "single"

    auth_enabled: bool = True
    api_keys: dict[str, str] = Field(
        default_factory=lambda: {
            "dev-editor-key": "editor",
            "dev-brand-key": "brand_owner",
            "dev-admin-key": "admin",
        }
    )

    model_version: str = "sdxl_stub_v1"
    brand_profile_version: str = "goe_brand_v1"
    brand_profiles_dir: Path = Field(default=Path("config/brand_profiles"))
    face_detector_mode: str = "opencv"
    face_detector_min_confidence: float = 0.50

    inference_backend: str = "stub"
    inference_fallback_to_stub: bool = True
    diffusers_base_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    diffusers_refiner_model: str = ""
    diffusers_device: str = "cuda"
    diffusers_dtype: str = "float16"
    diffusers_num_inference_steps: int = 35
    diffusers_guidance_scale: float = 6.5
    diffusers_strength: float = 0.42
    diffusers_lora_path: str = ""
    diffusers_lora_scale: float = 0.8
    faceid_adapter_path: str = ""
    faceid_adapter_subfolder: str = ""
    faceid_weight_name: str = ""
    faceid_enabled: bool = True

    export_web_size: str = "1200x1500"
    export_print_size: str = "3000x3750"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    settings.brand_profiles_dir.mkdir(parents=True, exist_ok=True)
    return settings
