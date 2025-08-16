"""
프로젝트 API 테스트
프로젝트 CRUD, 검색, 필터링, 페이지네이션 테스트
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.project import ProjectStatus, ProjectVisibility
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


def create_mock_project():
    """테스트용 프로젝트 객체 생성"""
    from app.models.project import Project
    from datetime import datetime, timezone
    
    project = Project(
        id=1,
        owner_id=1,
        slug="test-project",
        title="Test Project",
        description="Test project description",
        content={"type": "project", "content": "Test content"},
        tech_stack=["Python", "FastAPI"],
        categories=["Backend"],
        tags=["API", "Test"],
        status=ProjectStatus.ACTIVE,
        visibility=ProjectVisibility.PUBLIC,
        featured=False,
        view_count=10,
        like_count=5,
        published_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    project.owner = create_mock_user()
    return project


class TestProjectAPI:
    """프로젝트 API 테스트 클래스"""
    
    def setup_auth_override(self, mock_user):
        """인증 의존성 오버라이드 설정"""
        def get_mock_user():
            return mock_user
        app.dependency_overrides[get_current_user] = get_mock_user
    
    def cleanup_auth_override(self):
        """인증 의존성 오버라이드 정리"""
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_create_project_success(self):
        """프로젝트 생성 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                # 생성된 프로젝트 모킹
                created_project = create_mock_project()
                MockService.return_value.create_project = AsyncMock(return_value=created_project)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/projects/",
                        json={
                            "slug": "test-project",
                            "title": "Test Project",
                            "description": "Test project description",
                            "content": {"type": "project", "content": "Test content"},
                            "tech_stack": ["Python", "FastAPI"],
                            "categories": ["Backend"],
                            "tags": ["API", "Test"],
                            "status": "active",
                            "visibility": "public",
                            "featured": False
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 201
                data = response.json()
                assert data["slug"] == "test-project"
                assert data["title"] == "Test Project"
                assert data["status"] == "active"
                assert data["visibility"] == "public"
                assert data["tech_stack"] == ["Python", "FastAPI"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_create_project_duplicate_slug(self):
        """프로젝트 생성 실패 테스트 - 중복 slug"""
        
        from fastapi import HTTPException
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹 - 중복 slug 에러
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.create_project = AsyncMock(
                    side_effect=HTTPException(status_code=400, detail="Project with slug 'test-project' already exists")
                )
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/projects/",
                        json={
                            "slug": "test-project",
                            "title": "Test Project",
                            "description": "Test project description"
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 400
                assert "already exists" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_project_by_id_success(self):
        """프로젝트 ID로 조회 성공 테스트"""
        
        mock_user = create_mock_user()
        mock_project = create_mock_project()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_by_id = AsyncMock(return_value=mock_project)
                MockService.return_value.increment_view_count = AsyncMock(return_value=True)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/projects/1")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == 1
                assert data["slug"] == "test-project"
                assert data["title"] == "Test Project"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self):
        """프로젝트 조회 실패 테스트 - 존재하지 않음"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹 - 프로젝트 없음
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_by_id = AsyncMock(return_value=None)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/projects/999")
                
                # 응답 검증
                assert response.status_code == 404
                assert response.json()["detail"] == "Project not found"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_project_forbidden(self):
        """프로젝트 조회 실패 테스트 - 권한 없음 (비공개 프로젝트)"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 다른 사용자의 비공개 프로젝트 생성
            private_project = create_mock_project()
            private_project.owner_id = 2  # 다른 사용자
            private_project.visibility = ProjectVisibility.PRIVATE
            
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_by_id = AsyncMock(return_value=private_project)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/projects/1")
                
                # 응답 검증
                assert response.status_code == 403
                assert "Not authorized" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_projects_with_filters(self):
        """프로젝트 목록 조회 (필터링) 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 딕셔너리 형태의 프로젝트 데이터 (직렬화 가능)
            project_data = {
                "id": 1,
                "owner_id": 1,
                "slug": "test-project",
                "title": "Test Project",
                "description": "Test project description",
                "content": {"type": "project", "content": "Test content"},
                "tech_stack": ["Python", "FastAPI"],
                "categories": ["Backend"],
                "tags": ["API", "Test"],
                "status": "active",
                "visibility": "public",
                "featured": False,
                "view_count": 10,
                "like_count": 5,
                "published_at": "2024-08-16T12:00:00Z",
                "created_at": "2024-08-16T12:00:00Z",
                "updated_at": "2024-08-16T12:00:00Z",
                "owner": {
                    "id": 1,
                    "email": "test@example.com",
                    "name": "Test User",
                    "github_username": "testuser",
                    "is_verified": True
                }
            }
            
            # 목록 응답 모킹 (직렬화 가능한 형태로)
            projects_response = {
                "projects": [project_data],
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
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_projects = AsyncMock(return_value=projects_response)
                
                # API 호출 (필터링 포함)
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/projects/",
                        params={
                            "status": "active",
                            "visibility": "public",
                            "featured": "false",
                            "tech_stack": ["Python", "FastAPI"],
                            "categories": ["Backend"],
                            "search": "Test",
                            "sort_by": "updated_at",
                            "sort_order": "desc",
                            "page": 1,
                            "page_size": 20
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert len(data["projects"]) == 1
                assert data["pagination"]["total_count"] == 1
                assert data["projects"][0]["slug"] == "test-project"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_update_project_success(self):
        """프로젝트 수정 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 수정된 프로젝트 모킹
            updated_project = create_mock_project()
            updated_project.title = "Updated Project"
            updated_project.description = "Updated description"
            
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.update_project = AsyncMock(return_value=updated_project)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.put(
                        "/api/v1/projects/1",
                        json={
                            "title": "Updated Project",
                            "description": "Updated description"
                        }
                    )
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["title"] == "Updated Project"
                assert data["description"] == "Updated description"
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_delete_project_success(self):
        """프로젝트 삭제 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.delete_project = AsyncMock(return_value=True)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.delete("/api/v1/projects/1")
                
                # 응답 검증
                assert response.status_code == 204
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_get_project_stats(self):
        """프로젝트 통계 조회 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 통계 데이터 모킹
            stats_data = {
                "total_projects": 5,
                "by_status": {
                    "draft": 1,
                    "active": 3,
                    "archived": 1,
                    "deleted": 0
                },
                "by_visibility": {
                    "public": 2,
                    "private": 3,
                    "unlisted": 0
                },
                "total_views": 150,
                "total_likes": 25
            }
            
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_stats = AsyncMock(return_value=stats_data)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.get("/api/v1/projects/stats/overview")
                
                # 응답 검증
                assert response.status_code == 200
                data = response.json()
                assert data["total_projects"] == 5
                assert data["by_status"]["active"] == 3
                assert data["total_views"] == 150
                assert data["total_likes"] == 25
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_increment_view_count_success(self):
        """조회수 증가 성공 테스트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 다른 사용자의 공개 프로젝트로 설정
            public_project = create_mock_project()
            public_project.owner_id = 2  # 다른 사용자
            public_project.visibility = ProjectVisibility.PUBLIC
            
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_by_id = AsyncMock(return_value=public_project)
                MockService.return_value.increment_view_count = AsyncMock(return_value=True)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post("/api/v1/projects/1/views")
                
                # 응답 검증
                assert response.status_code == 204
        
        finally:
            self.cleanup_auth_override()
    
    @pytest.mark.asyncio
    async def test_increment_view_count_own_project(self):
        """조회수 증가 실패 테스트 - 본인 프로젝트"""
        
        mock_user = create_mock_user()
        self.setup_auth_override(mock_user)
        
        try:
            # 본인 프로젝트로 설정
            own_project = create_mock_project()
            own_project.owner_id = 1  # 현재 사용자
            own_project.visibility = ProjectVisibility.PUBLIC
            
            # 서비스 모킹
            with patch('app.api.endpoints.projects.ProjectService') as MockService:
                MockService.return_value.get_project_by_id = AsyncMock(return_value=own_project)
                
                # API 호출
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post("/api/v1/projects/1/views")
                
                # 응답 검증
                assert response.status_code == 400
                assert "Cannot increment view count" in response.json()["detail"]
        
        finally:
            self.cleanup_auth_override()


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(pytest.main([__file__, "-v"]))