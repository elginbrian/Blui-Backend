"""
Transaction endpoints
"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import User
from app.schemas.schemas import (
    TransactionCreate, TransactionUpdate, Transaction,
    TransactionsListResponse, GroupedTransactionsResponse
)
from app.services.services import TransactionService

router = APIRouter()


@router.get("/transactions", response_model=TransactionsListResponse)
async def get_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    start_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get transactions with optional filters
    """
    transactions = TransactionService.get_user_transactions(
        db, current_user.id, month, year, date, start_date, end_date
    )
    return TransactionsListResponse(transactions=transactions)


@router.get("/transactions/grouped", response_model=GroupedTransactionsResponse)
async def get_grouped_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    start_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get transactions grouped by date
    """
    grouped_transactions = TransactionService.get_grouped_transactions(
        db, current_user.id, month, year, start_date, end_date
    )
    return GroupedTransactionsResponse(groups=grouped_transactions)


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a single transaction by ID
    """
    transaction = TransactionService.get_transaction_by_id(db, current_user.id, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaction


@router.post("/transactions", response_model=Transaction)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new transaction
    """
    try:
        transaction = TransactionService.create_transaction(db, current_user.id, transaction_data)
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a transaction
    """
    try:
        transaction = TransactionService.update_transaction(
            db, current_user.id, transaction_id, transaction_data
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a transaction
    """
    success = TransactionService.delete_transaction(db, current_user.id, transaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )