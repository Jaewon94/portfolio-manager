from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .user import User
    from .note import Note


class ProjectStatus(enum.Enum):
    """프로젝트 상태"""

    PLANNING = "planning"  # 기획
    IN_PROGRESS = "in_progress"  # 진행 중
    COMPLETED = "completed"  # 완료
    ON_HOLD = "on_hold"  # 중단
    CANCELLED = "cancelled"  # 취소


class ProjectType(enum.Enum):
    """프로젝트 타입"""

    WEB = "web"  # 웹 애플리케이션
    MOBILE = "mobile"  # 모바일 앱
    DESKTOP = "desktop"  # 데스크톱 앱
    API = "api"  # API/백엔드
    LIBRARY = "library"  # 라이브러리/패키지
    OTHER = "other"  # 기타


class Project(Base, TimestampMixin):
    """프로젝트 모델"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 프로젝트 속성
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False
    )
    project_type: Mapped[ProjectType] = mapped_column(
        SQLEnum(ProjectType), default=ProjectType.WEB, nullable=False
    )

    # 기술 스택 (JSON으로 저장)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # URL 정보
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 소유자 정보
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # 관계 설정
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Project(id={self.id}, title={self.title}, status={self.status.value})>"
        )
