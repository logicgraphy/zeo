from fastapi import APIRouter
import uuid

from ..models import HireRequest, MessageResponse
from ..database import DatabaseService

router = APIRouter(prefix="/hire", tags=["hire"])

@router.post("/request", response_model=MessageResponse)
async def hire_request(req: HireRequest):
    """Submit a hire request"""
    req_id = str(uuid.uuid4())
    DatabaseService.create_hire_request(req_id, req.dict())
    return MessageResponse(message="Your request has been received.") 