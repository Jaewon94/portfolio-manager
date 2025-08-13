from typing import Optional
from pydantic import BaseModel
from app.models.note import NoteType

class NoteBase(BaseModel):
    """노트 기본 스키마"""
    title: str
    content: str
    note_type: NoteType = NoteType.GENERAL
    tags: Optional[str] = None

class NoteCreate(NoteBase):
    """노트 생성 스키마"""
    project_id: int

class NoteUpdate(BaseModel):
    """노트 수정 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[NoteType] = None
    tags: Optional[str] = None

class NoteInDB(NoteBase):
    """데이터베이스의 노트 스키마"""
    id: int
    project_id: int

    class Config:
        from_attributes = True

class Note(NoteBase):
    """노트 응답 스키마"""
    id: int
    project_id: int

    class Config:
        from_attributes = True