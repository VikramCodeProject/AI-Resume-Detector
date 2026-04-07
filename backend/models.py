"""Database models for persistent storage."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from utils.time_utils import utc_now


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="candidate")
    gdpr_consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="processing")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    processing_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)

    trust_overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    trust_verified_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_doubtful_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_fake_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trust_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    resume_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(50), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    extracted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)

