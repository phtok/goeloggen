# Portrait Brand Generator (MVP Core)

FastAPI + Redis + Worker implementation for brand-consistent portrait generation.

## Included in this implementation

- API endpoints:
  - `POST /v1/jobs`
  - `GET /v1/jobs/{job_id}`
  - `GET /v1/jobs/{job_id}/variants`
  - `POST /v1/jobs/{job_id}/approve`
  - `GET /v1/jobs/{job_id}/audit`
  - `GET /v1/jobs/{job_id}/export`
- Production-ready control points:
  - API key auth (`X-API-Key`) with role checks (`editor`, `brand_owner`, `admin`)
  - audit event logging for create/queue/approve/export/worker stages
  - single- and double-approval mode (`APPROVAL_MODE=single|double`)
- Face validation:
  - face detection provider modes (`opencv`, `insightface`, `stub`)
  - hard single-face gate at upload time
- Inference modes:
  - `stub` mode (deterministic local fallback)
  - `diffusers` mode (SDXL img2img + optional LoRA + optional FaceID adapter)
- Storage modes:
  - `local` artifacts
  - `r2` artifacts with local cache + upload sync + URL generation
- PostgreSQL-backed models for jobs, variants, approvals, and audit events.

## Quick start (Docker)

```bash
cd /Users/philipptok/goeloggen/services/brand-portrait
cp .env.example .env
docker compose up --build
```

API docs:

- [http://localhost:8000/docs](http://localhost:8000/docs)

## Local start (without Docker)

```bash
cd /Users/philipptok/goeloggen/services/brand-portrait
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd /Users/philipptok/goeloggen/services/brand-portrait
source .venv/bin/activate
python -m app.worker.main
```

## Install optional feature packs

Face detection providers:

```bash
pip install -e ".[vision]"
```

Diffusers inference:

```bash
pip install -e ".[ml]"
```

All optional packages:

```bash
pip install -e ".[dev,vision,ml]"
```

## API usage examples

Create a job:

```bash
curl -sS -X POST "http://localhost:8000/v1/jobs" \
  -H "X-API-Key: dev-editor-key" \
  -F "image=@/absolute/path/to/portrait.jpg" \
  -F "brand_profile=goe_brand_v1" \
  -F "aspect_ratio=4:5" \
  -F "enable_preprocessing=true"
```

Approve a variant:

```bash
curl -sS -X POST "http://localhost:8000/v1/jobs/<job_id>/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-editor-key" \
  -d '{"variant_id":"<variant_id>"}'
```

In `APPROVAL_MODE=double`, add a second approval from a brand owner key:

```bash
curl -sS -X POST "http://localhost:8000/v1/jobs/<job_id>/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-brand-key" \
  -d '{"variant_id":"<variant_id>"}'
```

Export approved output:

```bash
curl -sS "http://localhost:8000/v1/jobs/<job_id>/export" \
  -H "X-API-Key: dev-editor-key"
```

## Key configuration switches

- `FACE_DETECTOR_MODE=opencv|insightface|stub`
- `INFERENCE_BACKEND=stub|diffusers`
- `INFERENCE_FALLBACK_TO_STUB=true|false`
- `STORAGE_BACKEND=local|r2`
- `APPROVAL_MODE=single|double`
- `AUTH_ENABLED=true|false`

## Notes and boundaries

- `diffusers` mode requires model access and GPU sizing outside this repository.
- `insightface` provider may require additional runtime data/model downloads.
- R2 URLs are generated from `R2_PUBLIC_BASE_URL` if set, otherwise via presigned URLs.
