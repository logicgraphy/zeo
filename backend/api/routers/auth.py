from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta

from ..models import UserRegister, EmailVerification, UserResponse, MessageResponse
from ..utils import generate_verification_code, send_verification_email
from ..database import DatabaseService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserRegister):
    """Register a new user and send verification email"""
    
    # Check if user already exists
    if DatabaseService.get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Generate and store verification code
    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=5)
    DatabaseService.set_verification_code(user.email, verification_code, expires_at)
    
    # Create user in database
    user_data = DatabaseService.create_user(user.email, user.name, False)
    
    # Send verification email
    if not send_verification_email(user.email, verification_code):
        # Clean up if email sending fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return UserResponse(
        email=user_data["email"],
        name=user_data["name"],
        is_verified=user_data["is_verified"]
    )

@router.post("/verify-email")
async def verify_email(verification: EmailVerification):
    """Verify user email with verification code"""
    
    # Check if user exists
    user = DatabaseService.get_user(verification.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if verification code exists
    code_data = DatabaseService.get_verification_code(verification.email)
    if not code_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new one."
        )
    
    # Check if code has expired
    if datetime.now() > code_data["expires_at"]:
        DatabaseService.delete_verification_code(verification.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new one."
        )
    
    # Check attempt limit (max 3 attempts)
    if code_data["attempts"] >= 3:
        DatabaseService.delete_verification_code(verification.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many failed attempts. Please request a new verification code."
        )
    
    # Verify code
    if verification.code != code_data["code"]:
        remaining_attempts = 3 - DatabaseService.increment_verification_attempts(verification.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. {remaining_attempts} attempts remaining."
        )
    
    # Mark user as verified and clean up verification code
    DatabaseService.update_user_verification(verification.email)
    DatabaseService.delete_verification_code(verification.email)
    
    # Get updated user (we know it exists since we verified it above)
    updated_user = DatabaseService.get_user(verification.email)
    if not updated_user:  # This should never happen, but satisfies the type checker
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User verification failed"
        )
    
    return {
        "message": "Email verified successfully",
        "user": UserResponse(
            email=updated_user["email"],
            name=updated_user["name"],
            is_verified=updated_user["is_verified"]
        )
    }

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_code(email_request: dict):
    """Resend verification code"""
    email = email_request.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    # Check if user exists
    user = DatabaseService.get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification code
    verification_code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=5)
    DatabaseService.set_verification_code(email, verification_code, expires_at)
    
    # Send verification email
    if not send_verification_email(email, verification_code):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )
    
    return MessageResponse(message="Verification code sent successfully") 