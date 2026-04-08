def test_list_anomalies(app_client):
    response = app_client.get("/api/anomalies")

    assert response.status_code == 200
    assert response.json() == {"anomalies": []}


def test_resolve_anomaly(app_client):
    response = app_client.patch("/api/anomalies/5/resolve")

    assert response.status_code == 200
    assert response.json() == {"id": 5, "resolved": True}
