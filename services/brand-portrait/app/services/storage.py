from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


def parse_size(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {value}")
    width, height = int(parts[0]), int(parts[1])
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid size values: {value}")
    return width, height


class ArtifactStore:
    def __init__(
        self,
        *,
        root: Path,
        public_base_url: str,
        backend: str = "local",
        r2_bucket: str = "",
        r2_endpoint_url: str = "",
        r2_region: str = "auto",
        r2_access_key_id: str = "",
        r2_secret_access_key: str = "",
        r2_prefix: str = "portrait-generator",
        r2_public_base_url: str = "",
        r2_signed_url_expiry_seconds: int = 3600,
    ) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.public_base_url = public_base_url.rstrip("/")
        self.backend = backend.strip().lower()
        self.r2_bucket = r2_bucket
        self.r2_prefix = r2_prefix.strip("/")
        self.r2_public_base_url = r2_public_base_url.rstrip("/")
        self.r2_signed_url_expiry_seconds = r2_signed_url_expiry_seconds

        self.s3_client = None
        if self.backend == "r2":
            try:
                import boto3  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency branch
                raise RuntimeError("storage backend 'r2' requires boto3") from exc
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=r2_endpoint_url,
                region_name=r2_region,
                aws_access_key_id=r2_access_key_id,
                aws_secret_access_key=r2_secret_access_key,
            )

    def _safe_abs_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if not str(candidate).startswith(str(self.root)):
            raise ValueError("Unsafe artifact path")
        return candidate

    def _object_key(self, relative_path: str) -> str:
        clean_relative = relative_path.lstrip("/")
        if self.r2_prefix:
            return f"{self.r2_prefix}/{clean_relative}"
        return clean_relative

    def _content_type_for_path(self, relative_path: str) -> str:
        suffix = Path(relative_path).suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if suffix == ".png":
            return "image/png"
        if suffix == ".webp":
            return "image/webp"
        if suffix == ".json":
            return "application/json"
        return "application/octet-stream"

    def _upload_if_r2(self, relative_path: str, payload: bytes) -> None:
        if self.backend != "r2" or self.s3_client is None:
            return
        self.s3_client.put_object(
            Bucket=self.r2_bucket,
            Key=self._object_key(relative_path),
            Body=payload,
            ContentType=self._content_type_for_path(relative_path),
        )

    def _download_if_r2(self, relative_path: str) -> bytes | None:
        if self.backend != "r2" or self.s3_client is None:
            return None
        try:
            response = self.s3_client.get_object(
                Bucket=self.r2_bucket,
                Key=self._object_key(relative_path),
            )
            return response["Body"].read()
        except Exception:
            return None

    def resolve(self, relative_path: str) -> Path:
        destination = self._safe_abs_path(relative_path)
        if destination.exists():
            return destination
        downloaded = self._download_if_r2(relative_path)
        if downloaded is None:
            raise FileNotFoundError(f"artifact not found: {relative_path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(downloaded)
        return destination

    def read_bytes(self, relative_path: str) -> bytes:
        return self.resolve(relative_path).read_bytes()

    def save_input(self, job_id: str, original_filename: str, payload: bytes) -> str:
        suffix = Path(original_filename or "").suffix.lower() or ".jpg"
        relative = Path("inputs") / job_id / f"input{suffix}"
        destination = self._safe_abs_path(relative.as_posix())
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        self._upload_if_r2(relative.as_posix(), payload)
        return relative.as_posix()

    def save_variant(self, job_id: str, variant_index: int, image: Image.Image) -> str:
        relative = Path("outputs") / job_id / f"variant_{variant_index:02d}.jpg"
        destination = self._safe_abs_path(relative.as_posix())
        destination.parent.mkdir(parents=True, exist_ok=True)
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="JPEG", quality=95, optimize=True)
        payload = buffer.getvalue()
        destination.write_bytes(payload)
        self._upload_if_r2(relative.as_posix(), payload)
        return relative.as_posix()

    def build_exports(
        self,
        *,
        job_id: str,
        source_relative_path: str,
        web_size: str,
        print_size: str,
    ) -> dict[str, Any]:
        source_payload = self.read_bytes(source_relative_path)
        with Image.open(io.BytesIO(source_payload)) as image:
            source = image.convert("RGB")
            web = ImageOps.fit(source, parse_size(web_size), method=Image.Resampling.LANCZOS)
            print_img = ImageOps.fit(
                source,
                parse_size(print_size),
                method=Image.Resampling.LANCZOS,
            )

        export_dir = Path("exports") / job_id
        web_relative = export_dir / "web.jpg"
        print_relative = export_dir / "print.png"

        web_abs = self._safe_abs_path(web_relative.as_posix())
        print_abs = self._safe_abs_path(print_relative.as_posix())
        web_abs.parent.mkdir(parents=True, exist_ok=True)

        web_buffer = io.BytesIO()
        print_buffer = io.BytesIO()
        web.save(web_buffer, format="JPEG", quality=95, optimize=True)
        print_img.save(print_buffer, format="PNG", optimize=True)
        web_payload = web_buffer.getvalue()
        print_payload = print_buffer.getvalue()

        web_abs.write_bytes(web_payload)
        print_abs.write_bytes(print_payload)
        self._upload_if_r2(web_relative.as_posix(), web_payload)
        self._upload_if_r2(print_relative.as_posix(), print_payload)

        return {
            "web_path": web_relative.as_posix(),
            "print_path": print_relative.as_posix(),
        }

    def to_public_url(self, relative_path: str) -> str:
        if self.backend == "r2":
            object_key = self._object_key(relative_path)
            if self.r2_public_base_url:
                return f"{self.r2_public_base_url}/{object_key}"
            if self.s3_client is not None:
                return self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.r2_bucket, "Key": object_key},
                    ExpiresIn=self.r2_signed_url_expiry_seconds,
                )
        return f"{self.public_base_url}/{relative_path.lstrip('/')}"
