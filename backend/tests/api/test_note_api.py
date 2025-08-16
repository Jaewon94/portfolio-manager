"""
노트 API 테스트
노트 CRUD, 타입 필터링, 태그 기능, 검색 테스트
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.note import NoteType
from app.models.user import User
from app.services.auth import get_current_user


def create_mock_user():
    """테스트용 사용자 객체 생성"""
    user = User(
        id=1,
        email="test@example.com",
        name="Test User",
        github_username="testuser",
        is_verified=True
    )
    return user


def create_mock_note():
    """테스트용 노트 객체 생성"""
    from app.models.note import Note
    from datetime import datetime, timezone
    
    note = Note(
        id=1,
        project_id=1,
        type=NoteType.LEARN,
        title="Test Note",
        content={"type": "note", "blocks": [{"type": "paragraph", "content": "Test content"}]},
        tags=["Python", "FastAPI"],
        is_pinned=False,
        is_archived=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return note


def create_mock_project():
    """테스트용 프로젝트 객체 생성 (노트 관계를 위해)"""
    from app.models.project import Project
    from datetime import datetime, timezone
    
    project = Project(
        id=1,
        owner_id=1,
        slug="test-project",
        title="Test Project",
        description="Test project description"
    )
    return project


class TestNoteAPI:
    """노트 API 테스트 클래스"""
    
    def setup_auth_override(self, mock_user):
        """인증 의존성 오버라이드 설정"""
        def get_mock_user():
            return mock_user
        app.dependency_overrides[get_current_user] = get_mock_user
    
    def cleanup_auth_override(self):
        """인증 의존성 오버라이드 정리"""
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_create_note_success(self):
        """노트 생성 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                # 생성된 노트 모킹
                created_note = create_mock_note()
                MockService.return_value.create_note = AsyncMock(return_value=created_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/notes/",
                        json={
                            "project_id": 1,
                            "type": "learn",
                            "title": "Test Note",
                            "content": {"type": "note", "blocks": [{"type": "paragraph", "content": "Test content"}]},
                            "tags": ["Python", "FastAPI"],
                            "is_pinned": False,
                            "is_archived": False
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 201
                data = response.json()
                assert data["title"] == "Test Note"
                assert data["type"] == "learn"
                assert data["tags"] == ["Python", "FastAPI"]
                assert data["is_pinned"] == False
                assert data["is_archived"] == False
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_create_note_project_not_found(self):
        """노트 생성 실패 테스트 - 프로젝트 없음"""
        
        from fastapi import HTTPException
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹 - 프로젝트 없음 에러
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.create_note = AsyncMock(
                    side_effect=HTTPException(status_code=404, detail="Project not found")
                )
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/notes/",
                        json={
                            "project_id": 999,
                            "type": "learn",
                            "title": "Test Note",
                            "content": {"type": "note", "content": "Test content"}
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 404
                assert "Project not found" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_create_note_unauthorized(self):
        """노트 생성 실패 테스트 - 권한 없음 (다른 사용자의 프로젝트)"""
        
        from fastapi import HTTPException
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹 - 권한 없음 에러
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.create_note = AsyncMock(
                    side_effect=HTTPException(status_code=403, detail="Not authorized to create note in this project")
                )
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/notes/",
                        json={
                            "project_id": 1,
                            "type": "learn",
                            "title": "Test Note",
                            "content": {"type": "note", "content": "Test content"}
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 403
                assert "Not authorized" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_note_by_id_success(self):
        """노트 ID로 조회 성공 테스트"""
        
        mock_user = create_mock_user()
        mock_note = create_mock_note()
        mock_project = create_mock_project()
        mock_note.project = mock_project
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_note_by_id = AsyncMock(return_value=mock_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/notes/1")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == 1
                assert data["title"] == "Test Note"
                assert data["type"] == "learn"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_note_not_found(self):
        """노트 조회 실패 테스트 - 존재하지 않음"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹 - 노트 없음
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_note_by_id = AsyncMock(return_value=None)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/notes/999")
                
                # 응답 검증
                assert response.status_code == 404
                assert response.json()["detail"] == "Note not found"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_note_forbidden(self):
        """노트 조회 실패 테스트 - 권한 없음 (다른 사용자의 노트)"""
        
        mock_user = create_mock_user()
        mock_note = create_mock_note()
        mock_project = create_mock_project()
        mock_project.owner_id = 2  # 다른 사용자
        mock_note.project = mock_project
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_note_by_id = AsyncMock(return_value=mock_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/notes/1")
                
                # 응답 검증
                assert response.status_code == 403
                assert "Not authorized" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_notes_with_filters(self):
        """노트 목록 조회 (필터링) 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 딕셔너리 형태의 노트 데이터 (직렬화 가능)
            note_data = {
                "id": 1,
                "project_id": 1,
                "type": "learn",
                "title": "Test Note",
                "content": {"type": "note", "blocks": [{"type": "paragraph", "content": "Test content"}]},
                "tags": ["Python", "FastAPI"],
                "is_pinned": False,
                "is_archived": False,
                "created_at": "2024-08-16T12:00:00Z",
                "updated_at": "2024-08-16T12:00:00Z",
                "project": {
                    "id": 1,
                    "slug": "test-project",
                    "title": "Test Project"
                }
            }
            
            # 목록 응답 모킹
            notes_response = {
                "notes": [note_data],
                "pagination": {
                    "total_count": 1,
                    "total_pages": 1,
                    "current_page": 1,
                    "page_size": 20,
                    "has_next": False,
                    "has_prev": False
                }
            }
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_notes = AsyncMock(return_value=notes_response)
                
                # API 호출 (필터링 포함)
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/notes/",
                        params={
                            "project_id": 1,
                            "type": "learn",
                            "tags": ["Python", "FastAPI"],
                            "search": "Test",
                            "is_pinned": "false",
                            "is_archived": "false",
                            "sort_by": "updated_at",
                            "sort_order": "desc",
                            "page": 1,
                            "page_size": 20
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert len(data["notes"]) == 1
                assert data["pagination"]["total_count"] == 1
                assert data["notes"][0]["title"] == "Test Note"
                assert data["notes"][0]["type"] == "learn"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_update_note_success(self):
        """노트 수정 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 수정된 노트 모킹
            updated_note = create_mock_note()
            updated_note.title = "Updated Note"
            updated_note.content = {"type": "note", "blocks": [{"type": "paragraph", "content": "Updated content"}]}
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.update_note = AsyncMock(return_value=updated_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.put(
                        "/api/v1/notes/1",
                        json={
                            "title": "Updated Note",
                            "content": {"type": "note", "blocks": [{"type": "paragraph", "content": "Updated content"}]}
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["title"] == "Updated Note"
                assert data["content"]["blocks"][0]["content"] == "Updated content"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_delete_note_success(self):
        """노트 삭제 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.delete_note = AsyncMock(return_value=True)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.delete("/api/v1/notes/1")
                
                # 응답 검증
                assert response.status_code == 204
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_note_stats(self):
        """노트 통계 조회 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 통계 데이터 모킹
            stats_data = {
                "total_notes": 15,
                "by_type": {
                    "learn": 8,
                    "change": 4,
                    "research": 3
                },
                "by_status": {
                    "pinned": 2,
                    "archived": 1,
                    "active": 12
                },
                "popular_tags": [
                    {"tag": "Python", "count": 10},
                    {"tag": "FastAPI", "count": 8},
                    {"tag": "React", "count": 5}
                ]
            }
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_note_stats = AsyncMock(return_value=stats_data)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/notes/stats/overview")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["total_notes"] == 15
                assert data["by_type"]["learn"] == 8
                assert data["by_status"]["active"] == 12
                assert len(data["popular_tags"]) == 3
                assert data["popular_tags"][0]["tag"] == "Python"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_toggle_pin_note_success(self):
        """노트 고정/해제 토글 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 토글된 노트 모킹
            pinned_note = create_mock_note()
            pinned_note.is_pinned = True
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.toggle_pin = AsyncMock(return_value=pinned_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post("/api/v1/notes/1/pin")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["is_pinned"] == True
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_toggle_archive_note_success(self):
        """노트 아카이브/복원 토글 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 토글된 노트 모킹
            archived_note = create_mock_note()
            archived_note.is_archived = True
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.toggle_archive = AsyncMock(return_value=archived_note)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post("/api/v1/notes/1/archive")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["is_archived"] == True
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_notes_by_type(self):
        """노트 타입별 조회 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 타입별 노트 데이터
            learn_notes = [
                {
                    "id": 1,
                    "project_id": 1,
                    "type": "learn",
                    "title": "Python Learning",
                    "tags": ["Python", "Basics"]
                },
                {
                    "id": 2,
                    "project_id": 1,
                    "type": "learn",
                    "title": "FastAPI Learning",
                    "tags": ["FastAPI", "API"]
                }
            ]
            
            notes_response = {
                "notes": learn_notes,
                "pagination": {
                    "total_count": 2,
                    "total_pages": 1,
                    "current_page": 1,
                    "page_size": 20,
                    "has_next": False,
                    "has_prev": False
                }
            }
            
            # 서비스 모킹
            with patch('app.api.endpoints.notes.NoteService') as MockService:
                MockService.return_value.get_notes = AsyncMock(return_value=notes_response)
                
                # API 호출 (learn 타입만 조회)
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/notes/",
                        params={"type": "learn"}
                    )
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert len(data["notes"]) == 2
                assert data["pagination"]["total_count"] == 2
                assert all(note["type"] == "learn" for note in data["notes"])
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_note_validation_errors(self):
        """노트 유효성 검사 에러 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # API 호출 - 필수 필드 누락 (title)
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/notes/",
                    json={
                        "project_id": 1,
                        "type": "learn",
                        "content": {"type": "note", "content": "Test content"}
                        # title 누락
                    }
                )
            
            # 응답 검증
            assert response.status_code == 422  # Validation Error
            error_detail = response.json()["detail"]
            assert any("title" in str(error) for error in error_detail)
        
        finally:
            self.cleanup_auth_override()


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(pytest.main([__file__, "-v"]))