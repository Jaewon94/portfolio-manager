"""
API 라우터 통합
모든 API 엔드포인트를 하나로 모음
"""

from app.api.endpoints import (
    auth,
    dashboard,
    github_repository,
    media,
    notes,
    projects,
    search,
)
from fastapi import APIRouter

# 메인 API 라우터
api_router = APIRouter()

# 인증 API 라우터 등록
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# 프로젝트 API 라우터 등록
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

# 노트 API 라우터 등록
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])

# 검색 API 라우터 등록
api_router.include_router(search.router, prefix="/search", tags=["search"])

# 미디어 API 라우터 등록
api_router.include_router(media.router, prefix="/media", tags=["media"])

# 대시보드 API 라우터 등록
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# GitHub Repository API 라우터 등록
api_router.include_router(github_repository.router, prefix="/github", tags=["github"])
