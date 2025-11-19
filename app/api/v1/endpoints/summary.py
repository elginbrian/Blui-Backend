"""
Summary endpoints
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import User
from app.schemas.schemas import BalanceSummaryResponse, MonthlySummaryListResponse
from app.services.services import SummaryService

router = APIRouter()


@router.get("/summary", response_model=BalanceSummaryResponse)
async def get_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get monthly balance summary
    """
    summary = SummaryService.get_monthly_summary(db, current_user.id, month, year)
    return summary


@router.get("/summary/history", response_model=MonthlySummaryListResponse)
async def get_summary_history(
    start_month: Optional[int] = Query(None, ge=1, le=12),
    start_year: Optional[int] = Query(None, ge=2000, le=2100),
    end_month: Optional[int] = Query(None, ge=1, le=12),
    end_year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get summary history for multiple months
    """
    # For now, return empty list - implement pagination later
    # This would require more complex logic to generate date ranges
    return MonthlySummaryListResponse(summaries=[])