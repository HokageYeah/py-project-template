from fastapi import APIRouter

from app.api.endpoints import wx_public

api_router = APIRouter()
api_router.include_router(wx_public.router, prefix="/wx/public", tags=["微信公众号"])
