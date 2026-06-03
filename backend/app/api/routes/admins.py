"""admins routes"""
from fastapi import APIRouter, Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter()

@router.get("/")
async def list_items(db: AsyncSession = Depends(get_db)):
    return {"message": "admins endpoint active", "status": "ok"}
