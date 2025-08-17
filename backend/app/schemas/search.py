"""
검색 관련 스키마
"""

from typing import Any, Dict, List, Optional

from app.schemas.note import Note as NoteResponse
from app.schemas.project import Project as ProjectResponse
from app.schemas.user import User as UserResponse
from pydantic import BaseModel, ConfigDict


class SearchResponse(BaseModel):
    """전역 검색 응답"""

    projects: List[ProjectResponse] = []
    notes: List[NoteResponse] = []
    users: List[UserResponse] = []
    total_count: int
    query: str

    model_config = ConfigDict(from_attributes=True)


class AutocompleteResponse(BaseModel):
    """자동완성 응답"""

    query: str
    suggestions: List[str]
    type: str

    model_config = ConfigDict(from_attributes=True)


class PopularSearchItem(BaseModel):
    """인기 검색어 항목"""

    keyword: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class PopularSearchResponse(BaseModel):
    """인기 검색어 응답"""

    popular_searches: List[PopularSearchItem]
    limit: int

    model_config = ConfigDict(from_attributes=True)


class SearchStatsResponse(BaseModel):
    """검색 통계 응답"""

    total_projects: int
    total_notes: int
    total_users: int
    indexable_content: int

    model_config = ConfigDict(from_attributes=True)
