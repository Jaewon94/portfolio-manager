"""
API 라우터 통합
모든 API 엔드포인트를 하나로 모음
"""

from fastapi import APIRouter

from app.api.endpoints import auth, projects, notes, search

# 메인 API 라우터
api_router = APIRouter()

# 인증 API 라우터 등록
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# 프로젝트 API 라우터 등록
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

# 노트 API 라우터 등록
api_router.include_router(
    notes.router,
    prefix="/notes",
    tags=["notes"]
)

# 검색 API 라우터 등록
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)