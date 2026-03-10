from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageEnhance

from app.core.settings import Settings


@dataclass
class GenerationResult:
    image: Image.Image
    seed: int
    metadata: dict[str, Any]


class BaseInferenceAdapter:
    backend_name = "base"

    def generate_variants(
        self,
        *,
        source_image: Image.Image,
        brand_profile: dict[str, Any],
        job_id: str,
        num_variants: int,
    ) -> list[GenerationResult]:
        raise NotImplementedError


class StubInferenceAdapter(BaseInferenceAdapter):
    backend_name = "stub"

    def _seed_for(self, job_id: str, variant_index: int) -> int:
        digest = hashlib.sha256(f"{job_id}:{variant_index}".encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def generate_variants(
        self,
        *,
        source_image: Image.Image,
        brand_profile: dict[str, Any],
        job_id: str,
        num_variants: int,
    ) -> list[GenerationResult]:
        outputs: list[GenerationResult] = []
        palette = brand_profile.get("palette", [])
        overlay_color = palette[0] if palette else "#D9C7A1"

        for variant_index in range(num_variants):
            seed = self._seed_for(job_id, variant_index)
            image = source_image.convert("RGB")
            image = ImageEnhance.Brightness(image).enhance([1.02, 0.98, 1.00][variant_index % 3])
            image = ImageEnhance.Contrast(image).enhance([1.04, 1.01, 1.06][variant_index % 3])
            image = ImageEnhance.Color(image).enhance([0.95, 0.90, 0.98][variant_index % 3])
            overlay = Image.new("RGB", image.size, overlay_color)
            image = Image.blend(image, overlay, alpha=0.08)
            outputs.append(
                GenerationResult(
                    image=image,
                    seed=seed,
                    metadata={
                        "backend": self.backend_name,
                        "variant_index": variant_index + 1,
                        "faceid_applied": False,
                        "lora_applied": False,
                    },
                )
            )
        return outputs


class DiffusersInferenceAdapter(BaseInferenceAdapter):
    backend_name = "diffusers"

    def __init__(self, settings: Settings) -> None:
        import torch  # type: ignore
        from diffusers import AutoPipelineForImage2Image  # type: ignore

        self.settings = settings
        self.torch = torch
        self.device = (
            "cuda"
            if settings.diffusers_device == "cuda" and torch.cuda.is_available()
            else "cpu"
        )
        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(settings.diffusers_dtype.lower(), torch.float16)
        if self.device == "cpu":
            torch_dtype = torch.float32

        self.pipe = AutoPipelineForImage2Image.from_pretrained(
            settings.diffusers_base_model,
            torch_dtype=torch_dtype,
            use_safetensors=True,
        )
        self.pipe = self.pipe.to(self.device)

        self.lora_applied = False
        if settings.diffusers_lora_path:
            self.pipe.load_lora_weights(settings.diffusers_lora_path)
            if hasattr(self.pipe, "set_adapters"):
                self.pipe.set_adapters(["default"], adapter_weights=[settings.diffusers_lora_scale])
            self.lora_applied = True

        self.faceid_applied = False
        if settings.faceid_enabled and settings.faceid_adapter_path:
            ip_kwargs: dict[str, Any] = {}
            if settings.faceid_adapter_subfolder:
                ip_kwargs["subfolder"] = settings.faceid_adapter_subfolder
            if settings.faceid_weight_name:
                ip_kwargs["weight_name"] = settings.faceid_weight_name
            self.pipe.load_ip_adapter(settings.faceid_adapter_path, **ip_kwargs)
            self.faceid_applied = True

    def _seed_for(self, job_id: str, variant_index: int) -> int:
        digest = hashlib.sha256(f"{job_id}:{variant_index}".encode("utf-8")).hexdigest()
        return int(digest[:8], 16)

    def _build_prompt(self, brand_profile: dict[str, Any], variant_index: int) -> str:
        prompt = brand_profile.get(
            "prompt_template",
            "brand-consistent headshot portrait, studio lighting",
        )
        variations = [
            "neutral expression, centered composition",
            "subtle smile, natural posture",
            "calm expression, slight head angle",
        ]
        return f"{prompt}, {variations[variant_index % len(variations)]}"

    def generate_variants(
        self,
        *,
        source_image: Image.Image,
        brand_profile: dict[str, Any],
        job_id: str,
        num_variants: int,
    ) -> list[GenerationResult]:
        outputs: list[GenerationResult] = []
        negative_prompt = brand_profile.get("negative_prompt", "")
        for variant_index in range(num_variants):
            seed = self._seed_for(job_id, variant_index)
            generator = self.torch.Generator(device=self.device).manual_seed(seed)
            kwargs: dict[str, Any] = {
                "prompt": self._build_prompt(brand_profile, variant_index),
                "negative_prompt": negative_prompt,
                "image": source_image,
                "strength": self.settings.diffusers_strength,
                "guidance_scale": self.settings.diffusers_guidance_scale,
                "num_inference_steps": self.settings.diffusers_num_inference_steps,
                "generator": generator,
            }
            if self.faceid_applied:
                kwargs["ip_adapter_image"] = source_image
            result = self.pipe(**kwargs)
            image = result.images[0].convert("RGB")
            outputs.append(
                GenerationResult(
                    image=image,
                    seed=seed,
                    metadata={
                        "backend": self.backend_name,
                        "variant_index": variant_index + 1,
                        "faceid_applied": self.faceid_applied,
                        "lora_applied": self.lora_applied,
                        "guidance_scale": self.settings.diffusers_guidance_scale,
                        "strength": self.settings.diffusers_strength,
                        "steps": self.settings.diffusers_num_inference_steps,
                    },
                )
            )
        return outputs


def build_inference_adapter(settings: Settings) -> BaseInferenceAdapter:
    backend = settings.inference_backend.strip().lower()
    if backend == "diffusers":
        try:
            return DiffusersInferenceAdapter(settings=settings)
        except Exception:
            if settings.inference_fallback_to_stub:
                return StubInferenceAdapter()
            raise
    return StubInferenceAdapter()
