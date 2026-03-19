import json
from pathlib import Path
from typing import Any

from app.core.settings import Settings


def load_brand_profile(settings: Settings, profile_id: str) -> dict[str, Any]:
    profile_path = settings.brand_profiles_dir / f"{profile_id}.json"
    if not profile_path.exists():
        raise FileNotFoundError(f"Brand profile not found: {profile_path}")
    return json.loads(profile_path.read_text(encoding="utf-8"))


def list_brand_profiles(settings: Settings) -> list[str]:
    profile_ids: list[str] = []
    for path in sorted(Path(settings.brand_profiles_dir).glob("*.json")):
        profile_ids.append(path.stem)
    return profile_ids
