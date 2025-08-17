"""
GitHub 저장소 관련 통합 테스트
실제 데이터베이스와의 상호작용 테스트
"""

import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.github import GithubRepositoryService
from app.schemas.github import GithubRepositoryCreate, GithubRepositoryUpdate
from app.models.github_repository import GithubRepository
from app.models.project import Project
from app.models.user import User
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    ExternalAPIException
)


class TestGithubRepositoryIntegration:
    """GitHub 저장소 서비스 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_create_github_repository_with_real_db(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """실제 데이터베이스에 GitHub 저장소 생성 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/integration-test-repo",
            repository_name="testuser/integration-test-repo",
            sync_enabled=True
        )
        
        # When
        result = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # Then
        assert result is not None
        assert result.id is not None
        assert result.project_id == test_project.id
        assert result.github_url == str(create_data.github_url)
        assert result.repository_name == create_data.repository_name
        assert result.sync_enabled == create_data.sync_enabled
        assert result.created_at is not None
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_duplicate_github_repository(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """중복된 GitHub URL로 저장소 생성 시 예외 발생 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        github_url = "https://github.com/testuser/duplicate-test-repo"
        create_data = GithubRepositoryCreate(
            github_url=github_url,
            repository_name="testuser/duplicate-test-repo",
            sync_enabled=True
        )
        
        # 첫 번째 저장소 생성
        await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # When & Then - 같은 URL로 다시 생성 시도
        with pytest.raises(DuplicateException) as exc_info:
            await service.create_github_repository(
                project_id=test_project.id,
                data=create_data
            )
        
        assert "GitHub URL already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_github_repository_by_project_id(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """프로젝트 ID로 GitHub 저장소 조회 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/project-lookup-repo",
            repository_name="testuser/project-lookup-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # When
        result = await service.get_by_project_id(test_project.id)
        
        # Then
        assert result is not None
        assert result.id == created_repo.id
        assert result.project_id == test_project.id
        assert result.github_url == created_repo.github_url
    
    @pytest.mark.asyncio
    async def test_get_github_repository_by_id(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """ID로 GitHub 저장소 조회 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/id-lookup-repo",
            repository_name="testuser/id-lookup-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # When
        result = await service.get_by_id(created_repo.id)
        
        # Then
        assert result is not None
        assert result.id == created_repo.id
        assert result.project_id == test_project.id
        assert result.github_url == created_repo.github_url
    
    @pytest.mark.asyncio
    async def test_update_github_repository(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 정보 업데이트 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/update-test-repo",
            repository_name="testuser/update-test-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # 시간 차이를 보장하기 위해 잠시 대기
        import time
        time.sleep(0.001)  # 1ms 대기
        
        # When
        update_data = GithubRepositoryUpdate(
            github_url="https://github.com/testuser/updated-repo",
            sync_enabled=False
        )
        
        result = await service.update_repository(created_repo.id, update_data)
        
        # Then
        assert result is not None
        assert result.id == created_repo.id
        assert result.github_url == str(update_data.github_url)
        assert result.repository_name == "testuser/updated-repo"  # URL에서 자동 추출
        assert result.sync_enabled == update_data.sync_enabled
        assert result.updated_at >= created_repo.updated_at  # 시간이 같거나 더 클 수 있음
    
    @pytest.mark.asyncio
    async def test_delete_github_repository(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 삭제 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/delete-test-repo",
            repository_name="testuser/delete-test-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # When
        result = await service.delete_repository(created_repo.id)
        
        # Then
        assert result is True
        
        # 삭제 확인
        deleted_repo = await service.get_by_id(created_repo.id)
        assert deleted_repo is None
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_with_mock_api(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub API 모킹을 통한 저장소 동기화 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/sync-test-repo",
            repository_name="testuser/sync-test-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # Mock GitHub API 응답
        mock_github_data = {
            "name": "sync-test-repo",
            "full_name": "testuser/sync-test-repo",
            "stargazers_count": 50,
            "forks_count": 10,
            "watchers_count": 75,
            "language": "Python",
            "license": {"name": "MIT"},
            "private": False,
            "fork": False,
            "default_branch": "main"
        }
        
        # When
        with patch.object(service, '_fetch_github_data', return_value=mock_github_data):
            result = await service.sync_repository(created_repo.id)
        
        # Then
        assert result is not None
        assert result.id == created_repo.id
        assert result.stars == 50
        assert result.forks == 10
        assert result.watchers == 75
        assert result.language == "Python"
        assert result.license == "MIT"
        assert result.is_private is False
        assert result.is_fork is False
        assert result.last_synced_at is not None
        assert result.sync_error_message is None
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_api_failure(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub API 실패 시 에러 메시지 저장 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/api-failure-repo",
            repository_name="testuser/api-failure-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
        # When & Then
        with patch.object(service, '_fetch_github_data', 
                         side_effect=ExternalAPIException("API rate limit exceeded")):
            with pytest.raises(ExternalAPIException) as exc_info:
                await service.sync_repository(created_repo.id)
            
            assert "GitHub API rate limit exceeded" in str(exc_info.value)
        
        # 에러 메시지가 저장되었는지 확인
        updated_repo = await service.get_by_id(created_repo.id)
        assert updated_repo.sync_error_message is not None
        assert "API rate limit exceeded" in updated_repo.sync_error_message
        assert updated_repo.last_synced_at is not None
    
    @pytest.mark.asyncio
    async def test_bulk_sync_repositories(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """여러 GitHub 저장소 일괄 동기화 통합 테스트"""
        # Given
        from app.models.project import Project, ProjectStatus, ProjectVisibility
        
        service = GithubRepositoryService(test_db)
        
        # 추가 프로젝트들 생성
        additional_projects = []
        for i in range(2):
            project = Project(
                owner_id=test_user.id,
                slug=f"bulk-test-project-{i+1}",
                title=f"Bulk Test Project {i+1}",
                description=f"Test project for bulk sync {i+1}",
                content={"sections": []},
                tech_stack=["Python"],
                categories=["Backend"],
                tags=["test"],
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC,
                featured=False,
            )
            test_db.add(project)
            await test_db.commit()
            await test_db.refresh(project)
            additional_projects.append(project)
        
        # 전체 프로젝트 목록 (기존 test_project + 새로 생성한 프로젝트들)
        all_projects = [test_project] + additional_projects
        repos = []
        
        # 각 프로젝트에 하나씩 GitHub 저장소 생성
        for i, project in enumerate(all_projects):
            create_data = GithubRepositoryCreate(
                github_url=f"https://github.com/testuser/bulk-sync-repo-{i}",
                repository_name=f"testuser/bulk-sync-repo-{i}",
                sync_enabled=True
            )
            
            repo = await service.create_github_repository(
                project_id=project.id,
                data=create_data
            )
            repos.append(repo)
        
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
        project_ids = [project.id for project in all_projects]
        
        with patch.object(service, '_fetch_github_data', side_effect=mock_fetch_github_data):
            results = await service.bulk_sync_repositories(project_ids)
        
        # Then
        assert len(results) == 3  # 3개 프로젝트 모두 성공
        
        # 모든 결과가 성공인지 확인
        for result in results:
            assert result["success"] is True
            assert result["project_id"] in project_ids
            assert "last_synced_at" in result
            assert "repository_id" in result
    
    @pytest.mark.asyncio
    async def test_get_commit_history_with_mock(
        self, 
        test_db: AsyncSession,
        test_user: User,
        test_project: Project
    ):
        """GitHub 저장소 커밋 히스토리 조회 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        create_data = GithubRepositoryCreate(
            github_url="https://github.com/testuser/commit-history-repo",
            repository_name="testuser/commit-history-repo",
            sync_enabled=True
        )
        
        # 저장소 생성
        created_repo = await service.create_github_repository(
            project_id=test_project.id,
            data=create_data
        )
        
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
        with patch.object(service, '_fetch_commits', return_value=mock_commits):
            commits = await service.get_commit_history(created_repo.id, limit=10)
        
        # Then
        assert len(commits) == 2
        
        # 첫 번째 커밋 확인
        first_commit = commits[0]
        assert first_commit.sha == "abc123def456"
        assert first_commit.message == "Initial commit"
        assert first_commit.author_name == "Test User"
        assert first_commit.author_email == "test@example.com"
        
        # 두 번째 커밋 확인
        second_commit = commits[1]
        assert second_commit.sha == "def456ghi789"
        assert second_commit.message == "Add feature"
    
    @pytest.mark.asyncio
    async def test_repository_not_found_exceptions(
        self, 
        test_db: AsyncSession
    ):
        """존재하지 않는 저장소에 대한 예외 처리 통합 테스트"""
        # Given
        service = GithubRepositoryService(test_db)
        non_existent_id = 99999
        
        # When & Then - 동기화 시도
        with pytest.raises(NotFoundException) as exc_info:
            await service.sync_repository(non_existent_id)
        assert f"GitHub repository with ID {non_existent_id} not found" in str(exc_info.value)
        
        # When & Then - 업데이트 시도
        update_data = GithubRepositoryUpdate(sync_enabled=False)
        with pytest.raises(NotFoundException) as exc_info:
            await service.update_repository(non_existent_id, update_data)
        assert f"GitHub repository with ID {non_existent_id} not found" in str(exc_info.value)
        
        # When & Then - 삭제 시도
        with pytest.raises(NotFoundException) as exc_info:
            await service.delete_repository(non_existent_id)
        assert f"GitHub repository with ID {non_existent_id} not found" in str(exc_info.value)
        
        # When & Then - 커밋 히스토리 조회 시도
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_commit_history(non_existent_id)
        assert f"GitHub repository with ID {non_existent_id} not found" in str(exc_info.value)