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


def enqueue(func, *args, **kwargs):
    q = get_queue()
    return q.enqueue(func, *args, **kwargs)
from redis import Redis
from rq import Queue
from config import settings


_redis = Redis.from_url(settings.redis_url)
queue = Queue("default", connection=_redis)


def enqueue_ingestion(job_func, *args, **kwargs):
    """Enqueue a callable with given args on the default queue."""
    return queue.enqueue(job_func, *args, **kwargs)
