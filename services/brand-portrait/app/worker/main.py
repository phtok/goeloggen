from __future__ import annotations

import time
import traceback

from app.core.settings import get_settings
from app.db.base import Base, utcnow
from app.db.session import SessionLocal, engine
from app.models import JobStatus
from app.repositories.jobs import get_job
from app.services.audit import log_audit_event
from app.services.auth import Actor
from app.services.inference import build_inference_adapter
from app.services.pipeline import process_job
from app.services.queue import QueueClient
from app.services.storage import ArtifactStore


def run_worker_loop() -> None:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)

    queue = QueueClient(redis_url=settings.redis_url, queue_name=settings.queue_name)
    store = ArtifactStore(
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
    inference_adapter = build_inference_adapter(settings)
    system_actor = Actor(actor_id="worker", role="system")

    print(f"[worker] started queue={settings.queue_name}")
    while True:
        job_id = queue.dequeue_job(timeout_seconds=5)
        if not job_id:
            continue

        with SessionLocal() as session:
            job = get_job(session, job_id)
            if job is None:
                print(f"[worker] skipping unknown job={job_id}")
                continue
            if job.status == JobStatus.DONE:
                print(f"[worker] skipping already completed job={job_id}")
                continue

            try:
                job.status = JobStatus.RUNNING
                job.started_at = utcnow()
                job.error_message = None
                log_audit_event(
                    session,
                    action="job_processing_started",
                    actor=system_actor,
                    details={"job_id": job.id},
                    job_id=job.id,
                )
                session.commit()

                process_job(
                    session=session,
                    settings=settings,
                    store=store,
                    inference_adapter=inference_adapter,
                    job=job,
                )
                log_audit_event(
                    session,
                    action="job_processing_completed",
                    actor=system_actor,
                    details={"job_id": job.id},
                    job_id=job.id,
                )
                session.commit()
                print(f"[worker] completed job={job_id}")
            except Exception as exc:  # pragma: no cover - runtime failure branch
                session.rollback()
                if job is not None:
                    job.status = JobStatus.FAILED
                    job.finished_at = utcnow()
                    job.error_message = str(exc)[:500]
                    log_audit_event(
                        session,
                        action="job_processing_failed",
                        actor=system_actor,
                        details={"job_id": job.id, "error": str(exc)[:500]},
                        job_id=job.id,
                    )
                    session.commit()
                print(f"[worker] failed job={job_id} error={exc}")
                traceback.print_exc()
                time.sleep(0.1)


if __name__ == "__main__":
    run_worker_loop()
