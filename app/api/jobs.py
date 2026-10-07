from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, GenerationJob
from app.schemas import GenerationJobCreate, JobResponse
from app.services.job_processor import process_generation_job


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=201
)
def create_generation_job(
    request: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Create the generation job
    job = GenerationJob(
        event_name=request.event_name,
        organization=request.organization,
        event_date=str(request.date),
        status="PENDING",
        total_certificates=len(request.recipients),
        successful_certificates=0,
        failed_certificates=0
    )

    db.add(job)
    db.flush()

    # Create individual certificate records
    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=str(recipient.email),
            certificate_type=recipient.certificate_type,
            status="PENDING"
        )

        db.add(certificate)

    db.commit()
    db.refresh(job)

    # Start processing after the API response
    background_tasks.add_task(
        process_generation_job,
        job.id
    )

    return job


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_generation_job(
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

    return job