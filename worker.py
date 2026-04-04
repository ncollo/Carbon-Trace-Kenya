from redis import Redis
from rq import Worker, Queue, Connection
from config import settings
import os

# Prometheus metrics for worker process
try:
    from prometheus_client import start_http_server
except Exception:
    start_http_server = None


def run_worker():
    # start metrics HTTP server if available
    port = int(os.getenv("WORKER_METRICS_PORT", "8001"))
    if start_http_server:
        try:
            start_http_server(port)
        except Exception:
            pass

    redis_conn = Redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        qs = ["default"]
        w = Worker(qs)
        w.work()


if __name__ == "__main__":
    run_worker()
"""Run an RQ worker programmatically.

Usage: set `REDIS_URL` or configure `redis_url` in `config.py`, then run:
    python worker.py
"""
from redis import Redis
from rq import Worker, Queue, Connection
from config import settings


listen = ["default"]


def run_worker():
    redis_conn = Redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()


if __name__ == "__main__":
    run_worker()
