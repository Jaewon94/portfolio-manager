from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .project import Project

class NoteType(enum.Enum):
    """노트 타입"""
    GENERAL = "general"         # 일반 노트
    BUG = "bug"                # 버그 리포트
    FEATURE = "feature"         # 기능 아이디어
    TODO = "todo"              # 할 일
    MEETING = "meeting"         # 회의록
    RESEARCH = "research"       # 조사/연구

class Note(Base, TimestampMixin):
    """노트 모델"""
    __tablename__ = "notes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 노트 속성
    note_type: Mapped[NoteType] = mapped_column(
        SQLEnum(NoteType), 
        default=NoteType.GENERAL, 
        nullable=False
    )
    
    # 태그 (콤마로 구분된 문자열)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 프로젝트 연결
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # 관계 설정
    project: Mapped["Project"] = relationship("Project", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, type={self.note_type.value})>"