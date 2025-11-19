"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: Optional[str] = None
    photo_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[str] = None
    photo_url: Optional[str] = None


class UserInDBBase(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    icon: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoriesListResponse(BaseModel):
    categories: List[Category]


# Transaction schemas
class TransactionBase(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$")
    name: str = Field(..., min_length=1, max_length=100)
    category_id: str
    amount: float = Field(..., gt=0)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD format
    note: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    note: Optional[str] = None


class Transaction(TransactionBase):
    id: str
    user_id: str
    category: Optional[Category] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionsListResponse(BaseModel):
    transactions: List[Transaction]


# Summary schemas
class CategorySummary(BaseModel):
    category_id: str
    category_name: str
    category_icon: str
    category_color: str
    total: float
    percentage: float


class BalanceSummaryResponse(BaseModel):
    user_id: str
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    balance: float
    total_income: float
    total_expense: float
    income_by_category: Optional[List[CategorySummary]] = None
    expense_by_category: Optional[List[CategorySummary]] = None


class MonthlySummaryListResponse(BaseModel):
    summaries: List[BalanceSummaryResponse]


# Grouped transactions
class TransactionsByDateResponse(BaseModel):
    date: str
    transactions: List[Transaction]
    total_income: float
    total_expense: float


class GroupedTransactionsResponse(BaseModel):
    groups: List[TransactionsByDateResponse]