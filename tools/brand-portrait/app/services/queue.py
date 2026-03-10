from __future__ import annotations

import redis


class QueueClient:
    def __init__(self, redis_url: str, queue_name: str) -> None:
        self.queue_name = queue_name
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

    def enqueue_job(self, job_id: str) -> None:
        self.client.rpush(self.queue_name, job_id)

    def dequeue_job(self, timeout_seconds: int = 5) -> str | None:
        item = self.client.blpop(self.queue_name, timeout=timeout_seconds)
        if item is None:
            return None
        return item[1]
