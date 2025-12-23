from sqlalchemy import Column, Integer, String, Enum
from db import Base
import enum


class JobStatus(enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, nullable=False)
    status = Column(
        Enum(JobStatus, name="job_status_enum"),
        default=JobStatus.processing,
        nullable=False
    )
    image_url = Column(String(255), nullable=True)
    worker = Column(String(100))
