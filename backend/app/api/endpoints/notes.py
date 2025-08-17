"""
노트 API 엔드포인트
프로젝트별 노트 CRUD, 타입별 분류, 태그 관리
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.models.note import NoteType
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.services.note import NoteService

router = APIRouter()


@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 생성
    
    - **project_id**: 프로젝트 ID (노트가 속할 프로젝트)
    - **type**: 노트 타입 (learn/change/research)
    - **title**: 노트 제목
    - **content**: 노트 내용 (JSONB)
    - **tags**: 태그 배열
    - **is_pinned**: 고정 노트 여부
    - **is_archived**: 아카이브 여부
    """
    service = NoteService(db)
    note = await service.create_note(current_user.id, note_data)
    return note


@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 상세 조회
    
    - 노트가 속한 프로젝트의 소유자만 조회 가능
    """
    service = NoteService(db)
    note = await service.get_note_by_id(note_id, include_project=True)
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # 권한 확인: 프로젝트 소유자만 접근 가능
    if note.project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this note"
        )
    
    return note


@router.get("/", response_model=Dict[str, Any])
async def get_notes(
    # 필터 매개변수
    project_id: Optional[int] = Query(None, description="프로젝트 ID 필터"),
    type: Optional[NoteType] = Query(None, description="노트 타입 필터"),
    tags: Optional[List[str]] = Query(None, description="태그 필터 (OR 조건)"),
    search: Optional[str] = Query(None, description="제목/내용 검색어"),
    is_pinned: Optional[bool] = Query(None, description="고정 노트 필터"),
    is_archived: Optional[bool] = Query(None, description="아카이브 노트 필터"),
    
    # 정렬 매개변수
    sort_by: str = Query("updated_at", description="정렬 기준 (created_at, updated_at, title)"),
    sort_order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    
    # 페이지네이션 매개변수
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 목록 조회 (필터링, 검색, 페이지네이션)
    
    **필터링 옵션:**
    - **project_id**: 특정 프로젝트의 노트만 조회
    - **type**: 노트 타입별 필터 (learn/change/research)
    - **tags**: 태그 배열 (OR 조건으로 매칭)
    - **search**: 제목/내용에서 텍스트 검색
    - **is_pinned**: 고정 노트만 조회
    - **is_archived**: 아카이브 노트 포함/제외
    
    **정렬 옵션:**
    - **sort_by**: created_at, updated_at, title
    - **sort_order**: asc (오름차순), desc (내림차순)
    - 고정 노트는 항상 상단에 표시
    
    **페이지네이션:**
    - **page**: 페이지 번호 (1부터 시작)
    - **page_size**: 페이지 크기 (최대 100)
    
    **권한:**
    - 현재 사용자가 소유한 프로젝트의 노트만 조회 가능
    """
    service = NoteService(db)
    
    result = await service.get_notes(
        owner_id=current_user.id,
        project_id=project_id,
        type=type,
        tags=tags,
        search=search,
        is_pinned=is_pinned,
        is_archived=is_archived,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    return result


@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 수정
    
    - 노트가 속한 프로젝트의 소유자만 수정 가능
    """
    service = NoteService(db)
    note = await service.update_note(note_id, note_data, current_user.id)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 삭제
    
    - 노트가 속한 프로젝트의 소유자만 삭제 가능
    """
    service = NoteService(db)
    await service.delete_note(note_id, current_user.id)


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_note_stats(
    project_id: Optional[int] = Query(None, description="특정 프로젝트의 통계 (없으면 전체)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 통계 조회
    
    **통계 항목:**
    - 전체 노트 수
    - 타입별 노트 수
    - 상태별 노트 수 (고정, 아카이브, 활성)
    - 인기 태그 (상위 10개)
    
    **권한:**
    - 현재 사용자의 노트 통계만 조회 가능
    """
    service = NoteService(db)
    stats = await service.get_note_stats(current_user.id, project_id)
    return stats


@router.post("/{note_id}/pin", response_model=Note)
async def toggle_pin_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 고정/해제 토글
    
    - 고정된 노트는 목록에서 항상 상단에 표시
    - 노트가 속한 프로젝트의 소유자만 실행 가능
    """
    service = NoteService(db)
    note = await service.toggle_pin(note_id, current_user.id)
    return note


@router.post("/{note_id}/archive", response_model=Note)
async def toggle_archive_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    노트 아카이브/복원 토글
    
    - 아카이브된 노트는 기본 목록에서 숨겨짐
    - is_archived=true 필터로 조회 가능
    - 노트가 속한 프로젝트의 소유자만 실행 가능
    """
    service = NoteService(db)
    note = await service.toggle_archive(note_id, current_user.id)
    return note