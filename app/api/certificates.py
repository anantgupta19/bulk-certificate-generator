from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, GenerationJob
from app.schemas import CertificateResponse


router = APIRouter(
    prefix="/api",
    tags=["Certificates"]
)


ARCHIVE_DIR = Path("generated_archives")
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


@router.get(
    "/jobs/{job_id}/certificates",
    response_model=list[CertificateResponse]
)
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return certificates


@router.get(
    "/certificates/{certificate_id}/download"
)
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "SUCCESS":
        raise HTTPException(
            status_code=409,
            detail=(
                "Certificate is not available. "
                f"Current status: {certificate.status}"
            )
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file path is missing"
        )

    file_path = Path(certificate.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )


@router.get(
    "/jobs/{job_id}/download"
)
def download_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Create and download a ZIP archive containing
    all successfully generated certificates for a job.
    """

    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(
            Certificate.job_id == job_id,
            Certificate.status == "SUCCESS"
        )
        .all()
    )

    if not certificates:
        raise HTTPException(
            status_code=409,
            detail="No successfully generated certificates available"
        )

    zip_filename = f"certificates_job_{job_id}.zip"
    zip_path = ARCHIVE_DIR / zip_filename

    # Re-create the archive each time so it always reflects
    # the latest successful certificates.
    with ZipFile(
        zip_path,
        mode="w",
        compression=ZIP_DEFLATED
    ) as archive:

        for certificate in certificates:

            if not certificate.file_path:
                continue

            file_path = Path(certificate.file_path)

            if not file_path.exists():
                continue

            archive.write(
                file_path,
                arcname=file_path.name
            )

    if not zip_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Failed to create certificate archive"
        )

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename
    )