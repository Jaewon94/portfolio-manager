"""
프로젝트 서비스
프로젝트 CRUD, 검색, 필터링, 페이지네이션
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """프로젝트 관련 비즈니스 로직"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, owner_id: int, project_data: ProjectCreate) -> Project:
        """
        프로젝트 생성
        
        Args:
            owner_id: 프로젝트 소유자 ID
            project_data: 프로젝트 생성 데이터
            
        Returns:
            Project: 생성된 프로젝트
        """
        # slug 중복 확인 (같은 소유자 내에서)
        stmt = select(Project).where(
            Project.owner_id == owner_id,
            Project.slug == project_data.slug
        )
        result = await self.db.execute(stmt)
        existing_project = result.scalar_one_or_none()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with slug '{project_data.slug}' already exists"
            )
        
        # 새 프로젝트 생성
        project = Project(
            owner_id=owner_id,
            slug=project_data.slug,
            title=project_data.title,
            description=project_data.description,
            content=project_data.content,
            tech_stack=project_data.tech_stack,
            categories=project_data.categories,
            tags=project_data.tags,
            status=project_data.status,
            visibility=project_data.visibility,
            featured=project_data.featured,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # 프로젝트가 활성화되고 공개인 경우 published_at 설정
        if project.status == ProjectStatus.ACTIVE and project.visibility == ProjectVisibility.PUBLIC:
            project.published_at = datetime.now(timezone.utc)
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def get_project_by_id(self, project_id: int, include_owner: bool = False) -> Optional[Project]:
        """프로젝트 ID로 조회"""
        stmt = select(Project).where(Project.id == project_id)
        
        if include_owner:
            stmt = stmt.options(selectinload(Project.owner))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_project_by_slug(self, owner_id: int, slug: str, include_owner: bool = False) -> Optional[Project]:
        """소유자 ID와 slug로 조회"""
        stmt = select(Project).where(
            Project.owner_id == owner_id,
            Project.slug == slug
        )
        
        if include_owner:
            stmt = stmt.options(selectinload(Project.owner))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_projects(
        self,
        owner_id: Optional[int] = None,
        status: Optional[ProjectStatus] = None,
        visibility: Optional[ProjectVisibility] = None,
        featured: Optional[bool] = None,
        tech_stack: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        프로젝트 목록 조회 (필터링, 검색, 페이지네이션)
        
        Args:
            owner_id: 소유자 ID 필터
            status: 프로젝트 상태 필터
            visibility: 공개 설정 필터
            featured: 추천 프로젝트 필터
            tech_stack: 기술 스택 필터 (OR 조건)
            categories: 카테고리 필터 (OR 조건)
            tags: 태그 필터 (OR 조건)
            search: 제목/설명 검색어
            sort_by: 정렬 기준
            sort_order: 정렬 순서 (asc/desc)
            page: 페이지 번호
            page_size: 페이지 크기
            
        Returns:
            Dict: 프로젝트 목록과 페이지네이션 정보
        """
        # 기본 쿼리
        stmt = select(Project).options(selectinload(Project.owner))
        count_stmt = select(func.count(Project.id))
        
        # 필터 조건 구성
        filters = []
        
        if owner_id is not None:
            filters.append(Project.owner_id == owner_id)
        
        if status is not None:
            filters.append(Project.status == status)
        
        if visibility is not None:
            filters.append(Project.visibility == visibility)
        
        if featured is not None:
            filters.append(Project.featured == featured)
        
        # 배열 필터 (ANY 연산자 사용)
        if tech_stack:
            tech_conditions = [Project.tech_stack.any(tech) for tech in tech_stack]
            filters.append(or_(*tech_conditions))
        
        if categories:
            category_conditions = [Project.categories.any(cat) for cat in categories]
            filters.append(or_(*category_conditions))
        
        if tags:
            tag_conditions = [Project.tags.any(tag) for tag in tags]
            filters.append(or_(*tag_conditions))
        
        # 텍스트 검색 (제목, 설명에서 검색)
        if search:
            search_condition = or_(
                Project.title.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
            filters.append(search_condition)
        
        # 필터 적용
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        
        # 정렬
        sort_column = getattr(Project, sort_by, Project.updated_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(asc(sort_column))
        
        # 전체 개수 조회
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # 페이지네이션 적용
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # 결과 조회
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        
        # 페이지네이션 메타데이터 계산
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "projects": projects,
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate, owner_id: int) -> Project:
        """
        프로젝트 수정
        
        Args:
            project_id: 프로젝트 ID
            project_data: 수정할 데이터
            owner_id: 소유자 ID (권한 확인용)
            
        Returns:
            Project: 수정된 프로젝트
        """
        # 프로젝트 조회 및 권한 확인
        project = await self.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this project"
            )
        
        # slug 변경 시 중복 확인
        if project_data.slug and project_data.slug != project.slug:
            stmt = select(Project).where(
                Project.owner_id == owner_id,
                Project.slug == project_data.slug,
                Project.id != project_id
            )
            result = await self.db.execute(stmt)
            existing_project = result.scalar_one_or_none()
            
            if existing_project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Project with slug '{project_data.slug}' already exists"
                )
        
        # 수정할 데이터 구성
        update_data = {}
        for field, value in project_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # published_at 처리
        if (project_data.status == ProjectStatus.ACTIVE and 
            project_data.visibility == ProjectVisibility.PUBLIC and 
            not project.published_at):
            update_data["published_at"] = datetime.now(timezone.utc)
        elif (project_data.status and project_data.status != ProjectStatus.ACTIVE) or \
             (project_data.visibility and project_data.visibility != ProjectVisibility.PUBLIC):
            # 비활성화되거나 비공개로 변경되면 published_at 제거
            update_data["published_at"] = None
        
        # updated_at 갱신
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # 업데이트 실행
        stmt = update(Project).where(Project.id == project_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
        
        # 수정된 프로젝트 반환
        return await self.get_project_by_id(project_id, include_owner=True)
    
    async def delete_project(self, project_id: int, owner_id: int) -> bool:
        """
        프로젝트 삭제
        
        Args:
            project_id: 프로젝트 ID
            owner_id: 소유자 ID (권한 확인용)
            
        Returns:
            bool: 삭제 성공 여부
        """
        # 프로젝트 조회 및 권한 확인
        project = await self.get_project_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )
        
        # 프로젝트 삭제 (연관 데이터도 cascade로 함께 삭제됨)
        stmt = delete(Project).where(Project.id == project_id)
        await self.db.execute(stmt)
        await self.db.commit()
        
        return True
    
    async def increment_view_count(self, project_id: int) -> bool:
        """프로젝트 조회수 증가"""
        stmt = update(Project).where(Project.id == project_id).values(
            view_count=Project.view_count + 1
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return True
    
    async def get_project_stats(self, owner_id: Optional[int] = None) -> Dict[str, Any]:
        """
        프로젝트 통계 조회
        
        Args:
            owner_id: 특정 소유자의 통계만 조회 (None이면 전체)
            
        Returns:
            Dict: 프로젝트 통계
        """
        base_filter = []
        if owner_id:
            base_filter.append(Project.owner_id == owner_id)
        
        # 전체 프로젝트 수
        total_stmt = select(func.count(Project.id))
        if base_filter:
            total_stmt = total_stmt.where(and_(*base_filter))
        
        # 상태별 프로젝트 수
        status_stmt = select(
            Project.status,
            func.count(Project.id).label('count')
        ).group_by(Project.status)
        if base_filter:
            status_stmt = status_stmt.where(and_(*base_filter))
        
        # 공개 설정별 프로젝트 수
        visibility_stmt = select(
            Project.visibility,
            func.count(Project.id).label('count')
        ).group_by(Project.visibility)
        if base_filter:
            visibility_stmt = visibility_stmt.where(and_(*base_filter))
        
        # 전체 조회수/좋아요 수
        metrics_stmt = select(
            func.sum(Project.view_count).label('total_views'),
            func.sum(Project.like_count).label('total_likes')
        )
        if base_filter:
            metrics_stmt = metrics_stmt.where(and_(*base_filter))
        
        # 쿼리 실행
        total_result = await self.db.execute(total_stmt)
        status_result = await self.db.execute(status_stmt)
        visibility_result = await self.db.execute(visibility_stmt)
        metrics_result = await self.db.execute(metrics_stmt)
        
        # 결과 가공
        total_count = total_result.scalar() or 0
        
        status_stats = {}
        for row in status_result:
            status_stats[row.status.value] = row.count
        
        visibility_stats = {}
        for row in visibility_result:
            visibility_stats[row.visibility.value] = row.count
        
        metrics = metrics_result.first()
        total_views = metrics.total_views or 0
        total_likes = metrics.total_likes or 0
        
        return {
            "total_projects": total_count,
            "by_status": status_stats,
            "by_visibility": visibility_stats,
            "total_views": total_views,
            "total_likes": total_likes
        }