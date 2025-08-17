"""
GitHub 저장소 API 엔드포인트 테스트
FastAPI HTTP 요청/응답 테스트
"""

import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.project import Project
from app.models.github_repository import GithubRepository
from app.schemas.github import GithubRepositoryCreate, GithubRepositoryUpdate
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    ExternalAPIException
)


class TestGithubRepositoryAPI:
    """GitHub 저장소 API 엔드포인트 테스트"""
    
    @pytest.mark.asyncio
    async def test_create_github_repository_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 연동 생성 API 성공 테스트"""
        # Given
        request_data = {
            "github_url": "https://github.com/testuser/api-test-repo",
            "repository_name": "testuser/api-test-repo",
            "sync_enabled": True
        }
        
        # When
        response = await authenticated_client.post(
            f"/api/v1/projects/{test_project.id}/github",
            json=request_data
        )
        
        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        
        github_repo = data["data"]
        assert github_repo["project_id"] == test_project.id
        assert github_repo["github_url"] == request_data["github_url"]
        assert github_repo["repository_name"] == request_data["repository_name"]
        assert github_repo["sync_enabled"] == request_data["sync_enabled"]
        assert "id" in github_repo
        assert "created_at" in github_repo
        assert "updated_at" in github_repo
    
    @pytest.mark.asyncio
    async def test_create_github_repository_duplicate_url(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """중복된 GitHub URL로 저장소 연동 시 실패 테스트"""
        # Given - 첫 번째 저장소 생성
        request_data = {
            "github_url": "https://github.com/testuser/duplicate-api-repo",
            "repository_name": "testuser/duplicate-api-repo",
            "sync_enabled": True
        }
        
        # 첫 번째 생성
        await authenticated_client.post(
            f"/api/v1/projects/{test_project.id}/github",
            json=request_data
        )
        
        # When - 같은 URL로 다시 생성 시도
        response = await authenticated_client.post(
            f"/api/v1/projects/{test_project.id}/github",
            json=request_data
        )
        
        # Then
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "GitHub URL already exists" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_create_github_repository_invalid_url(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """잘못된 GitHub URL 형식으로 저장소 연동 시 실패 테스트"""
        # Given
        request_data = {
            "github_url": "https://not-github.com/user/repo",
            "repository_name": "user/repo",
            "sync_enabled": True
        }
        
        # When
        response = await authenticated_client.post(
            f"/api/v1/projects/{test_project.id}/github",
            json=request_data
        )
        
        # Then
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "GitHub URL" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_create_github_repository_project_not_found(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User
    ):
        """존재하지 않는 프로젝트에 GitHub 저장소 연동 시 실패 테스트"""
        # Given
        non_existent_project_id = 99999
        request_data = {
            "github_url": "https://github.com/testuser/test-repo",
            "repository_name": "testuser/test-repo",
            "sync_enabled": True
        }
        
        # When
        response = await authenticated_client.post(
            f"/api/v1/projects/{non_existent_project_id}/github",
            json=request_data
        )
        
        # Then
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Project not found" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_create_github_repository_unauthorized_project(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        admin_user: User
    ):
        """다른 사용자의 프로젝트에 GitHub 저장소 연동 시 실패 테스트"""
        # Given - 다른 사용자의 프로젝트 생성
        from app.models.project import Project, ProjectStatus, ProjectVisibility
        
        other_project = Project(
            owner_id=admin_user.id,
            slug="other-user-project",
            title="Other User Project",
            description="Other user's project",
            content={"sections": []},
            tech_stack=["Python"],
            categories=["Backend"],
            tags=["test"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            featured=False,
        )
        test_db.add(other_project)
        await test_db.commit()
        await test_db.refresh(other_project)
        
        request_data = {
            "github_url": "https://github.com/testuser/unauthorized-repo",
            "repository_name": "testuser/unauthorized-repo",
            "sync_enabled": True
        }
        
        # When
        response = await authenticated_client.post(
            f"/api/v1/projects/{other_project.id}/github",
            json=request_data
        )
        
        # Then
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert "Not authorized" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_github_repository_by_project_id(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """프로젝트 ID로 GitHub 저장소 조회 API 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/get-test-repo",
            repository_name="testuser/get-test-repo",
            sync_enabled=True,
            stars=50,
            forks=10,
            watchers=75,
            language="Python",
            license="MIT",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # When
        response = await authenticated_client.get(
            f"/api/v1/projects/{test_project.id}/github"
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        repo_data = data["data"]
        assert repo_data["id"] == github_repo.id
        assert repo_data["project_id"] == test_project.id
        assert repo_data["github_url"] == github_repo.github_url
        assert repo_data["repository_name"] == github_repo.repository_name
        assert repo_data["stars"] == 50
        assert repo_data["forks"] == 10
        assert repo_data["watchers"] == 75
        assert repo_data["language"] == "Python"
        assert repo_data["license"] == "MIT"
    
    @pytest.mark.asyncio
    async def test_get_github_repository_not_found(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소가 연동되지 않은 프로젝트 조회 시 404 테스트"""
        # When
        response = await authenticated_client.get(
            f"/api/v1/projects/{test_project.id}/github"
        )
        
        # Then
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "GitHub repository not found" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_update_github_repository_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 정보 업데이트 API 성공 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/update-test-repo",
            repository_name="testuser/update-test-repo",
            sync_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # When
        update_data = {
            "github_url": "https://github.com/testuser/updated-api-repo",
            "sync_enabled": False
        }
        
        response = await authenticated_client.patch(
            f"/api/v1/projects/{test_project.id}/github",
            json=update_data
        )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        updated_repo = data["data"]
        assert updated_repo["id"] == github_repo.id
        assert updated_repo["github_url"] == update_data["github_url"]
        assert updated_repo["repository_name"] == "testuser/updated-api-repo"
        assert updated_repo["sync_enabled"] == update_data["sync_enabled"]
    
    @pytest.mark.asyncio
    async def test_delete_github_repository_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 연동 해제 API 성공 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/delete-test-repo",
            repository_name="testuser/delete-test-repo",
            sync_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # When
        response = await authenticated_client.delete(
            f"/api/v1/projects/{test_project.id}/github"
        )
        
        # Then
        assert response.status_code == 204
        
        # 삭제 확인
        get_response = await authenticated_client.get(
            f"/api/v1/projects/{test_project.id}/github"
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 동기화 API 성공 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/sync-test-repo",
            repository_name="testuser/sync-test-repo",
            sync_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # Mock GitHub API 응답
        mock_github_data = {
            "name": "sync-test-repo",
            "full_name": "testuser/sync-test-repo",
            "stargazers_count": 100,
            "forks_count": 25,
            "watchers_count": 125,
            "language": "Python",
            "license": {"name": "MIT"},
            "private": False,
            "fork": False,
            "default_branch": "main"
        }
        
        # When
        with patch('app.services.github.GithubRepositoryService._fetch_github_data', 
                  return_value=mock_github_data):
            response = await authenticated_client.post(
                f"/api/v1/projects/{test_project.id}/github/sync"
            )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        synced_repo = data["data"]
        assert synced_repo["id"] == github_repo.id
        assert synced_repo["stars"] == 100
        assert synced_repo["forks"] == 25
        assert synced_repo["watchers"] == 125
        assert synced_repo["language"] == "Python"
        assert synced_repo["license"] == "MIT"
        assert synced_repo["last_synced_at"] is not None
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_api_failure(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub API 실패 시 동기화 API 실패 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/api-failure-repo",
            repository_name="testuser/api-failure-repo",
            sync_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # When
        with patch('app.services.github.GithubRepositoryService._fetch_github_data',
                  side_effect=ExternalAPIException("GitHub API rate limit exceeded")):
            response = await authenticated_client.post(
                f"/api/v1/projects/{test_project.id}/github/sync"
            )
        
        # Then
        assert response.status_code == 502
        data = response.json()
        assert data["success"] is False
        assert "GitHub API" in data["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_get_commit_history_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 커밋 히스토리 조회 API 성공 테스트"""
        # Given - GitHub 저장소 생성
        github_repo = GithubRepository(
            project_id=test_project.id,
            github_url="https://github.com/testuser/commit-history-repo",
            repository_name="testuser/commit-history-repo",
            sync_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(github_repo)
        await test_db.commit()
        await test_db.refresh(github_repo)
        
        # Mock 커밋 데이터
        mock_commits = [
            {
                "sha": "abc123def456",
                "commit": {
                    "message": "Initial commit",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2024-01-01T00:00:00Z"
                    }
                },
                "html_url": "https://github.com/testuser/commit-history-repo/commit/abc123def456"
            },
            {
                "sha": "def456ghi789",
                "commit": {
                    "message": "Add feature",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2024-01-02T00:00:00Z"
                    }
                },
                "html_url": "https://github.com/testuser/commit-history-repo/commit/def456ghi789"
            }
        ]
        
        # When
        with patch('app.services.github.GithubRepositoryService._fetch_commits',
                  return_value=mock_commits):
            response = await authenticated_client.get(
                f"/api/v1/projects/{test_project.id}/github/commits",
                params={"limit": 10}
            )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        commits = data["data"]
        assert len(commits) == 2
        
        # 첫 번째 커밋 확인
        first_commit = commits[0]
        assert first_commit["sha"] == "abc123def456"
        assert first_commit["message"] == "Initial commit"
        assert first_commit["author_name"] == "Test User"
        assert first_commit["author_email"] == "test@example.com"
        
        # 두 번째 커밋 확인
        second_commit = commits[1]
        assert second_commit["sha"] == "def456ghi789"
        assert second_commit["message"] == "Add feature"
    
    @pytest.mark.asyncio
    async def test_bulk_sync_repositories_success(
        self,
        authenticated_client: AsyncClient,
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """여러 GitHub 저장소 일괄 동기화 API 성공 테스트"""
        # Given - 추가 프로젝트 및 GitHub 저장소들 생성
        from app.models.project import Project, ProjectStatus, ProjectVisibility
        
        # 추가 프로젝트 생성
        project2 = Project(
            owner_id=test_user.id,
            slug="bulk-sync-project-2",
            title="Bulk Sync Project 2",
            description="Test project for bulk sync",
            content={"sections": []},
            tech_stack=["Python"],
            categories=["Backend"],
            tags=["test"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            featured=False,
        )
        test_db.add(project2)
        await test_db.commit()
        await test_db.refresh(project2)
        
        # GitHub 저장소들 생성
        repos = []
        for i, project in enumerate([test_project, project2]):
            github_repo = GithubRepository(
                project_id=project.id,
                github_url=f"https://github.com/testuser/bulk-sync-repo-{i}",
                repository_name=f"testuser/bulk-sync-repo-{i}",
                sync_enabled=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            test_db.add(github_repo)
            repos.append(github_repo)
        
        await test_db.commit()
        for repo in repos:
            await test_db.refresh(repo)
        
        # Mock GitHub API 응답
        def mock_fetch_github_data(repo_name):
            return {
                "name": repo_name.split('/')[-1],
                "full_name": repo_name,
                "stargazers_count": 100,
                "forks_count": 20,
                "watchers_count": 150,
                "language": "Python",
                "license": {"name": "MIT"},
                "private": False,
                "fork": False
            }
        
        # When
        request_data = {
            "project_ids": [test_project.id, project2.id]
        }
        
        with patch('app.services.github.GithubRepositoryService._fetch_github_data',
                  side_effect=mock_fetch_github_data):
            response = await authenticated_client.post(
                "/api/v1/github/bulk-sync",
                json=request_data
            )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        results = data["data"]
        assert len(results) == 2
        
        # 모든 결과가 성공인지 확인
        for result in results:
            assert result["success"] is True
            assert result["project_id"] in [test_project.id, project2.id]
            assert "last_synced_at" in result
            assert "repository_id" in result
    
    @pytest.mark.asyncio
    async def test_unauthenticated_access(
        self,
        async_client: AsyncClient,
        test_db: AsyncSession,
        test_project: Project
    ):
        """인증되지 않은 사용자의 GitHub 저장소 API 접근 차단 테스트"""
        # When & Then - 인증 토큰 없이 API 호출
        endpoints = [
            ("POST", f"/api/v1/projects/{test_project.id}/github", {"github_url": "https://github.com/test/repo"}),
            ("GET", f"/api/v1/projects/{test_project.id}/github", None),
            ("PATCH", f"/api/v1/projects/{test_project.id}/github", {"sync_enabled": False}),
            ("DELETE", f"/api/v1/projects/{test_project.id}/github", None),
            ("POST", f"/api/v1/projects/{test_project.id}/github/sync", None),
            ("GET", f"/api/v1/projects/{test_project.id}/github/commits", None),
        ]
        
        for method, url, json_data in endpoints:
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json=json_data)
            elif method == "PATCH":
                response = await async_client.patch(url, json=json_data)
            elif method == "DELETE":
                response = await async_client.delete(url)
            
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "authentication" in data["error"]["message"].lower()