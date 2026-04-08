def test_get_report_pdf(app_client):
    response = app_client.get("/api/reports/7/pdf")

    assert response.status_code == 200
    assert response.json() == {"id": 7, "format": "pdf", "url": "/downloads/7.pdf"}


def test_get_report_xbrl(app_client):
    response = app_client.get("/api/reports/7/xbrl")

    assert response.status_code == 200
    assert response.json() == {"id": 7, "format": "xbrl", "url": "/downloads/7.xbrl"}
