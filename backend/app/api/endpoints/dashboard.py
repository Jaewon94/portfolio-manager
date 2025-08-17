"""
대시보드 API 엔드포인트
Dashboard API endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStatsResponse,
    ProjectStatsResponse,
    ActivityTimelineResponse,
    PopularProjectsResponse,
    TechStackStatsResponse,
    CategoryStatsResponse,
    NoteTypeStatsResponse
)
from app.services.dashboard import DashboardService

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    include_activities: bool = Query(False, description="최근 활동 포함 여부"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    대시보드 기본 통계 조회
    
    - 총 프로젝트 수
    - 총 노트 수  
    - 총 조회수
    - 총 좋아요 수
    - 최근 활동 (선택적)
    """
    dashboard_service = DashboardService(db)
    stats = await dashboard_service.get_user_stats(
        user_id=current_user.id,
        include_activities=include_activities
    )
    
    return DashboardStatsResponse(success=True, data=stats)


@router.get("/projects/stats", response_model=ProjectStatsResponse)
async def get_project_stats_by_period(
    period: str = Query("daily", description="통계 기간 (daily, weekly, monthly)"),
    days: int = Query(7, description="조회할 일수 (1-365)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 통계 조회 - 기간별
    
    - 일별/주별/월별 프로젝트 통계
    - 조회수, 좋아요, 노트 수 등
    """
    dashboard_service = DashboardService(db)
    stats = await dashboard_service.get_project_stats_by_period(
        user_id=current_user.id,
        period=period,
        days=days
    )
    
    return ProjectStatsResponse(success=True, data=stats)


@router.get("/activities", response_model=ActivityTimelineResponse)
async def get_activity_timeline(
    limit: int = Query(10, description="조회할 활동 수 (1-50)", ge=1, le=50),
    offset: int = Query(0, description="건너뛸 활동 수", ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    활동 타임라인 조회
    
    - 프로젝트 생성, 노트 추가 등의 활동
    - 시간 순 정렬
    - 페이지네이션 지원
    """
    dashboard_service = DashboardService(db)
    activities = await dashboard_service.get_activity_timeline(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return ActivityTimelineResponse(success=True, data=activities)


@router.get("/projects/popular", response_model=PopularProjectsResponse)
async def get_popular_projects(
    limit: int = Query(5, description="조회할 프로젝트 수 (1-20)", ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 프로젝트 통계
    
    - 조회수 기준 상위 프로젝트
    - 좋아요 수 포함
    """
    dashboard_service = DashboardService(db)
    popular_projects = await dashboard_service.get_popular_projects(
        user_id=current_user.id,
        limit=limit
    )
    
    return PopularProjectsResponse(success=True, data=popular_projects)


@router.get("/stats/tech-stack", response_model=TechStackStatsResponse)
async def get_tech_stack_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    기술 스택 분포 통계
    
    - 사용된 기술별 프로젝트 수
    - 비율 계산
    """
    dashboard_service = DashboardService(db)
    tech_distribution = await dashboard_service.get_tech_stack_distribution(
        user_id=current_user.id
    )
    
    return TechStackStatsResponse(success=True, data=tech_distribution)


@router.get("/stats/categories", response_model=CategoryStatsResponse)
async def get_category_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    카테고리 분포 통계
    
    - 카테고리별 프로젝트 수
    - 비율 계산
    """
    dashboard_service = DashboardService(db)
    category_distribution = await dashboard_service.get_category_distribution(
        user_id=current_user.id
    )
    
    return CategoryStatsResponse(success=True, data=category_distribution)


@router.get("/notes/stats", response_model=NoteTypeStatsResponse)
async def get_note_stats_by_type(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 타입별 통계
    
    - learn, change, research 타입별 노트 수
    - 최근 7일 추가된 노트 수
    - 비율 계산
    """
    dashboard_service = DashboardService(db)
    note_stats = await dashboard_service.get_note_stats_by_type(
        user_id=current_user.id
    )
    
    return NoteTypeStatsResponse(success=True, data=note_stats)