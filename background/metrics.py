from prometheus_client import Counter, Histogram

# Web process metrics
JOBS_ENQUEUED = Counter("ctk_jobs_enqueued_total", "Total number of jobs enqueued")

# Worker process metrics (local to worker process)
JOBS_SUCCEEDED = Counter("ctk_jobs_succeeded_total", "Total number of succeeded jobs")
JOBS_FAILED = Counter("ctk_jobs_failed_total", "Total number of failed jobs")
JOB_DURATION_SECONDS = Histogram("ctk_job_duration_seconds", "Job duration in seconds")
