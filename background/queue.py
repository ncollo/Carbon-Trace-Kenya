import rq
from redis import Redis
from typing import Optional
from config import settings


_conn: Optional[Redis] = None


def get_redis_conn() -> Redis:
    global _conn
    if _conn is None:
        _conn = Redis.from_url(settings.redis_url)
    return _conn


def get_queue(name: str = "default") -> rq.Queue:
    return rq.Queue(name, connection=get_redis_conn())


def enqueue(func, *args, job_timeout=None, retry=None, **kwargs):
    """Enqueue a job and return the job id.

    `func` can be a callable or an import string (e.g. "module.sub:fn" or "module.fn").
    `retry` can be an rq.Retry object or None.
    Returns: job id string.
    """
    q = get_queue()
    job = q.enqueue(func, *args, job_timeout=job_timeout, retry=retry, **kwargs)
    return job.id
from redis import Redis
from rq import Queue
from config import settings


_redis = Redis.from_url(settings.redis_url)
queue = Queue("default", connection=_redis)


def enqueue_ingestion(job_func, *args, **kwargs):
    """Enqueue a callable with given args on the default queue."""
    return queue.enqueue(job_func, *args, **kwargs)
