"""
Authentication endpoints
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, UserUpdate, User, Token, AuthResponse, UserResponse
)
from app.services.services import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    try:
        user = AuthService.register_user(db, user_data)
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=30)
        )

        return AuthResponse(
            token=access_token,
            user=UserResponse(
                id=user.id,
                fullName=user.full_name,
                email=user.email,
                dateOfBirth=user.date_of_birth,
                photoUrl=user.photo_url
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Login user
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=30)
    )

    return AuthResponse(
        token=access_token,
        user=UserResponse(
            id=user.id,
            fullName=user.full_name,
            email=user.email,
            dateOfBirth=user.date_of_birth,
            photoUrl=user.photo_url
        )
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user profile
    """
    return UserResponse(
        id=current_user.id,
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
    Update user profile
    """
    try:
        updated_user = AuthService.update_user(db, current_user.id, user_data)
        return UserResponse(
            id=updated_user.id,
            fullName=updated_user.full_name,
            email=updated_user.email,
            dateOfBirth=updated_user.date_of_birth,
            photoUrl=updated_user.photo_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/photo", response_model=UserResponse)
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload user profile photo
    """
    # For now, just update with a placeholder URL
    # In production, you would upload to cloud storage
    photo_url = f"/uploads/{current_user.id}/profile.jpg"

    user_update = UserUpdate(photoUrl=photo_url)
    updated_user = AuthService.update_user(db, current_user.id, user_update)

    return UserResponse(
        id=updated_user.id,
        fullName=updated_user.full_name,
        email=updated_user.email,
        dateOfBirth=updated_user.date_of_birth,
        photoUrl=updated_user.photo_url
    )