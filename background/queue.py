import sys
from redis import Redis
from typing import Optional
from config import settings

# Conditional RQ import - RQ requires Unix 'fork' which doesn't exist on Windows
_rq_available = False
_conn: Optional[Redis] = None

try:
    import rq
    import rq as rq_module
    _rq_available = True
except (ImportError, ValueError):
    # ValueError: cannot find context for 'fork' (Windows)
    # ImportError: rq not installed (fallback)
    pass


def get_redis_conn() -> Redis:
    global _conn
    if _conn is None:
        _conn = Redis.from_url(settings.redis_url)
    return _conn


def get_queue(name: str = "default"):
    """Get RQ queue or raise error if not available"""
    if not _rq_available:
        raise RuntimeError(
            "RQ is not available on Windows. "
            "Background jobs are disabled. "
            "Run the application on Unix/Linux for full functionality."
        )
    return rq.Queue(name, connection=get_redis_conn())


def enqueue(func, *args, job_timeout=None, retry=None, on_success=None, on_failure=None, **kwargs):
    """Enqueue a job and return the job id.

    If RQ is not available (Windows), returns a mock job ID.
    `func` can be a callable or an import string. Optionally provide
    `on_success` and `on_failure` as import strings or callables.
    Returns job id string.
    """
    if not _rq_available:
        # Return a mock job ID for Windows development
        import uuid
        return str(uuid.uuid4())
    
    if retry is None:
        # sensible default: 3 retries with backoff intervals
        retry = rq_module.Retry(max=3, interval=[10, 30, 60])

    q = get_queue()
    job = q.enqueue(func, *args, job_timeout=job_timeout, retry=retry, on_success=on_success, on_failure=on_failure, **kwargs)
    try:
        from background.metrics import JOBS_ENQUEUED
        JOBS_ENQUEUED.inc()
    except Exception:
        pass
    return job.id


def enqueue_ingestion(job_func, *args, **kwargs):
    """Enqueue a callable with given args on the default queue."""
    return queue.enqueue(job_func, *args, **kwargs)
