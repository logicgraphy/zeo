# db/models.py
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base, Mapped, mapped_column
import uuid

def gen_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sites: Mapped[list["Site"]] = relationship("Site", back_populates="user")
    codes: Mapped[list["VerificationCode"]] = relationship("VerificationCode", back_populates="user")
    hire_requests: Mapped[list["HireRequest"]] = relationship("HireRequest", back_populates="user")

class Site(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"))
    url: Mapped[str] = mapped_column(Text)
    last_grade: Mapped[str] = mapped_column(String(5), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="sites")
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="site")
    hire_requests: Mapped[list["HireRequest"]] = relationship("HireRequest", back_populates="site")

class VerificationCode(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"))
    code_hash: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="codes")

class ReportStatus(str, enum.Enum):
    pending = "pending"
    ready = "ready"
    failed = "failed"

class Report(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    site_id: Mapped[str] = mapped_column(String(36), ForeignKey("site.id"))
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    report_url: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    site: Mapped[Site] = relationship("Site", back_populates="reports")
    diy_steps: Mapped[list["DiyStep"]] = relationship("DiyStep", back_populates="report")

class StepPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"

class DiyStep(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("report.id"))
    step_text: Mapped[str] = mapped_column(Text)
    priority: Mapped[StepPriority] = mapped_column(Enum(StepPriority))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    report: Mapped[Report] = relationship("Report", back_populates="diy_steps")

class HireRequest(Base):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"))
    site_id: Mapped[str] = mapped_column(String(36), ForeignKey("site.id"))
    name: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="hire_requests")
    site: Mapped[Site] = relationship("Site", back_populates="hire_requests")