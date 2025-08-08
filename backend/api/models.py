from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

# User-related models
class UserRegister(BaseModel):
    email: EmailStr    
    name: str

class EmailVerification(BaseModel):
    email: EmailStr
    code: str

class UserResponse(BaseModel):
    email: str
    name: str
    is_verified: bool

# Analysis and Report models
class QuickAnalyzeRequest(BaseModel):
    url: str

class ReportRequest(BaseModel):
    url: str
    email: EmailStr

class ReportStatus(BaseModel):
    site_id: str
    status: str
    score: int
    report_url: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str
    score: int
    issues: list[dict]
    report_url: Optional[str] = None

# Step models
class StepPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class StepResponse(BaseModel):
    id: str
    priority: StepPriority
    text: str
    completed: bool

class StepUpdate(BaseModel):
    completed: bool

class StepsResponse(BaseModel):
    steps: list[StepResponse]

# Hire request models
class HireRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None
    site_id: str
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None

# Generic response models
class MessageResponse(BaseModel):
    message: str

class AnalysisResponse(BaseModel):
    score: int
    summary: str
    analysis_id: str
    formatted_summary_html: Optional[str] = None