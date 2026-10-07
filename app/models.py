from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_name = Column(
        String(255),
        nullable=False
    )

    organization = Column(
        String(255),
        nullable=False
    )

    event_date = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING"
    )

    total_certificates = Column(
        Integer,
        default=0
    )

    successful_certificates = Column(
        Integer,
        default=0
    )

    failed_certificates = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    @property
    def progress_percentage(self):
        """
        Calculate the percentage of certificates
        that have finished processing.
        """

        if self.total_certificates == 0:
            return 0.0

        completed = (
            self.successful_certificates
            + self.failed_certificates
        )

        return round(
            (completed / self.total_certificates) * 100,
            2
        )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("generation_jobs.id"),
        nullable=False,
        index=True
    )

    recipient_name = Column(
        String(255),
        nullable=False
    )

    recipient_email = Column(
        String(255),
        nullable=False
    )

    certificate_type = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING"
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    job = relationship(
        "GenerationJob",
        back_populates="certificates"
    )