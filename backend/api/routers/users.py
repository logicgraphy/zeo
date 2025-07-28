from fastapi import APIRouter, HTTPException, status

from ..models import UserResponse
from ..database import DatabaseService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{email}", response_model=UserResponse)
async def get_user(email: str):
    """Get user information"""
    user = DatabaseService.get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        email=user["email"],
        name=user["name"],
        is_verified=user["is_verified"]
    ) 