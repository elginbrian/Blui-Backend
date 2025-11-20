"""
Business logic services
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, Category, Transaction
from app.schemas.schemas import (
    UserCreate, UserUpdate, CategoryCreate, TransactionCreate, TransactionUpdate,
    BalanceSummaryResponse, CategorySummary, TransactionsByDateResponse
)


class AuthService:
    """Authentication service"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_data.password)

        user = User(
            id=user_id,
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_password,
            date_of_birth=user_data.date_of_birth,
            photo_url=user_data.photo_url
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> User:
        """Update user profile"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_photo(db: Session, user_id: str, photo_content: bytes, filename: str) -> User:
        """Update user profile photo"""
        import os
        from pathlib import Path

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        uploads_dir = Path("/app/uploads")
        user_dir = uploads_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        file_extension = Path(filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
            file_extension = '.jpg'  # default to jpg

        unique_filename = f"profile_{user_id}{file_extension}"
        file_path = user_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(photo_content)

        photo_url = f"/uploads/{user_id}/{unique_filename}"

        user.photo_url = photo_url
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user


class CategoryService:
    """Category service"""

    @staticmethod
    def get_user_categories(db: Session, user_id: str) -> List[Category]:
        """Get all categories for a user"""
        return db.query(Category).filter(Category.user_id == user_id).all()

    @staticmethod
    def create_category(db: Session, user_id: str, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        category_id = str(uuid.uuid4())
        category = Category(
            id=category_id,
            user_id=user_id,
            name=category_data.name,
            icon=category_data.icon,
            color=category_data.color
        )

        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, user_id: str, category_id: str) -> bool:
        """Delete a category"""
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            return False

        db.delete(category)
        db.commit()
        return True


class TransactionService:
    """Transaction service"""

    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions with optional filters"""
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if month and year:
            query = query.filter(
                Transaction.date.like(f"{year}-{month:02d}-%")
            )
        elif date:
            query = query.filter(Transaction.date == date)
        elif start_date and end_date:
            query = query.filter(Transaction.date.between(start_date, end_date))
        elif start_date:
            query = query.filter(Transaction.date >= start_date)
        elif end_date:
            query = query.filter(Transaction.date <= end_date)

        return query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).all()

    @staticmethod
    def get_grouped_transactions(
        db: Session,
        user_id: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[TransactionsByDateResponse]:
        """Get transactions grouped by date"""
        transactions = TransactionService.get_user_transactions(
            db, user_id, month, year, None, start_date, end_date
        )

        # Group by date
        grouped = {}
        for transaction in transactions:
            date = transaction.date
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(transaction)

        # Convert to response format
        result = []
        for date, txns in grouped.items():
            total_income = sum(t.amount for t in txns if t.type == "income")
            total_expense = sum(t.amount for t in txns if t.type == "expense")

            result.append(TransactionsByDateResponse(
                date=date,
                transactions=txns,
                total_income=total_income,
                total_expense=total_expense
            ))

        # Sort by date descending
        result.sort(key=lambda x: x.date, reverse=True)
        return result

    @staticmethod
    def get_transaction_by_id(db: Session, user_id: str, transaction_id: str) -> Optional[Transaction]:
        """Get a single transaction by ID"""
        return db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()

    @staticmethod
    def create_transaction(db: Session, user_id: str, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        # Verify category belongs to user
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id,
            Category.user_id == user_id
        ).first()

        if not category:
            raise ValueError("Category not found or doesn't belong to user")

        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            id=transaction_id,
            user_id=user_id,
            category_id=transaction_data.category_id,
            type=transaction_data.type,
            name=transaction_data.name,
            amount=transaction_data.amount,
            date=transaction_data.date,
            note=transaction_data.note
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def update_transaction(
        db: Session,
        user_id: str,
        transaction_id: str,
        transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update a transaction"""
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()

        if not transaction:
            return None

        # Verify category if being updated
        if transaction_data.category_id:
            category = db.query(Category).filter(
                Category.id == transaction_data.category_id,
                Category.user_id == user_id
            ).first()
            if not category:
                raise ValueError("Category not found or doesn't belong to user")

        update_data = transaction_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def delete_transaction(db: Session, user_id: str, transaction_id: str) -> bool:
        """Delete a transaction"""
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()

        if not transaction:
            return False

        db.delete(transaction)
        db.commit()
        return True


class SummaryService:
    """Summary and analytics service"""

    @staticmethod
    def get_monthly_summary(
        db: Session,
        user_id: str,
        month: int,
        year: int
    ) -> BalanceSummaryResponse:
        """Get monthly balance summary"""
        # Get all transactions for the month
        transactions = TransactionService.get_user_transactions(
            db, user_id, month, year
        )

        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")
        balance = total_income - total_expense

        # Calculate category breakdowns
        income_by_category = SummaryService._calculate_category_breakdown(
            transactions, "income", total_income
        )
        expense_by_category = SummaryService._calculate_category_breakdown(
            transactions, "expense", total_expense
        )

        return BalanceSummaryResponse(
            user_id=str(user_id),
            month=month,
            year=year,
            balance=balance,
            total_income=total_income,
            total_expense=total_expense,
            income_by_category=income_by_category,
            expense_by_category=expense_by_category
        )

    @staticmethod
    def _calculate_category_breakdown(
        transactions: List[Transaction],
        transaction_type: str,
        total_amount: float
    ) -> Optional[List[CategorySummary]]:
        """Calculate breakdown by category"""
        if total_amount == 0:
            return None

        # Group by category
        category_totals = {}
        for transaction in transactions:
            if transaction.type == transaction_type:
                cat_id = transaction.category_id
                if cat_id not in category_totals:
                    category_totals[cat_id] = {
                        'total': 0,
                        'category': transaction.category
                    }
                category_totals[cat_id]['total'] += transaction.amount

        # Convert to CategorySummary
        result = []
        for cat_data in category_totals.values():
            total = cat_data['total']
            category = cat_data['category']
            if category:
                result.append(CategorySummary(
                    category_id=str(category.id),
                    category_name=category.name,
                    category_icon=category.icon,
                    category_color=category.color,
                    total=total,
                    percentage=(total / total_amount) * 100
                ))

        # Sort by total descending
        result.sort(key=lambda x: x.total, reverse=True)
        return result