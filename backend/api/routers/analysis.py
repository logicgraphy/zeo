from fastapi import APIRouter, HTTPException
import uuid
import random
from datetime import datetime, timedelta

from ..models import (
    QuickAnalyzeRequest, ReportRequest, AnalysisResponse, 
    ReportStatus, ReportResponse, StepsResponse, StepResponse,
    StepUpdate, MessageResponse, EmailVerification
)
from ..utils import generate_verification_code, send_verification_email
from ..database import DatabaseService
from .auth import verify_email

router = APIRouter(tags=["analysis"])

@router.post("/analyze/quick", response_model=AnalysisResponse)
async def quick_analyze(req: QuickAnalyzeRequest):
    """Perform quick website analysis"""
    analysis_id = str(uuid.uuid4())
    grade = random.choice(["A", "B", "C", "D"])
    summary = f"Sample analysis summary for {req.url}"
    score = random.randint(70, 95)
    
    DatabaseService.create_analysis(analysis_id, req.url, grade, summary, score)
    
    return AnalysisResponse(
        grade=grade,
        summary=summary,
        analysis_id=analysis_id
    )

@router.post("/report/request", response_model=MessageResponse)
async def request_report(req: ReportRequest):
    """Request a detailed report for a website"""
    # If user not registered, register as unverified
    user = DatabaseService.get_user(req.email)
    if not user:
        DatabaseService.create_user(req.email, "Anonymous", False)
    
    # Generate verification code
    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=5)
    DatabaseService.set_verification_code(req.email, verification_code, expires_at)
    
    send_verification_email(req.email, verification_code)
    return MessageResponse(message="Verification code sent to email")

@router.get("/report/status/{analysis_id}", response_model=ReportStatus)
async def report_status(analysis_id: str):
    """Get the status of a report"""
    data = DatabaseService.get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return ReportStatus(
        site_id=analysis_id,
        status=data.get("status", "pending"),
        score=data.get("score", 80),
        report_url=None
    )

@router.get("/report/{analysis_id}", response_model=ReportResponse)
async def get_report(analysis_id: str):
    """Get detailed report for an analysis"""
    data = DatabaseService.get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(
        report_id=analysis_id,
        score=data.get("score", 80),
        issues=[
            {"priority": "high", "text": "Add meta descriptions"},
            {"priority": "medium", "text": "Optimize images"}
        ],
        report_url=None
    )

@router.get("/report/{analysis_id}/steps", response_model=StepsResponse)
async def get_steps(analysis_id: str):
    """Get improvement steps for an analysis"""
    # Create dummy steps if they don't exist
    existing_steps = DatabaseService.get_steps(analysis_id)
    if not existing_steps:
        steps = [
            {"id": "step1", "priority": "high", "text": "Fix H1 tags", "completed": False},
            {"id": "step2", "priority": "medium", "text": "Add alt attributes", "completed": False}
        ]
        DatabaseService.create_steps(analysis_id, steps)
    else:
        steps = existing_steps
    
    step_responses = [
        StepResponse(
            id=step["id"],
            priority=step["priority"],
            text=step["text"],
            completed=step["completed"]
        )
        for step in steps
    ]
    
    return StepsResponse(steps=step_responses)

@router.patch("/steps/{step_id}", response_model=StepResponse)
async def update_step(step_id: str, update: StepUpdate):
    """Update the completion status of a step"""
    updated_step = DatabaseService.update_step(step_id, update.completed)
    if not updated_step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    return StepResponse(
        id=updated_step["id"],
        priority=updated_step["priority"],
        text=updated_step["text"],
        completed=updated_step["completed"]
    ) 