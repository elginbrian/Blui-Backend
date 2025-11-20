"""
Authentication endpoints
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token
from app.models.models import User
from app.schemas.schemas import UserCreate, AuthResponse, UserResponse, LoginRequest
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
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=30)
        )

        return AuthResponse(
            token=access_token,
            user=UserResponse(
                id=str(user.id),
                full_name=user.full_name,
                email=user.email,
                date_of_birth=user.date_of_birth,
                photo_url=user.photo_url
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login user
    """
    user = AuthService.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return AuthResponse(
        token=access_token,
        user=UserResponse(
            id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            date_of_birth=user.date_of_birth,
            photo_url=user.photo_url
        )
    )