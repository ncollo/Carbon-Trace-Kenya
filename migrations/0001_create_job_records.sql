-- SQL migration: create job_records table

CREATE TABLE IF NOT EXISTS job_records (
    id SERIAL PRIMARY KEY,
    rq_job_id VARCHAR(255) NOT NULL UNIQUE,
    company_id INTEGER,
    task_name VARCHAR(255),
    enqueued_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    finished_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50),
    result JSONB
);
