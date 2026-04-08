from types import SimpleNamespace
from unittest.mock import MagicMock

import background.handlers as handlers


def _mock_session(job_record):
    session = MagicMock()
    session.query.return_value.filter.return_value.one_or_none.return_value = job_record
    return session


def test_job_success_updates_status(monkeypatch):
    record = SimpleNamespace(status=None, result=None)
    session = _mock_session(record)
    monkeypatch.setattr(handlers, "SessionLocal", lambda: session)

    job = SimpleNamespace(id="job-1", enqueued_at=None, ended_at=None)

    handlers.job_success(job, None, {"ok": True})

    assert record.status == "finished"
    assert record.result == {"ok": True}


def test_job_failure_updates_status(monkeypatch):
    record = SimpleNamespace(status=None, result=None)
    session = _mock_session(record)
    monkeypatch.setattr(handlers, "SessionLocal", lambda: session)

    job = SimpleNamespace(id="job-1")

    handlers.job_failure(job, None, Exception, ValueError("boom"), None)

    assert record.status == "failed"
    assert record.result == {"error": "boom"}


def test_job_success_no_matching_record(monkeypatch):
    session = _mock_session(None)
    monkeypatch.setattr(handlers, "SessionLocal", lambda: session)

    job = SimpleNamespace(id="job-1", enqueued_at=None, ended_at=None)

    handlers.job_success(job, None, {"ok": True})
