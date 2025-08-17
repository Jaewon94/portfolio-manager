from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base, TimestampMixin
from typing import TYPE_CHECKING, List
import enum

if TYPE_CHECKING:
    from .project import Project


class NoteType(enum.Enum):
    """좌측 탭 기반 노트 타입 (ERD 명세 기준)"""
    LEARN = "learn"        # 학습 탭
    CHANGE = "change"      # 변경 탭  
    RESEARCH = "research"  # 조사 탭


class Note(Base, TimestampMixin):
    """
    좌측 탭 기반 노트 모델
    CLAUDE.md 명세: (id, project_id, type[learn|change|research], title, content[JSONB], tags[], is_pinned, is_archived)
    """

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # 노트 기본 정보
    type: Mapped[NoteType] = mapped_column(SQLEnum(NoteType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Markdown 또는 구조화된 콘텐츠
    
    # 태그 (PostgreSQL 배열 사용)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    
    # 메타데이터
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 관계 설정
    project: Mapped["Project"] = relationship("Project", back_populates="notes")

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, type={self.type.value})>"

    @property
    def is_learn_note(self) -> bool:
        """학습 노트 여부"""
        return self.type == NoteType.LEARN

    @property
    def is_change_note(self) -> bool:
        """변경 노트 여부"""
        return self.type == NoteType.CHANGE

    @property
    def is_research_note(self) -> bool:
        """조사 노트 여부"""
        return self.type == NoteType.RESEARCH
