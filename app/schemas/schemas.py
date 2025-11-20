"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, alias="fullName")
    email: EmailStr
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    photo_url: Optional[str] = Field(None, alias="photoUrl")

    class Config:
        from_attributes = True
        populate_by_name = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, alias="fullName")
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    photo_url: Optional[str] = Field(None, alias="photoUrl")

    class Config:
        populate_by_name = True


class UserInDBBase(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    full_name: str = Field(..., alias="fullName")
    email: str
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")
    photo_url: Optional[str] = Field(None, alias="photoUrl")

    class Config:
        from_attributes = True
        populate_by_name = True


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    icon: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: str
    user_id: str = Field(..., alias="userId")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class CategoriesListResponse(BaseModel):
    categories: List[Category]


# Transaction schemas
class TransactionBase(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$")
    description: str = Field(..., min_length=1, max_length=100, alias="name")
    category_id: str = Field(..., alias="categoryId")
    amount: float = Field(..., gt=0)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD format

    class Config:
        populate_by_name = True


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=100, alias="name")
    category_id: Optional[str] = Field(None, alias="categoryId")
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    class Config:
        populate_by_name = True


class Transaction(TransactionBase):
    id: str
    user_id: str = Field(..., alias="userId")
    category: Optional[Category] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class TransactionsListResponse(BaseModel):
    transactions: List[Transaction]


# Summary schemas
class CategorySummary(BaseModel):
    category_id: str = Field(..., alias="categoryId")
    category_name: str = Field(..., alias="categoryName")
    category_icon: str = Field(..., alias="categoryIcon")
    category_color: str = Field(..., alias="categoryColor")
    total: float
    percentage: float

    class Config:
        populate_by_name = True


class BalanceSummaryResponse(BaseModel):
    user_id: str = Field(..., alias="userId")
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    balance: float
    total_income: float = Field(..., alias="totalIncome")
    total_expense: float = Field(..., alias="totalExpense")
    income_by_category: Optional[List[CategorySummary]] = Field(None, alias="incomeByCategory")
    expense_by_category: Optional[List[CategorySummary]] = Field(None, alias="expenseByCategory")

    class Config:
        populate_by_name = True


class MonthlySummaryListResponse(BaseModel):
    summaries: List[BalanceSummaryResponse]


# Grouped transactions
class TransactionsByDateResponse(BaseModel):
    date: str
    transactions: List[Transaction]
    total_income: float = Field(..., alias="totalIncome")
    total_expense: float = Field(..., alias="totalExpense")

    class Config:
        populate_by_name = True


class GroupedTransactionsResponse(BaseModel):
    groups: List[TransactionsByDateResponse]