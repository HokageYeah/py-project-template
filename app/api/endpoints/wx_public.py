from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.services.wx_public import fetch_wx_articles

router = APIRouter()


@router.get("/search")
async def search_wx_articles(query: str = Query(..., description="搜索关键词")):
    """搜索微信公众号文章"""
    result = await fetch_wx_articles(query)
    return result
