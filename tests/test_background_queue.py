from types import SimpleNamespace
from unittest.mock import MagicMock

import background.queue as queue_module


def test_enqueue_returns_job_id(monkeypatch):
    fake_job = SimpleNamespace(id="abc")

    class FakeQueue:
        def enqueue(self, *args, **kwargs):
            return fake_job

    monkeypatch.setattr(queue_module, "get_queue", lambda name="default": FakeQueue())
    monkeypatch.setattr(queue_module, "JOBS_ENQUEUED", SimpleNamespace(inc=lambda: None))

    assert queue_module.enqueue("task", 1) == "abc"


def test_enqueue_increments_counter(monkeypatch):
    fake_job = SimpleNamespace(id="xyz")

    class FakeQueue:
        def enqueue(self, *args, **kwargs):
            return fake_job

    counter = MagicMock()
    monkeypatch.setattr(queue_module, "get_queue", lambda name="default": FakeQueue())
    monkeypatch.setattr(queue_module, "JOBS_ENQUEUED", counter)

    queue_module.enqueue("task", 1)

    counter.inc.assert_called_once()
