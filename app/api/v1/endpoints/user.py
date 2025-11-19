"""
User profile endpoints
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import User
from app.schemas.schemas import UserUpdate, UserResponse
from app.services.services import AuthService

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile
    """
    return UserResponse(
        id=str(current_user.id),
        fullName=current_user.full_name,
        email=current_user.email,
        dateOfBirth=current_user.date_of_birth,
        photoUrl=current_user.photo_url
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile
    """
    try:
        updated_user = AuthService.update_user(db, current_user.id, user_data)
        return UserResponse(
            id=str(updated_user.id),
            fullName=updated_user.full_name,
            email=updated_user.email,
            dateOfBirth=updated_user.date_of_birth,
            photoUrl=updated_user.photo_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/photo", response_model=UserResponse)
async def upload_profile_photo(
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload profile photo
    """
    try:
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )

        # Read file content
        photo_content = await photo.read()

        # Update user photo
        updated_user = AuthService.update_user_photo(db, current_user.id, photo_content, photo.filename)

        return UserResponse(
            id=str(updated_user.id),
            fullName=updated_user.full_name,
            email=updated_user.email,
            dateOfBirth=updated_user.date_of_birth,
            photoUrl=updated_user.photo_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )