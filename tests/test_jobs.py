from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_generation_job():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Test Workshop",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "certificate_type": "Participation"
                }
            ]
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_name"] == "Test Workshop"
    assert data["organization"] == "ZHCET AMU"
    assert data["total_certificates"] == 1


def test_individual_certificate_failure(monkeypatch):
    from app.services import job_processor

    original_generator = job_processor.generate_certificate

    def failing_generator(
        recipient_name,
        organization,
        event_name,
        event_date,
        certificate_type,
        certificate_id,
    ):
        if recipient_name == "Failing User":
            raise RuntimeError(
                "Simulated certificate generation failure"
            )

        return original_generator(
            recipient_name=recipient_name,
            organization=organization,
            event_name=event_name,
            event_date=event_date,
            certificate_type=certificate_type,
            certificate_id=certificate_id,
        )

    monkeypatch.setattr(
        job_processor,
        "generate_certificate",
        failing_generator
    )

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Failure Handling Test",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "Working User",
                    "email": "working@example.com",
                    "certificate_type": "Participation"
                },
                {
                    "name": "Failing User",
                    "email": "failing@example.com",
                    "certificate_type": "Participation"
                },
                {
                    "name": "Another Working User",
                    "email": "working2@example.com",
                    "certificate_type": "Participation"
                }
            ]
        }
    )

    assert response.status_code == 201

    job_id = response.json()["id"]

    job_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert job_response.status_code == 200

    job = job_response.json()

    assert job["status"] == "COMPLETED_WITH_ERRORS"
    assert job["total_certificates"] == 3
    assert job["successful_certificates"] == 2
    assert job["failed_certificates"] == 1
    assert job["progress_percentage"] == 100.0

    certificates_response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()

    failed = [
        certificate
        for certificate in certificates
        if certificate["recipient_name"] == "Failing User"
    ]

    assert len(failed) == 1
    assert failed[0]["status"] == "FAILED"
    assert failed[0]["error_message"] is not None