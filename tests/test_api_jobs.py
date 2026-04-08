from db.models import JobRecord


class FakeJob:
    def __init__(self, status, result=None, exc_info=None):
        self._status = status
        self.result = result
        self.exc_info = exc_info

    def get_status(self):
        return self._status


def test_job_status_not_found(app_client, monkeypatch, mock_redis):
    def raise_not_found(*args, **kwargs):
        raise Exception("missing")

    monkeypatch.setattr("api.routers.jobs.rq.job.Job.fetch", raise_not_found)

    response = app_client.get("/api/jobs/bad-id/status")

    assert response.status_code == 404


def test_job_status_queued(app_client, monkeypatch, mock_redis):
    monkeypatch.setattr(
        "api.routers.jobs.rq.job.Job.fetch",
        lambda *args, **kwargs: FakeJob("queued"),
    )

    response = app_client.get("/api/jobs/job-1/status")

    assert response.status_code == 200
    assert response.json() == {"job_id": "job-1", "status": "queued", "result": None}


def test_job_status_finished(app_client, monkeypatch, mock_redis):
    monkeypatch.setattr(
        "api.routers.jobs.rq.job.Job.fetch",
        lambda *args, **kwargs: FakeJob("finished", result={"ok": True}),
    )

    response = app_client.get("/api/jobs/job-2/status")

    assert response.status_code == 200
    assert response.json() == {"job_id": "job-2", "status": "finished", "result": {"ok": True}}


def test_list_company_jobs(app_client, db_session, monkeypatch, mock_redis):
    record_one = JobRecord(rq_job_id="job-1", company_id=1, task_name="ingest:upload")
    record_two = JobRecord(rq_job_id="job-2", company_id=1, task_name="calculate:full")
    db_session.add_all([record_one, record_two])
    db_session.commit()

    def fake_fetch(job_id, connection=None):
        if job_id == "job-1":
            return FakeJob("finished", result={"status": "ok"})
        return FakeJob("failed", exc_info="boom")

    monkeypatch.setattr("api.routers.jobs.rq.job.Job.fetch", fake_fetch)

    response = app_client.get("/api/companies/1/jobs")

    assert response.status_code == 200
    payload = response.json()
    assert payload["company_id"] == 1
    assert len(payload["jobs"]) == 2
    statuses = {job["rq_job_id"]: job["status"] for job in payload["jobs"]}
    assert statuses["job-1"] == "finished"
    assert statuses["job-2"] == "failed"
