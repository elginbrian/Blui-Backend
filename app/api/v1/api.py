"""
Main API router that combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, transactions, summary

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(transactions.router, tags=["transactions"])
api_router.include_router(summary.router, tags=["summary"])