"""
노트 서비스
프로젝트별 노트 CRUD, 타입별 분류, 태그 관리
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc, Text
from sqlalchemy.orm import selectinload

from app.models.note import Note, NoteType
from app.models.project import Project
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    """노트 관련 비즈니스 로직"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_note(self, owner_id: int, note_data: NoteCreate) -> Note:
        """
        노트 생성
        
        Args:
            owner_id: 노트 소유자 ID
            note_data: 노트 생성 데이터
            
        Returns:
            Note: 생성된 노트
        """
        # 프로젝트 존재 확인 및 권한 검증
        if note_data.project_id:
            project_stmt = select(Project).where(Project.id == note_data.project_id)
            project_result = await self.db.execute(project_stmt)
            project = project_result.scalar_one_or_none()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            if project.owner_id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to create note in this project"
                )
        
        # 새 노트 생성
        note = Note(
            project_id=note_data.project_id,
            type=note_data.type,
            title=note_data.title,
            content=note_data.content,
            tags=note_data.tags or [],
            is_pinned=note_data.is_pinned,
            is_archived=note_data.is_archived,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note
    
    async def get_note_by_id(self, note_id: int, include_project: bool = False) -> Optional[Note]:
        """노트 ID로 조회"""
        stmt = select(Note).where(Note.id == note_id)
        
        if include_project:
            stmt = stmt.options(selectinload(Note.project))
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_notes(
        self,
        owner_id: int,
        project_id: Optional[int] = None,
        type: Optional[NoteType] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        노트 목록 조회 (필터링, 검색, 페이지네이션)
        
        Args:
            owner_id: 노트 소유자 ID (프로젝트 소유자 기준)
            project_id: 프로젝트 ID 필터
            type: 노트 타입 필터
            tags: 태그 필터 (OR 조건)
            search: 제목/내용 검색어
            is_pinned: 고정 노트 필터
            is_archived: 아카이브 노트 필터
            sort_by: 정렬 기준
            sort_order: 정렬 순서 (asc/desc)
            page: 페이지 번호
            page_size: 페이지 크기
            
        Returns:
            Dict: 노트 목록과 페이지네이션 정보
        """
        # 기본 쿼리 - 프로젝트와 조인하여 소유자 확인
        stmt = select(Note).join(Project).options(selectinload(Note.project))
        count_stmt = select(func.count(Note.id)).join(Project)
        
        # 필터 조건 구성
        filters = [Project.owner_id == owner_id]  # 소유자 필터는 필수
        
        if project_id is not None:
            filters.append(Note.project_id == project_id)
        
        if type is not None:
            filters.append(Note.type == type)
        
        if is_pinned is not None:
            filters.append(Note.is_pinned == is_pinned)
        
        if is_archived is not None:
            filters.append(Note.is_archived == is_archived)
        
        # 태그 필터 (ANY 연산자 사용)
        if tags:
            tag_conditions = [Note.tags.any(tag) for tag in tags]
            filters.append(or_(*tag_conditions))
        
        # 텍스트 검색 (제목, 내용에서 검색)
        if search:
            # JSONB 내용 검색을 위해 텍스트 변환
            search_condition = or_(
                Note.title.ilike(f"%{search}%"),
                func.cast(Note.content, Text).ilike(f"%{search}%")
            )
            filters.append(search_condition)
        
        # 필터 적용
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))
        
        # 정렬 (고정 노트가 항상 위에 오도록)
        sort_column = getattr(Note, sort_by, Note.updated_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(Note.is_pinned), desc(sort_column))
        else:
            stmt = stmt.order_by(desc(Note.is_pinned), asc(sort_column))
        
        # 전체 개수 조회
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # 페이지네이션 적용
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # 결과 조회
        result = await self.db.execute(stmt)
        notes = result.scalars().all()
        
        # 페이지네이션 메타데이터 계산
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "notes": notes,
            "pagination": {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
    
    async def update_note(self, note_id: int, note_data: NoteUpdate, owner_id: int) -> Note:
        """
        노트 수정
        
        Args:
            note_id: 노트 ID
            note_data: 수정할 데이터
            owner_id: 소유자 ID (권한 확인용)
            
        Returns:
            Note: 수정된 노트
        """
        # 노트 조회 및 권한 확인
        note = await self.get_note_by_id(note_id, include_project=True)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        if note.project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this note"
            )
        
        # 수정할 데이터 구성
        update_data = {}
        for field, value in note_data.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # updated_at 갱신
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # 업데이트 실행
        stmt = update(Note).where(Note.id == note_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
        
        # 수정된 노트 반환
        return await self.get_note_by_id(note_id, include_project=True)
    
    async def delete_note(self, note_id: int, owner_id: int) -> bool:
        """
        노트 삭제
        
        Args:
            note_id: 노트 ID
            owner_id: 소유자 ID (권한 확인용)
            
        Returns:
            bool: 삭제 성공 여부
        """
        # 노트 조회 및 권한 확인
        note = await self.get_note_by_id(note_id, include_project=True)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        if note.project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this note"
            )
        
        # 노트 삭제
        stmt = delete(Note).where(Note.id == note_id)
        await self.db.execute(stmt)
        await self.db.commit()
        
        return True
    
    async def get_note_stats(self, owner_id: int, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        노트 통계 조회
        
        Args:
            owner_id: 소유자 ID
            project_id: 특정 프로젝트의 통계만 조회 (None이면 전체)
            
        Returns:
            Dict: 노트 통계
        """
        base_filter = [Project.owner_id == owner_id]
        if project_id:
            base_filter.append(Note.project_id == project_id)
        
        # 전체 노트 수
        total_stmt = select(func.count(Note.id)).join(Project)
        total_stmt = total_stmt.where(and_(*base_filter))
        
        # 타입별 노트 수
        type_stmt = select(
            Note.type,
            func.count(Note.id).label('count')
        ).join(Project).group_by(Note.type)
        type_stmt = type_stmt.where(and_(*base_filter))
        
        # 상태별 노트 수
        status_stmt = select(
            func.count(Note.id).filter(Note.is_pinned == True).label('pinned_count'),
            func.count(Note.id).filter(Note.is_archived == True).label('archived_count'),
            func.count(Note.id).filter(and_(Note.is_pinned == False, Note.is_archived == False)).label('active_count')
        ).join(Project)
        status_stmt = status_stmt.where(and_(*base_filter))
        
        # 인기 태그 (상위 10개)
        tags_stmt = select(
            func.unnest(Note.tags).label('tag'),
            func.count('*').label('count')
        ).join(Project).group_by('tag').order_by(desc(func.count('*'))).limit(10)
        tags_stmt = tags_stmt.where(and_(*base_filter))
        
        # 쿼리 실행
        total_result = await self.db.execute(total_stmt)
        type_result = await self.db.execute(type_stmt)
        status_result = await self.db.execute(status_stmt)
        tags_result = await self.db.execute(tags_stmt)
        
        # 결과 가공
        total_count = total_result.scalar() or 0
        
        type_stats = {}
        for row in type_result:
            type_stats[row.type.value] = row.count
        
        status_data = status_result.first()
        status_stats = {
            "pinned": status_data.pinned_count or 0,
            "archived": status_data.archived_count or 0,
            "active": status_data.active_count or 0
        }
        
        popular_tags = []
        for row in tags_result:
            popular_tags.append({
                "tag": row.tag,
                "count": row.count
            })
        
        return {
            "total_notes": total_count,
            "by_type": type_stats,
            "by_status": status_stats,
            "popular_tags": popular_tags
        }
    
    async def toggle_pin(self, note_id: int, owner_id: int) -> Note:
        """노트 고정/해제 토글"""
        note = await self.get_note_by_id(note_id, include_project=True)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        if note.project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to pin/unpin this note"
            )
        
        # 고정 상태 토글
        new_pinned_state = not note.is_pinned
        stmt = update(Note).where(Note.id == note_id).values(
            is_pinned=new_pinned_state,
            updated_at=datetime.now(timezone.utc)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        return await self.get_note_by_id(note_id, include_project=True)
    
    async def toggle_archive(self, note_id: int, owner_id: int) -> Note:
        """노트 아카이브/복원 토글"""
        note = await self.get_note_by_id(note_id, include_project=True)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
        
        if note.project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to archive/restore this note"
            )
        
        # 아카이브 상태 토글
        new_archived_state = not note.is_archived
        stmt = update(Note).where(Note.id == note_id).values(
            is_archived=new_archived_state,
            updated_at=datetime.now(timezone.utc)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        return await self.get_note_by_id(note_id, include_project=True)