import rq
from redis import Redis
from typing import Optional
from config import settings
from background.metrics import JOBS_ENQUEUED
import rq as rq_module


_conn: Optional[Redis] = None


def get_redis_conn() -> Redis:
    global _conn
    if _conn is None:
        _conn = Redis.from_url(settings.redis_url)
    return _conn


def get_queue(name: str = "default") -> rq.Queue:
    return rq.Queue(name, connection=get_redis_conn())


def enqueue(func, *args, job_timeout=None, retry=None, on_success=None, on_failure=None, **kwargs):
    """Enqueue a job and return the job id.

    `func` can be a callable or an import string. Optionally provide
    `on_success` and `on_failure` as import strings or callables.
    Returns job id string.
    """
    if retry is None:
        # sensible default: 3 retries with backoff intervals
        retry = rq_module.Retry(max=3, interval=[10, 30, 60])

    q = get_queue()
    job = q.enqueue(func, *args, job_timeout=job_timeout, retry=retry, on_success=on_success, on_failure=on_failure, **kwargs)
    try:
        JOBS_ENQUEUED.inc()
    except Exception:
        pass
    return job.id
from redis import Redis
from rq import Queue
from config import settings


_redis = Redis.from_url(settings.redis_url)
queue = Queue("default", connection=_redis)


def enqueue_ingestion(job_func, *args, **kwargs):
    """Enqueue a callable with given args on the default queue."""
    return queue.enqueue(job_func, *args, **kwargs)
