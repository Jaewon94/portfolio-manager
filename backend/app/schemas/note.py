from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.note import NoteType


class NoteBase(BaseModel):
    """노트 기본 스키마 (ERD 명세 기준)"""

    title: str = Field(..., max_length=200, description="노트 제목")
    content: Dict[str, Any] = Field(..., description="노트 내용 (JSONB - Markdown 또는 구조화된 콘텐츠)")
    type: NoteType = Field(..., description="노트 타입 (learn|change|research)")
    tags: List[str] = Field(default=[], description="태그 배열")
    is_pinned: bool = Field(default=False, description="고정 여부")
    is_archived: bool = Field(default=False, description="아카이브 여부")


class NoteCreate(NoteBase):
    """노트 생성 스키마"""

    project_id: int = Field(..., description="프로젝트 ID")


class NoteUpdate(BaseModel):
    """노트 수정 스키마"""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[Dict[str, Any]] = None
    type: Optional[NoteType] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteInDB(NoteBase):
    """데이터베이스의 노트 스키마"""

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Note(NoteBase):
    """노트 응답 스키마"""

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
