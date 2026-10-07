from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_certificate_generation():
    file_path = generate_certificate(
        recipient_name="Test User",
        organization="ZHCET AMU",
        event_name="Test Workshop",
        event_date="2026-10-20",
        certificate_type="Participation",
        certificate_id=999999,
    )

    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0

    # Clean up the test certificate
    path.unlink()