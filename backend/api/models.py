from pydantic import BaseModel, EmailStr
from typing import Optional, List
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

class AEOReportMeta(BaseModel):
    report_title: str
    scope: str
    analyzed_at: str
    overall_score: int
    analyst: str
    tool_version: str

class ExecutiveSummary(BaseModel):
    summary_paragraph: str
    highlights: List[str]

class ScoreNotes(BaseModel):
    score: int
    notes: str

class OverallFindings(BaseModel):
    content_quality: ScoreNotes
    structure: ScoreNotes
    authority_signals: ScoreNotes
    ai_agent_compatibility: ScoreNotes
    impact: str
    common_themes: List[str]

class Strengths(BaseModel):
    brand_domain_trust: List[str]
    navigation_layout: List[str]
    technical_signals: List[str]

class Weaknesses(BaseModel):
    content_depth: List[str]
    authority_trust: List[str]
    semantic_accessibility: List[str]
    ux_friction: List[str]

class Recommendation(BaseModel):
    priority: str
    action: str
    rationale: str
    owner: str
    effort: str
    impact: str
    success_metrics: List[str]

class AEOReport(BaseModel):
    meta: AEOReportMeta
    executive_summary: ExecutiveSummary
    overall_findings: OverallFindings
    strengths: Strengths
    weaknesses: Weaknesses
    recommendations: List[Recommendation]
    bottom_line: str

# Steps: removed from workflow

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

# Contact models
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

# Quick analyze structured models
class CategoryScore(BaseModel):
    score: int
    reason: str

class QuickAnalyzeResponse(BaseModel):
    analysis_id: str
    overall_score: int
    url: str
    content_quality: CategoryScore
    structure_optimization: CategoryScore
    authority_trust: CategoryScore
    ai_agent_compatibility: CategoryScore