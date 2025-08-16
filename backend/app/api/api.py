"""
API 라우터 통합
모든 API 엔드포인트를 하나로 모음
"""

from fastapi import APIRouter

from app.api.endpoints import auth

# 메인 API 라우터
api_router = APIRouter()

# 인증 API 라우터 등록
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)