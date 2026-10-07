from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_job_status_and_progress():
    create_response = client.post(
        "/api/jobs",
        json={
            "event_name": "Progress Test",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "progress@example.com",
                    "certificate_type": "Participation"
                },
                {
                    "name": "Test User 2",
                    "email": "progress2@example.com",
                    "certificate_type": "Participation"
                }
            ]
        }
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["id"]

    response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["total_certificates"] == 2
    assert data["successful_certificates"] == 2
    assert data["failed_certificates"] == 0
    assert data["progress_percentage"] == 100.0


def test_certificate_retrieval():
    create_response = client.post(
        "/api/jobs",
        json={
            "event_name": "Retrieval Test",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "Download Test",
                    "email": "download@example.com",
                    "certificate_type": "Completion"
                }
            ]
        }
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["id"]

    certificates_response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()

    assert len(certificates) == 1
    assert certificates[0]["status"] == "SUCCESS"

    certificate_id = certificates[0]["id"]

    download_response = client.get(
        f"/api/certificates/{certificate_id}/download"
    )

    assert download_response.status_code == 200
    assert (
        download_response.headers["content-type"]
        == "application/pdf"
    )
def test_job_zip_download():
    create_response = client.post(
        "/api/jobs",
        json={
            "event_name": "ZIP Download Test",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "ZIP User One",
                    "email": "zip1@example.com",
                    "certificate_type": "Participation"
                },
                {
                    "name": "ZIP User Two",
                    "email": "zip2@example.com",
                    "certificate_type": "Completion"
                }
            ]
        }
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["id"]

    response = client.get(
        f"/api/jobs/{job_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    content_disposition = response.headers.get(
        "content-disposition",
        ""
    )

    assert f"certificates_job_{job_id}.zip" in content_disposition