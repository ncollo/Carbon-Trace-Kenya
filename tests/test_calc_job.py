from types import SimpleNamespace

import ghg_engine.calc_job as calc_job


def test_perform_calculation_returns_result(monkeypatch):
    monkeypatch.setattr(calc_job, "get_current_job", lambda: None)
    monkeypatch.setattr(calc_job.time, "sleep", lambda _: None)

    result = calc_job.perform_calculation(42)

    assert result == {"company_id": 42, "emissions": 123.45}


def test_perform_calculation_records_db_status(monkeypatch):
    job = SimpleNamespace(id="job-123")
    updates = []

    monkeypatch.setattr(calc_job, "get_current_job", lambda: job)
    monkeypatch.setattr(calc_job.time, "sleep", lambda _: None)

    def fake_update(rq_job_id, **fields):
        updates.append((rq_job_id, fields))

    monkeypatch.setattr(calc_job, "_update_job_record", fake_update)

    result = calc_job.perform_calculation(7)

    assert result == {"company_id": 7, "emissions": 123.45}
    assert any(fields.get("status") == "finished" for _, fields in updates)
