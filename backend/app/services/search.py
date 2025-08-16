"""
검색 서비스
PostgreSQL full-text search, 자동완성, 필터링
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text, desc
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.note import Note, NoteType
from app.models.user import User


class SearchService:
    """검색 관련 비즈니스 로직"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_all(
        self,
        query: str,
        user_id: Optional[int] = None,
        categories: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,  # ["project", "note", "user"]
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        전역 검색 (프로젝트, 노트, 사용자)
        
        Args:
            query: 검색어
            user_id: 검색 요청 사용자 (권한 확인용)
            categories: 검색 카테고리 필터
            content_types: 검색할 콘텐츠 타입
            limit: 결과 제한
            offset: 오프셋
            
        Returns:
            Dict: 검색 결과
        """
        results = {
            "projects": [],
            "notes": [],
            "users": [],
            "total_count": 0,
            "query": query
        }
        
        # 기본적으로 모든 타입 검색
        if not content_types:
            content_types = ["project", "note", "user"]
        
        # 프로젝트 검색
        if "project" in content_types:
            project_results = await self._search_projects(
                query, user_id, categories, limit, offset
            )
            results["projects"] = project_results["projects"]
            results["total_count"] += project_results["count"]
        
        # 노트 검색
        if "note" in content_types:
            note_results = await self._search_notes(
                query, user_id, limit, offset
            )
            results["notes"] = note_results["notes"]
            results["total_count"] += note_results["count"]
        
        # 사용자 검색
        if "user" in content_types:
            user_results = await self._search_users(
                query, limit, offset
            )
            results["users"] = user_results["users"]
            results["total_count"] += user_results["count"]
        
        return results
    
    async def _search_projects(
        self,
        query: str,
        user_id: Optional[int] = None,
        categories: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """프로젝트 전문 검색"""
        
        # 텍스트 검색 (기본 LIKE 검색으로 시작)
        search_conditions = []
        
        # 제목, 설명, 태그에서 검색
        if query:
            search_conditions.extend([
                Project.title.ilike(f'%{query}%'),
                Project.description.ilike(f'%{query}%'),
                func.array_to_string(Project.tags, ' ').ilike(f'%{query}%')
            ])
        
        # 기본 쿼리
        stmt = select(Project).options(selectinload(Project.owner))
        count_stmt = select(func.count(Project.id))
        
        # 필터 조건
        filters = []
        
        # 공개 프로젝트만 검색 (본인 프로젝트는 비공개도 포함)
        if user_id:
            visibility_filter = or_(
                Project.visibility == ProjectVisibility.PUBLIC,
                and_(
                    Project.owner_id == user_id,
                    Project.visibility.in_([ProjectVisibility.PUBLIC, ProjectVisibility.PRIVATE])
                )
            )
        else:
            visibility_filter = Project.visibility == ProjectVisibility.PUBLIC
        
        filters.append(visibility_filter)
        filters.append(Project.status == ProjectStatus.ACTIVE)
        
        # 텍스트 검색 조건 (OR 조건으로 연결)
        if search_conditions:
            filters.append(or_(*search_conditions))
        
        # 카테고리 필터
        if categories:
            category_conditions = [Project.categories.any(cat) for cat in categories]
            filters.append(or_(*category_conditions))
        
        # 필터 적용
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))
        
        # 제목 기준 정렬 (기본)
        stmt = stmt.order_by(Project.title)
        
        # 페이지네이션
        stmt = stmt.offset(offset).limit(limit)
        
        # 실행
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        result = await self.db.execute(stmt)
        projects = result.scalars().all()
        
        return {
            "projects": projects,
            "count": total_count
        }
    
    async def _search_notes(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """노트 전문 검색"""
        
        # 텍스트 검색 (기본 LIKE 검색)
        search_conditions = []
        
        # 제목, 태그에서 검색 (콘텐츠 검색은 임시로 제외)
        if query:
            search_conditions.extend([
                Note.title.ilike(f'%{query}%'),
                # func.cast(Note.content, text('TEXT')).ilike(f'%{query}%'),  # 임시로 제외
                func.array_to_string(Note.tags, ' ').ilike(f'%{query}%')
            ])
        
        # 프로젝트와 조인하여 권한 확인
        stmt = select(Note).join(Project).options(
            selectinload(Note.project).selectinload(Project.owner)
        )
        count_stmt = select(func.count(Note.id)).join(Project)
        
        # 필터 조건
        filters = []
        
        # 접근 권한 필터
        if user_id:
            access_filter = or_(
                and_(
                    Project.visibility == ProjectVisibility.PUBLIC,
                    Project.status == ProjectStatus.ACTIVE
                ),
                Project.owner_id == user_id  # 본인 노트는 모두 접근 가능
            )
        else:
            access_filter = and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            )
        
        filters.append(access_filter)
        filters.append(Note.is_archived == False)  # 아카이브된 노트 제외
        
        # 텍스트 검색 조건 (OR 조건으로 연결)
        if search_conditions:
            filters.append(or_(*search_conditions))
        
        # 필터 적용
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))
        
        # 제목 기준 정렬 (기본)
        stmt = stmt.order_by(Note.title)
        
        # 페이지네이션
        stmt = stmt.offset(offset).limit(limit)
        
        # 실행
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        result = await self.db.execute(stmt)
        notes = result.scalars().all()
        
        return {
            "notes": notes,
            "count": total_count
        }
    
    async def _search_users(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """사용자 검색 (공개 프로필만)"""
        
        # 텍스트 검색 (기본 LIKE 검색)
        search_conditions = []
        
        # 이름, GitHub 사용자명, 바이오에서 검색
        if query:
            search_conditions.extend([
                User.name.ilike(f'%{query}%'),
                User.github_username.ilike(f'%{query}%'),
                User.bio.ilike(f'%{query}%')
            ])
        
        # 기본 쿼리
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # 필터 조건
        filters = [User.is_verified == True]  # 인증된 사용자만
        
        # 텍스트 검색 조건 (OR 조건으로 연결)
        if search_conditions:
            filters.append(or_(*search_conditions))
        
        # 필터 적용
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))
        
        # 이름 기준 정렬 (기본)
        stmt = stmt.order_by(User.name)
        
        # 페이지네이션
        stmt = stmt.offset(offset).limit(limit)
        
        # 실행
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        
        return {
            "users": users,
            "count": total_count
        }
    
    async def get_autocomplete_suggestions(
        self,
        query: str,
        content_type: str = "all",  # "all", "project", "note", "tag"
        limit: int = 10
    ) -> List[str]:
        """
        자동완성 제안
        
        Args:
            query: 검색어 (부분)
            content_type: 자동완성 타입
            limit: 제안 개수
            
        Returns:
            List[str]: 자동완성 제안 목록
        """
        suggestions = []
        
        if content_type in ["all", "project"]:
            # 프로젝트 제목 자동완성
            project_suggestions = await self._get_project_title_suggestions(query, limit)
            suggestions.extend(project_suggestions)
        
        if content_type in ["all", "note"]:
            # 노트 제목 자동완성
            note_suggestions = await self._get_note_title_suggestions(query, limit)
            suggestions.extend(note_suggestions)
        
        if content_type in ["all", "tag"]:
            # 태그 자동완성
            tag_suggestions = await self._get_tag_suggestions(query, limit)
            suggestions.extend(tag_suggestions)
        
        # 중복 제거 및 관련도 순 정렬
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:limit]
    
    async def _get_project_title_suggestions(self, query: str, limit: int) -> List[str]:
        """프로젝트 제목 자동완성"""
        stmt = select(Project.title).where(
            and_(
                Project.title.ilike(f"%{query}%"),
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            )
        ).order_by(Project.title).limit(limit)
        
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
    
    async def _get_note_title_suggestions(self, query: str, limit: int) -> List[str]:
        """노트 제목 자동완성"""
        stmt = select(Note.title).join(Project).where(
            and_(
                Note.title.ilike(f"%{query}%"),
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE,
                Note.is_archived == False
            )
        ).order_by(Note.title).limit(limit)
        
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
    
    async def _get_tag_suggestions(self, query: str, limit: int) -> List[str]:
        """태그 자동완성"""
        # 프로젝트 태그
        project_tags_stmt = select(
            func.unnest(Project.tags).label('tag')
        ).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            )
        )
        
        # 노트 태그
        note_tags_stmt = select(
            func.unnest(Note.tags).label('tag')
        ).join(Project).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE,
                Note.is_archived == False
            )
        )
        
        # UNION으로 태그 통합 후 필터링
        union_stmt = project_tags_stmt.union(note_tags_stmt).subquery()
        
        # 서브쿼리로 감싸서 필터링 및 집계
        final_stmt = select(
            union_stmt.c.tag,
            func.count('*').label('count')
        ).where(
            union_stmt.c.tag.ilike(f"%{query}%")
        ).group_by(
            union_stmt.c.tag
        ).order_by(
            desc(func.count('*'))
        ).limit(limit)
        
        result = await self.db.execute(final_stmt)
        return [row[0] for row in result.fetchall()]
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 검색어 조회 (태그 기반)"""
        # 프로젝트와 노트의 모든 태그 집계
        project_tags = select(
            func.unnest(Project.tags).label('tag')
        ).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            )
        )
        
        note_tags = select(
            func.unnest(Note.tags).label('tag')
        ).join(Project).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE,
                Note.is_archived == False
            )
        )
        
        # 태그 통합 및 집계
        union_stmt = project_tags.union_all(note_tags).subquery()
        
        final_stmt = select(
            union_stmt.c.tag,
            func.count('*').label('count')
        ).group_by(
            union_stmt.c.tag
        ).order_by(
            desc(func.count('*'))
        ).limit(limit)
        
        result = await self.db.execute(final_stmt)
        
        return [
            {"keyword": row[0], "count": row[1]}
            for row in result.fetchall()
        ]
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """검색 통계 조회"""
        # 전체 공개 콘텐츠 수
        project_count_stmt = select(func.count(Project.id)).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            )
        )
        
        note_count_stmt = select(func.count(Note.id)).join(Project).where(
            and_(
                Project.visibility == ProjectVisibility.PUBLIC,
                Project.status == ProjectStatus.ACTIVE,
                Note.is_archived == False
            )
        )
        
        user_count_stmt = select(func.count(User.id)).where(
            User.is_verified == True
        )
        
        # 실행
        project_count_result = await self.db.execute(project_count_stmt)
        note_count_result = await self.db.execute(note_count_stmt)
        user_count_result = await self.db.execute(user_count_stmt)
        
        # 결과 값 추출
        total_projects = project_count_result.scalar()
        total_notes = note_count_result.scalar()
        total_users = user_count_result.scalar()
        
        return {
            "total_projects": total_projects,
            "total_notes": total_notes,
            "total_users": total_users,
            "indexable_content": total_projects + total_notes
        }