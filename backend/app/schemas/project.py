from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.project import ProjectStatus, ProjectVisibility


class ProjectBase(BaseModel):
    """프로젝트 기본 스키마 (ERD 명세 기준)"""

    slug: str = Field(..., max_length=100, description="URL friendly identifier")
    title: str = Field(..., max_length=200, description="프로젝트 제목")
    description: Optional[str] = Field(None, description="프로젝트 설명")
    content: Optional[Dict[str, Any]] = Field(None, description="프로젝트 상세 내용 (JSONB)")
    tech_stack: List[str] = Field(default=[], description="기술 스택 배열")
    categories: List[str] = Field(default=[], description="카테고리 배열")
    tags: List[str] = Field(default=[], description="태그 배열")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="프로젝트 상태")
    visibility: ProjectVisibility = Field(default=ProjectVisibility.PRIVATE, description="공개 설정")
    featured: bool = Field(default=False, description="추천 프로젝트 여부")


class ProjectCreate(ProjectBase):
    """프로젝트 생성 스키마"""

    pass


class ProjectUpdate(BaseModel):
    """프로젝트 수정 스키마"""

    slug: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    tech_stack: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
    visibility: Optional[ProjectVisibility] = None
    featured: Optional[bool] = None


class ProjectInDB(ProjectBase):
    """데이터베이스의 프로젝트 스키마"""

    id: int
    owner_id: int
    view_count: int
    like_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Project(ProjectBase):
    """프로젝트 응답 스키마"""

    id: int
    owner_id: int
    view_count: int
    like_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
