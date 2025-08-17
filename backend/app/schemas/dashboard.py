"""
대시보드 통계 스키마
Dashboard statistics schemas
"""

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator


class ActivityItem(BaseModel):
    """활동 항목"""

    id: int
    type: Literal[
        "project_created",
        "project_updated",
        "project_deleted",
        "note_added",
        "note_updated",
        "note_deleted",
        "media_uploaded",
    ]
    title: str
    description: str
    created_at: datetime
    metadata: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """대시보드 기본 통계"""

    total_projects: int = Field(..., ge=0, description="전체 프로젝트 수")
    total_notes: int = Field(..., ge=0, description="전체 노트 수")
    total_views: int = Field(..., ge=0, description="전체 조회수")
    total_likes: int = Field(..., ge=0, description="전체 좋아요 수")
    recent_activities: List[ActivityItem] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TechStackDistribution(BaseModel):
    """기술 스택 분포"""

    name: str
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)

    @validator("percentage")
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v


class CategoryDistribution(BaseModel):
    """카테고리 분포"""

    name: str
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=100)

    @validator("percentage")
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v


class NoteTypeStatDetail(BaseModel):
    """노트 타입별 상세 통계"""

    count: int = Field(..., ge=0)
    recent_count: int = Field(..., ge=0, description="최근 7일간 생성된 수")
    percentage: float = Field(..., ge=0, le=100)


class NoteTypeStats(BaseModel):
    """노트 타입별 통계"""

    by_type: Dict[str, Dict[str, Any]]  # 더 유연한 구조로 변경
    total: int = Field(..., ge=0)

    class Config:
        from_attributes = True


class DateRangeStats(BaseModel):
    """날짜별 통계"""

    date: date
    project_count: int = Field(..., ge=0)
    view_count: int = Field(..., ge=0)
    like_count: int = Field(..., ge=0)
    note_count: int = Field(..., ge=0)

    class Config:
        from_attributes = True


class PopularProject(BaseModel):
    """인기 프로젝트"""

    id: int
    title: str
    slug: str
    view_count: int = Field(..., ge=0)
    like_count: int = Field(..., ge=0)
    trend: Literal["up", "down", "stable"]
    trend_percentage: float = Field(default=0.0)

    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    """프로젝트 통계"""

    stats_by_date: List[DateRangeStats] = Field(default_factory=list)
    total_projects: int = Field(..., ge=0)
    total_views: int = Field(..., ge=0)
    total_likes: int = Field(..., ge=0)

    class Config:
        from_attributes = True


class ActivityTimeline(BaseModel):
    """활동 타임라인"""

    items: List[ActivityItem] = Field(default_factory=list)
    total: int = Field(..., ge=0)
    has_more: bool = False

    class Config:
        from_attributes = True


class TechStackStatsData(BaseModel):
    """기술 스택 통계 데이터"""

    distribution: List[TechStackDistribution] = Field(default_factory=list)
    total_projects: int = Field(..., ge=0)

    class Config:
        from_attributes = True


class CategoryStatsData(BaseModel):
    """카테고리 통계 데이터"""

    distribution: List[CategoryDistribution] = Field(default_factory=list)
    total_projects: int = Field(..., ge=0)

    class Config:
        from_attributes = True


# Response Models
class DashboardStatsResponse(BaseModel):
    """대시보드 통계 응답"""

    success: bool = True
    data: DashboardStats
    message: Optional[str] = None


class ProjectStatsResponse(BaseModel):
    """프로젝트 통계 응답"""

    success: bool = True
    data: ProjectStats
    message: Optional[str] = None


class ActivityTimelineResponse(BaseModel):
    """활동 타임라인 응답"""

    success: bool = True
    data: ActivityTimeline
    message: Optional[str] = None


class PopularProjectsData(BaseModel):
    """인기 프로젝트 데이터"""

    items: List[PopularProject] = Field(default_factory=list)

    class Config:
        from_attributes = True


class PopularProjectsResponse(BaseModel):
    """인기 프로젝트 응답"""

    success: bool = True
    data: PopularProjectsData
    message: Optional[str] = None


class TechStackStatsResponse(BaseModel):
    """기술 스택 통계 응답"""

    success: bool = True
    data: TechStackStatsData
    message: Optional[str] = None


class CategoryStatsResponse(BaseModel):
    """카테고리 통계 응답"""

    success: bool = True
    data: CategoryStatsData
    message: Optional[str] = None


class NoteTypeStatsResponse(BaseModel):
    """노트 타입별 통계 응답"""

    success: bool = True
    data: NoteTypeStats
    message: Optional[str] = None
