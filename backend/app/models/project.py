from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, Boolean, Integer, DateTime, ARRAY, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
import enum

if TYPE_CHECKING:
    from .user import User
    from .note import Note
    from .github_repository import GithubRepository


class ProjectStatus(enum.Enum):
    """프로젝트 상태 (ERD 명세 기준)"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectVisibility(enum.Enum):
    """프로젝트 공개 설정 (ERD 명세 기준)"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class Project(Base, TimestampMixin):
    """
    포트폴리오 프로젝트 모델
    CLAUDE.md 명세: (id, owner_id, slug, title, description, content[JSONB], tech_stack[], categories[], tags[], status, visibility, featured, view_count, like_count)
    """

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint('owner_id', 'slug', name='uq_owner_slug'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 기본 정보
    slug: Mapped[str] = mapped_column(String(100), nullable=False)  # URL friendly identifier
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # 프로젝트 상세 내용
    
    # 프로젝트 메타데이터 (PostgreSQL 배열 사용)
    tech_stack: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    categories: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    
    # 프로젝트 설정
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False
    )
    visibility: Mapped[ProjectVisibility] = mapped_column(
        SQLEnum(ProjectVisibility), default=ProjectVisibility.PRIVATE, nullable=False
    )
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 통계 및 메트릭
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 타임스탬프 (published_at은 ERD 명세 추가)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # 관계 설정
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    notes: Mapped[List["Note"]] = relationship(
        "Note", back_populates="project", cascade="all, delete-orphan"
    )
    # 1:1 관계 - GitHub 저장소 (선택적)
    github_repository: Mapped[Optional["GithubRepository"]] = relationship(
        "GithubRepository", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, slug={self.slug}, title={self.title}, status={self.status.value})>"

    @property
    def is_public(self) -> bool:
        """공개 프로젝트 여부"""
        return self.visibility == ProjectVisibility.PUBLIC

    @property
    def is_published(self) -> bool:
        """게시된 프로젝트 여부"""
        return self.status == ProjectStatus.ACTIVE and self.published_at is not None
