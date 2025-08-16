"""
검색 API 엔드포인트
전역 검색, 자동완성, 인기 검색어
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import get_current_user_optional
from app.services.search import SearchService
from app.models.user import User
from app.schemas.search import (
    SearchResponse, 
    AutocompleteResponse, 
    PopularSearchResponse,
    SearchStatsResponse
)

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., min_length=1, max_length=100, description="검색어"),
    categories: Optional[List[str]] = Query(None, description="카테고리 필터"),
    content_types: Optional[List[str]] = Query(None, description="콘텐츠 타입 필터"),
    limit: int = Query(20, ge=1, le=100, description="결과 제한"),
    offset: int = Query(0, ge=0, description="오프셋"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    전역 검색
    
    - **q**: 검색어 (필수)
    - **categories**: 카테고리 필터 (선택)
    - **content_types**: 검색할 콘텐츠 타입 ["project", "note", "user"] (선택)
    - **limit**: 결과 개수 제한 (기본값: 20)
    - **offset**: 페이지네이션 오프셋 (기본값: 0)
    """
    service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    try:
        results = await service.search_all(
            query=q,
            user_id=user_id,
            categories=categories,
            content_types=content_types,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete(
    q: str = Query(..., min_length=1, max_length=50, description="자동완성 쿼리"),
    type: str = Query("all", description="자동완성 타입"),
    limit: int = Query(10, ge=1, le=20, description="제안 개수"),
    db: AsyncSession = Depends(get_db)
):
    """
    자동완성 제안
    
    - **q**: 자동완성할 검색어 (필수)
    - **type**: 자동완성 타입 ["all", "project", "note", "tag"] (기본값: "all")
    - **limit**: 제안 개수 (기본값: 10)
    """
    service = SearchService(db)
    
    # 유효한 타입 검증
    valid_types = ["all", "project", "note", "tag"]
    if type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid autocomplete type. Must be one of: {valid_types}"
        )
    
    try:
        suggestions = await service.get_autocomplete_suggestions(
            query=q,
            content_type=type,
            limit=limit
        )
        
        return {
            "query": q,
            "suggestions": suggestions,
            "type": type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Autocomplete failed: {str(e)}"
        )


@router.get("/popular", response_model=PopularSearchResponse)
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50, description="인기 검색어 개수"),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 검색어 조회
    
    - **limit**: 반환할 인기 검색어 개수 (기본값: 10)
    """
    service = SearchService(db)
    
    try:
        popular_searches = await service.get_popular_searches(limit=limit)
        
        return {
            "popular_searches": popular_searches,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular searches: {str(e)}"
        )


@router.get("/stats", response_model=SearchStatsResponse)
async def get_search_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    검색 통계 조회
    
    전체 인덱싱된 콘텐츠 수 및 검색 가능한 데이터 통계
    """
    service = SearchService(db)
    
    try:
        stats = await service.get_search_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search stats: {str(e)}"
        )


@router.get("/projects", response_model=SearchResponse)
async def search_projects_only(
    q: str = Query(..., min_length=1, max_length=100, description="검색어"),
    categories: Optional[List[str]] = Query(None, description="카테고리 필터"),
    limit: int = Query(20, ge=1, le=100, description="결과 제한"),
    offset: int = Query(0, ge=0, description="오프셋"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트만 검색
    
    - **q**: 검색어 (필수)
    - **categories**: 카테고리 필터 (선택)
    - **limit**: 결과 개수 제한 (기본값: 20)
    - **offset**: 페이지네이션 오프셋 (기본값: 0)
    """
    service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    try:
        results = await service.search_all(
            query=q,
            user_id=user_id,
            categories=categories,
            content_types=["project"],
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project search failed: {str(e)}"
        )


@router.get("/notes", response_model=SearchResponse)
async def search_notes_only(
    q: str = Query(..., min_length=1, max_length=100, description="검색어"),
    limit: int = Query(20, ge=1, le=100, description="결과 제한"),
    offset: int = Query(0, ge=0, description="오프셋"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    노트만 검색
    
    - **q**: 검색어 (필수)
    - **limit**: 결과 개수 제한 (기본값: 20)
    - **offset**: 페이지네이션 오프셋 (기본값: 0)
    """
    service = SearchService(db)
    user_id = current_user.id if current_user else None
    
    try:
        results = await service.search_all(
            query=q,
            user_id=user_id,
            categories=None,
            content_types=["note"],
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Note search failed: {str(e)}"
        )


@router.get("/users", response_model=SearchResponse)
async def search_users_only(
    q: str = Query(..., min_length=1, max_length=100, description="검색어"),
    limit: int = Query(20, ge=1, le=100, description="결과 제한"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자만 검색
    
    - **q**: 검색어 (필수)
    - **limit**: 결과 개수 제한 (기본값: 20)
    - **offset**: 페이지네이션 오프셋 (기본값: 0)
    """
    service = SearchService(db)
    
    try:
        results = await service.search_all(
            query=q,
            user_id=None,  # 사용자 검색은 공개 프로필만
            categories=None,
            content_types=["user"],
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User search failed: {str(e)}"
        )