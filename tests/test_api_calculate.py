import jwt

from config import settings


def _auth_headers():
    token = jwt.encode({"sub": "user-1"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"Authorization": f"Bearer {token}"}


def test_calculate_unauthenticated(app_client):
    response = app_client.post("/api/calculate/1")

    assert response.status_code == 401


def test_calculate_authenticated_enqueues_job(app_client, monkeypatch):
    monkeypatch.setattr("api.routers.calculate.enqueue", lambda *args, **kwargs: "job-123")

    response = app_client.post("/api/calculate/1", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json() == {"status": "queued", "company_id": 1, "job_id": "job-123"}
