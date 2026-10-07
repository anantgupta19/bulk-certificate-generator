from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_email_is_rejected():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": [
                {
                    "name": "Anant Gupta",
                    "email": "invalid-email",
                    "certificate_type": "Participation"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_empty_recipients_are_rejected():
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "organization": "ZHCET AMU",
            "date": "2026-10-20",
            "recipients": []
        }
    )

    assert response.status_code == 422