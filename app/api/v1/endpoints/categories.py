"""
Category endpoints
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import User
from app.schemas.schemas import CategoryCreate, Category, CategoriesListResponse
from app.services.services import CategoryService

router = APIRouter()


@router.get("/categories", response_model=CategoriesListResponse)
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all categories for current user
    """
    categories = CategoryService.get_user_categories(db, current_user.id)
    return CategoriesListResponse(categories=categories)


@router.post("/categories", response_model=Category)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new category
    """
    category = CategoryService.create_category(db, current_user.id, category_data)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a category
    """
    success = CategoryService.delete_category(db, current_user.id, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )