from __future__ import annotations

import io
import math
import uuid
from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageEnhance, ImageOps
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.db.base import utcnow
from app.models import Job, JobStatus, Variant
from app.repositories.jobs import clear_job_variants
from app.services.brand_profile import load_brand_profile
from app.services.inference import BaseInferenceAdapter
from app.services.storage import ArtifactStore


@dataclass
class VariantScore:
    identity_score: float
    brand_score: float
    quality_flags: dict[str, Any]


def _parse_aspect_ratio(aspect_ratio: str) -> tuple[int, int]:
    parts = aspect_ratio.split(":")
    if len(parts) != 2:
        return 4, 5
    width, height = int(parts[0]), int(parts[1])
    if width <= 0 or height <= 0:
        return 4, 5
    return width, height


def _enforce_aspect_ratio(image: Image.Image, aspect_ratio: str) -> Image.Image:
    width, height = image.size
    ratio_w, ratio_h = _parse_aspect_ratio(aspect_ratio)
    target_ratio = ratio_w / ratio_h
    source_ratio = width / height

    if source_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        box = (left, 0, left + new_width, height)
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        box = (0, top, width, top + new_height)
    return image.crop(box)


def _apply_preprocessing(image: Image.Image, enabled: bool) -> Image.Image:
    if not enabled:
        return image
    preprocessed = ImageOps.autocontrast(image)
    preprocessed = ImageEnhance.Sharpness(preprocessed).enhance(1.12)
    return preprocessed


def _apply_brand_lock(image: Image.Image, palette: list[str]) -> Image.Image:
    styled = image.convert("RGB")
    styled = ImageEnhance.Contrast(styled).enhance(1.03)
    styled = ImageEnhance.Color(styled).enhance(0.96)

    # Warm tone overlay derived from brand palette.
    overlay_color = palette[0] if palette else "#D9C7A1"
    overlay = Image.new("RGB", styled.size, overlay_color)
    styled = Image.blend(styled, overlay, alpha=0.08)
    return styled


def _rgb_histogram_similarity(image_a: Image.Image, image_b: Image.Image) -> float:
    hist_a = image_a.convert("RGB").histogram()
    hist_b = image_b.convert("RGB").histogram()
    numerator = sum(a * b for a, b in zip(hist_a, hist_b))
    norm_a = math.sqrt(sum(a * a for a in hist_a))
    norm_b = math.sqrt(sum(b * b for b in hist_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, numerator / (norm_a * norm_b)))


def _hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    raw = hex_value.lstrip("#")
    if len(raw) != 6:
        return (217, 199, 161)
    return (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16))


def _brand_palette_match_score(image: Image.Image, palette: list[str]) -> float:
    if not palette:
        return 0.5
    resized = image.convert("RGB").resize((64, 64), resample=Image.Resampling.BILINEAR)
    pixels = list(resized.getdata())
    mean_r = sum(pixel[0] for pixel in pixels) / len(pixels)
    mean_g = sum(pixel[1] for pixel in pixels) / len(pixels)
    mean_b = sum(pixel[2] for pixel in pixels) / len(pixels)
    target_r, target_g, target_b = _hex_to_rgb(palette[0])
    distance = math.sqrt(
        (mean_r - target_r) ** 2 + (mean_g - target_g) ** 2 + (mean_b - target_b) ** 2
    )
    max_distance = math.sqrt(255**2 * 3)
    score = 1.0 - (distance / max_distance)
    return max(0.0, min(1.0, score))


def _compute_scores(
    source_image: Image.Image,
    candidate_image: Image.Image,
    palette: list[str],
    thresholds: tuple[float, float],
) -> VariantScore:
    identity_threshold, brand_threshold = thresholds
    hist_similarity = _rgb_histogram_similarity(source_image, candidate_image)
    identity_score = round(0.65 + hist_similarity * 0.35, 3)
    brand_score = round(_brand_palette_match_score(candidate_image, palette), 3)

    flags: dict[str, Any] = {
        "identity_gate_passed": identity_score >= identity_threshold,
        "brand_gate_passed": brand_score >= brand_threshold,
    }
    if identity_score < identity_threshold:
        flags["identity_warning"] = "identity_score_below_threshold"
    if brand_score < brand_threshold:
        flags["brand_warning"] = "brand_score_below_threshold"

    return VariantScore(
        identity_score=identity_score,
        brand_score=brand_score,
        quality_flags=flags,
    )


def process_job(
    session: Session,
    settings: Settings,
    store: ArtifactStore,
    inference_adapter: BaseInferenceAdapter,
    job: Job,
) -> None:
    brand_profile = load_brand_profile(settings, job.brand_profile)
    input_payload = store.read_bytes(job.input_path)
    with Image.open(io.BytesIO(input_payload)) as original:
        source = original.convert("RGB")

    working = _apply_preprocessing(source, job.preprocessing_enabled)
    cropped = _enforce_aspect_ratio(working, job.aspect_ratio)
    final_base = cropped.resize((1200, 1500), resample=Image.Resampling.LANCZOS)

    generated_variants = inference_adapter.generate_variants(
        source_image=final_base,
        brand_profile=brand_profile,
        job_id=job.id,
        num_variants=settings.variants_per_job,
    )
    if not generated_variants:
        raise RuntimeError("inference produced no variants")

    clear_job_variants(session, job.id)

    palette = brand_profile.get("palette", [])
    for variant_index, generated in enumerate(generated_variants):
        styled = _apply_brand_lock(generated.image, palette)
        relative_path = store.save_variant(job.id, variant_index + 1, styled)
        score = _compute_scores(
            source_image=final_base,
            candidate_image=styled,
            palette=palette,
            thresholds=(job.identity_threshold, job.brand_threshold),
        )
        session.add(
            Variant(
                id=str(uuid.uuid4()),
                job_id=job.id,
                variant_index=variant_index + 1,
                image_path=relative_path,
                seed=generated.seed,
                generation_meta=generated.metadata,
                identity_score=score.identity_score,
                brand_score=score.brand_score,
                quality_flags=score.quality_flags,
                is_approved=False,
            )
        )

    job.model_version = f"{inference_adapter.backend_name}:{settings.model_version}"
    job.status = JobStatus.DONE
    job.finished_at = utcnow()
    job.error_message = None
    session.commit()
