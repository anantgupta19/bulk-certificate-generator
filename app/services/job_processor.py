from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Certificate, GenerationJob
from app.services.certificate_generator import generate_certificate


def process_generation_job(job_id: int) -> None:
    """
    Process all certificates belonging to a generation job.

    Each certificate is processed independently so that
    one failure does not stop the remaining certificates.
    """

    db: Session = SessionLocal()

    try:
        job = (
            db.query(GenerationJob)
            .filter(GenerationJob.id == job_id)
            .first()
        )

        if job is None:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:

            try:
                certificate.status = "PROCESSING"
                db.commit()

                file_path = generate_certificate(
                    recipient_name=certificate.recipient_name,
                    organization=job.organization,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    certificate_type=certificate.certificate_type,
                    certificate_id=certificate.id,
                )

                certificate.status = "SUCCESS"
                certificate.file_path = file_path
                certificate.error_message = None

                job.successful_certificates += 1

                db.commit()

            except Exception as error:

                certificate.status = "FAILED"
                certificate.error_message = str(error)

                job.failed_certificates += 1

                db.commit()

        if job.failed_certificates == 0:
            job.status = "COMPLETED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"

        db.commit()

    finally:
        db.close()