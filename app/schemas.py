from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255
    )

    email: EmailStr

    certificate_type: str = Field(
        min_length=2,
        max_length=100
    )


class GenerationJobCreate(BaseModel):
    event_name: str = Field(
        min_length=2,
        max_length=255
    )

    organization: str = Field(
        min_length=2,
        max_length=255
    )

    date: date

    recipients: List[RecipientCreate] = Field(
        min_length=1
    )


class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    certificate_type: str
    status: str
    file_path: str | None = None
    error_message: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class JobResponse(BaseModel):
    id: int
    event_name: str
    organization: str
    event_date: str
    status: str
    total_certificates: int
    successful_certificates: int
    failed_certificates: int
    progress_percentage: float

    model_config = ConfigDict(
        from_attributes=True
    )