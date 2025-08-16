"""
검색 관련 스키마
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.schemas.project import Project as ProjectResponse
from app.schemas.note import Note as NoteResponse
from app.schemas.user import User as UserResponse


class SearchResponse(BaseModel):
    """전역 검색 응답"""
    projects: List[ProjectResponse] = []
    notes: List[NoteResponse] = []
    users: List[UserResponse] = []
    total_count: int
    query: str
    
    class Config:
        from_attributes = True


class AutocompleteResponse(BaseModel):
    """자동완성 응답"""
    query: str
    suggestions: List[str]
    type: str
    
    class Config:
        from_attributes = True


class PopularSearchItem(BaseModel):
    """인기 검색어 항목"""
    keyword: str
    count: int
    
    class Config:
        from_attributes = True


class PopularSearchResponse(BaseModel):
    """인기 검색어 응답"""
    popular_searches: List[PopularSearchItem]
    limit: int
    
    class Config:
        from_attributes = True


class SearchStatsResponse(BaseModel):
    """검색 통계 응답"""
    total_projects: int
    total_notes: int
    total_users: int
    indexable_content: int
    
    class Config:
        from_attributes = True