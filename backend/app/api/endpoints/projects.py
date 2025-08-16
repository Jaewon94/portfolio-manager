"""
프로젝트 API 엔드포인트
프로젝트 CRUD, 검색, 필터링, 페이지네이션
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import get_current_user
from app.models.user import User
from app.models.project import ProjectStatus, ProjectVisibility
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter()


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 생성
    
    - **slug**: URL friendly identifier (소유자 내에서 유니크)
    - **title**: 프로젝트 제목
    - **description**: 프로젝트 설명 (선택적)
    - **content**: 프로젝트 상세 내용 (JSONB)
    - **tech_stack**: 기술 스택 배열
    - **categories**: 카테고리 배열
    - **tags**: 태그 배열
    - **status**: 프로젝트 상태 (draft/active/archived/deleted)
    - **visibility**: 공개 설정 (public/private/unlisted)
    - **featured**: 추천 프로젝트 여부
    """
    service = ProjectService(db)
    project = await service.create_project(current_user.id, project_data)
    return project


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 상세 조회 (ID 기준)
    
    - 프로젝트 소유자이거나 공개 프로젝트인 경우만 조회 가능
    - 공개 프로젝트 조회 시 조회수 자동 증가
    """
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id, include_owner=True)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 권한 확인: 소유자이거나 공개 프로젝트인 경우만 접근 가능
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    # 공개 프로젝트이고 소유자가 아닌 경우 조회수 증가
    if project.is_public and project.owner_id != current_user.id:
        await service.increment_view_count(project_id)
        # 조회수 증가 후 프로젝트 정보 다시 조회
        project = await service.get_project_by_id(project_id, include_owner=True)
    
    return project


@router.get("/slug/{owner_id}/{slug}", response_model=Project)
async def get_project_by_slug(
    owner_id: int,
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 상세 조회 (소유자 ID + slug 기준)
    
    - 프로젝트 소유자이거나 공개 프로젝트인 경우만 조회 가능
    - 공개 프로젝트 조회 시 조회수 자동 증가
    """
    service = ProjectService(db)
    project = await service.get_project_by_slug(owner_id, slug, include_owner=True)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 권한 확인: 소유자이거나 공개 프로젝트인 경우만 접근 가능
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project"
        )
    
    # 공개 프로젝트이고 소유자가 아닌 경우 조회수 증가
    if project.is_public and project.owner_id != current_user.id:
        await service.increment_view_count(project.id)
        # 조회수 증가 후 프로젝트 정보 다시 조회
        project = await service.get_project_by_slug(owner_id, slug, include_owner=True)
    
    return project


@router.get("/", response_model=Dict[str, Any])
async def get_projects(
    # 필터 매개변수
    owner_id: Optional[int] = Query(None, description="소유자 ID 필터"),
    status: Optional[ProjectStatus] = Query(None, description="프로젝트 상태 필터"),
    visibility: Optional[ProjectVisibility] = Query(None, description="공개 설정 필터"),
    featured: Optional[bool] = Query(None, description="추천 프로젝트 필터"),
    tech_stack: Optional[List[str]] = Query(None, description="기술 스택 필터 (OR 조건)"),
    categories: Optional[List[str]] = Query(None, description="카테고리 필터 (OR 조건)"),
    tags: Optional[List[str]] = Query(None, description="태그 필터 (OR 조건)"),
    search: Optional[str] = Query(None, description="제목/설명 검색어"),
    
    # 정렬 매개변수
    sort_by: str = Query("updated_at", description="정렬 기준 (created_at, updated_at, title, view_count, like_count)"),
    sort_order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    
    # 페이지네이션 매개변수
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 목록 조회 (필터링, 검색, 페이지네이션)
    
    **필터링 옵션:**
    - **owner_id**: 특정 소유자의 프로젝트만 조회
    - **status**: 프로젝트 상태별 필터
    - **visibility**: 공개 설정별 필터
    - **featured**: 추천 프로젝트만 조회
    - **tech_stack**: 기술 스택 배열 (OR 조건으로 매칭)
    - **categories**: 카테고리 배열 (OR 조건으로 매칭)
    - **tags**: 태그 배열 (OR 조건으로 매칭)
    - **search**: 제목/설명에서 텍스트 검색
    
    **정렬 옵션:**
    - **sort_by**: created_at, updated_at, title, view_count, like_count
    - **sort_order**: asc (오름차순), desc (내림차순)
    
    **페이지네이션:**
    - **page**: 페이지 번호 (1부터 시작)
    - **page_size**: 페이지 크기 (최대 100)
    
    **권한:**
    - 소유자가 아닌 경우 공개 프로젝트만 조회 가능
    - owner_id 필터가 없는 경우 현재 사용자의 프로젝트만 조회
    """
    service = ProjectService(db)
    
    # 권한 확인: owner_id가 지정되지 않은 경우 현재 사용자의 프로젝트만 조회
    if owner_id is None:
        owner_id = current_user.id
    elif owner_id != current_user.id:
        # 다른 사용자의 프로젝트를 조회하는 경우 공개 프로젝트만 보이도록 설정
        visibility = ProjectVisibility.PUBLIC
    
    result = await service.get_projects(
        owner_id=owner_id,
        status=status,
        visibility=visibility,
        featured=featured,
        tech_stack=tech_stack,
        categories=categories,
        tags=tags,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    return result


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 수정
    
    - 프로젝트 소유자만 수정 가능
    - slug 변경 시 소유자 내에서 중복 확인
    - status/visibility 변경 시 published_at 자동 관리
    """
    service = ProjectService(db)
    project = await service.update_project(project_id, project_data, current_user.id)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 삭제
    
    - 프로젝트 소유자만 삭제 가능
    - 연관된 노트, GitHub 저장소 정보도 함께 삭제 (CASCADE)
    """
    service = ProjectService(db)
    await service.delete_project(project_id, current_user.id)


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_project_stats(
    owner_id: Optional[int] = Query(None, description="특정 소유자의 통계 (없으면 전체)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 통계 조회
    
    **통계 항목:**
    - 전체 프로젝트 수
    - 상태별 프로젝트 수
    - 공개 설정별 프로젝트 수
    - 전체 조회수/좋아요 수
    
    **권한:**
    - owner_id가 없는 경우: 전체 통계 (관리자용)
    - owner_id가 있는 경우: 해당 소유자 또는 본인의 통계만 조회 가능
    """
    service = ProjectService(db)
    
    # 권한 확인: 특정 소유자의 통계를 요청한 경우 본인 또는 관리자만 조회 가능
    if owner_id is not None and owner_id != current_user.id:
        # TODO: 관리자 권한 확인 로직 추가
        # 현재는 본인 통계만 조회 가능하도록 제한
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view other user's statistics"
        )
    
    # owner_id가 없는 경우 현재 사용자의 통계 조회
    if owner_id is None:
        owner_id = current_user.id
    
    stats = await service.get_project_stats(owner_id)
    return stats


@router.post("/{project_id}/views", status_code=status.HTTP_204_NO_CONTENT)
async def increment_view_count(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    프로젝트 조회수 증가
    
    - 공개 프로젝트만 조회수 증가 가능
    - 소유자 본인의 조회는 카운트하지 않음
    """
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 공개 프로젝트가 아니거나 소유자 본인인 경우 조회수 증가 안함
    if not project.is_public or project.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot increment view count for this project"
        )
    
    await service.increment_view_count(project_id)