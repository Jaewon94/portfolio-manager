from typing import Optional, List
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectType

class ProjectBase(BaseModel):
    """프로젝트 기본 스키마"""
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    project_type: ProjectType = ProjectType.WEB
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None

class ProjectCreate(ProjectBase):
    """프로젝트 생성 스키마"""
    pass

class ProjectUpdate(BaseModel):
    """프로젝트 수정 스키마"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    project_type: Optional[ProjectType] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None

class ProjectInDB(ProjectBase):
    """데이터베이스의 프로젝트 스키마"""
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Project(ProjectBase):
    """프로젝트 응답 스키마"""
    id: int
    owner_id: int

    class Config:
        from_attributes = True