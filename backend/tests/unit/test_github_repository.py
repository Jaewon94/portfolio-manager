"""
GitHub 저장소 관련 단위 테스트
TDD Red 단계: 실패하는 테스트 작성
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.services.github import GithubRepositoryService
from app.schemas.github import (
    GithubRepositoryCreate,
    GithubRepositoryUpdate,
    GithubRepositorySync,
    GithubRepository as GithubRepositorySchema
)
from app.models.github_repository import GithubRepository
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
    ExternalAPIException
)


class TestGithubRepositoryService:
    """GitHub 저장소 서비스 단위 테스트"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock 데이터베이스 세션"""
        return AsyncMock()
    
    @pytest.fixture
    def github_service(self, mock_db):
        """GitHub 저장소 서비스 인스턴스"""
        return GithubRepositoryService(mock_db)
    
    @pytest.fixture
    def sample_github_data(self):
        """테스트용 GitHub 저장소 데이터"""
        return {
            "project_id": 1,
            "github_url": "https://github.com/testuser/test-repo",
            "repository_name": "testuser/test-repo",
            "sync_enabled": True
        }
    
    @pytest.mark.asyncio
    async def test_create_github_repository_success(self, github_service, sample_github_data):
        """GitHub 저장소 연동 성공 테스트"""
        # Given
        create_data = GithubRepositoryCreate(**sample_github_data)
        
        # Mock database operations with proper async handling
        with patch.object(github_service, 'db') as mock_db:
            # Mock execute to return None for duplicate check (await 가능한 형태로)
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # Mock other db operations
            mock_db.add = Mock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            # Set up refresh side effect to set ID
            def set_id(repo):
                repo.id = 1
            mock_db.refresh.side_effect = set_id
            
            # When
            result = await github_service.create_github_repository(
                project_id=sample_github_data["project_id"],
                data=create_data
            )
            
            # Then
            assert result is not None
            assert result.github_url == sample_github_data["github_url"]
            assert result.repository_name == sample_github_data["repository_name"]
            assert result.sync_enabled == sample_github_data["sync_enabled"]
            assert result.id == 1
    
    @pytest.mark.asyncio
    async def test_create_github_repository_duplicate_url(self, github_service, sample_github_data):
        """중복된 GitHub URL로 저장소 생성 시 예외 발생 테스트"""
        # Given
        create_data = GithubRepositoryCreate(**sample_github_data)
        
        # Mock database to return existing repository for duplicate check
        with patch.object(github_service, 'db') as mock_db:
            # Mock first call to return None (no duplicate)
            mock_result_first = AsyncMock()
            mock_result_first.scalar_one_or_none = Mock(return_value=None)
            
            # Mock second call to return existing repository (duplicate)
            existing_repo = GithubRepository(
                id=1,
                project_id=1,
                github_url=sample_github_data["github_url"],
                repository_name=sample_github_data["repository_name"]
            )
            mock_result_second = AsyncMock()
            mock_result_second.scalar_one_or_none = Mock(return_value=existing_repo)
            
            # Set up execute to return different results on subsequent calls
            mock_db.execute = AsyncMock(side_effect=[mock_result_first, mock_result_second])
            mock_db.add = Mock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock(side_effect=lambda repo: setattr(repo, 'id', 1))
            
            # 첫 번째 생성
            await github_service.create_github_repository(
                project_id=sample_github_data["project_id"],
                data=create_data
            )
            
            # When & Then - 같은 URL로 다시 생성 시도
            with pytest.raises(DuplicateException) as exc_info:
                await github_service.create_github_repository(
                    project_id=2,  # 다른 프로젝트 ID
                    data=create_data
                )
            
            assert "GitHub URL already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_github_repository_invalid_url(self, github_service):
        """잘못된 GitHub URL 형식 테스트"""
        # Given - 잘못된 URL 직접 생성 (Pydantic 검증 우회)
        class MockData:
            def __init__(self):
                self.github_url = "https://not-github.com/user/repo"  # 잘못된 URL
                self.repository_name = "user/repo"
                self.sync_enabled = True
        
        create_data = MockData()
        
        # When & Then
        with pytest.raises(ValidationException) as exc_info:
            await github_service.create_github_repository(
                project_id=1,
                data=create_data
            )
        
        assert "Invalid GitHub URL format" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_success(self, github_service):
        """GitHub 저장소 정보 동기화 성공 테스트"""
        # Given
        repository_id = 1
        mock_github_api_response = {
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "stargazers_count": 100,
            "forks_count": 20,
            "watchers_count": 150,
            "language": "Python",
            "license": {"name": "MIT"},
            "private": False,
            "fork": False,
            "default_branch": "main"
        }
        
        # 기존 저장소 Mock 데이터
        existing_repo = GithubRepository(
            id=repository_id,
            project_id=1,
            github_url="https://github.com/testuser/test-repo",
            repository_name="testuser/test-repo"
        )
        
        # Mock 데이터베이스 및 GitHub API 호출
        with patch.object(github_service, 'get_by_id', return_value=existing_repo), \
             patch.object(github_service, '_fetch_github_data', return_value=mock_github_api_response), \
             patch.object(github_service, 'db') as mock_db:
            
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            # When
            result = await github_service.sync_repository(repository_id)
            
            # Then
            assert result is not None
            assert result.stars == 100
            assert result.forks == 20
            assert result.watchers == 150
            assert result.language == "Python"
            assert result.license == "MIT"
    
    @pytest.mark.asyncio
    async def test_sync_github_repository_api_failure(self, github_service):
        """GitHub API 호출 실패 시 예외 처리 테스트"""
        # Given
        repository_id = 1
        
        # 기존 저장소 Mock 데이터
        existing_repo = GithubRepository(
            id=repository_id,
            project_id=1,
            github_url="https://github.com/testuser/test-repo",
            repository_name="testuser/test-repo"
        )
        
        # Mock 설정: get_by_id는 성공, _fetch_github_data는 실패
        with patch.object(github_service, 'get_by_id', return_value=existing_repo), \
             patch.object(github_service, '_fetch_github_data', 
                         side_effect=ExternalAPIException("GitHub API rate limit exceeded")), \
             patch.object(github_service, 'db') as mock_db:
            
            mock_db.commit = AsyncMock()
            
            # When & Then
            with pytest.raises(ExternalAPIException) as exc_info:
                await github_service.sync_repository(repository_id)
            
            assert "GitHub API rate limit exceeded" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_github_repository_by_project_id(self, github_service):
        """프로젝트 ID로 GitHub 저장소 조회 테스트"""
        # Given
        project_id = 1
        expected_repo = GithubRepository(
            id=1,
            project_id=project_id,
            github_url="https://github.com/testuser/test-repo",
            repository_name="testuser/test-repo",
            stars=50,
            forks=10
        )
        
        # Mock 데이터베이스 조회
        with patch.object(github_service, 'db') as mock_db:
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = Mock(return_value=expected_repo)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # When
            result = await github_service.get_by_project_id(project_id)
            
            # Then
            assert result is not None
            assert result.project_id == project_id
            assert result.github_url == expected_repo.github_url
    
    @pytest.mark.asyncio
    async def test_update_github_repository(self, github_service):
        """GitHub 저장소 정보 업데이트 테스트"""
        # Given
        repository_id = 1
        update_data = GithubRepositoryUpdate(
            sync_enabled=False,
            github_url="https://github.com/testuser/new-repo"
        )
        
        # 기존 저장소 Mock 데이터
        existing_repo = GithubRepository(
            id=repository_id,
            project_id=1,
            github_url="https://github.com/testuser/old-repo",
            repository_name="testuser/old-repo",
            sync_enabled=True
        )
        
        # Mock 설정
        with patch.object(github_service, 'get_by_id', return_value=existing_repo), \
             patch.object(github_service, 'db') as mock_db:
            
            # Mock 중복 확인 (업데이트 시 다른 저장소에서 같은 URL 사용하지 않음)
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_db.execute = AsyncMock(return_value=mock_result)
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            # 업데이트 후 상태 시뮬레이션
            def update_repo(repo):
                repo.sync_enabled = False
                repo.github_url = "https://github.com/testuser/new-repo"
                repo.repository_name = "testuser/new-repo"
            
            mock_db.refresh.side_effect = update_repo
            
            # When
            result = await github_service.update_repository(repository_id, update_data)
            
            # Then
            assert result is not None
            assert result.sync_enabled is False
            assert result.github_url == "https://github.com/testuser/new-repo"
    
    @pytest.mark.asyncio
    async def test_delete_github_repository(self, github_service):
        """GitHub 저장소 연동 해제 테스트"""
        # Given
        repository_id = 1
        
        # 기존 저장소 Mock 데이터
        existing_repo = GithubRepository(
            id=repository_id,
            project_id=1,
            github_url="https://github.com/testuser/test-repo",
            repository_name="testuser/test-repo"
        )
        
        # Mock 설정
        with patch.object(github_service, 'get_by_id', return_value=existing_repo), \
             patch.object(github_service, 'db') as mock_db:
            
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()
            
            # When
            result = await github_service.delete_repository(repository_id)
            
            # Then
            assert result is True
            
            # 삭제 호출 확인
            mock_db.delete.assert_called_once_with(existing_repo)
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_sync_repositories(self, github_service):
        """여러 GitHub 저장소 일괄 동기화 테스트"""
        # Given
        project_ids = [1, 2, 3]
        
        # Mock 저장소들
        repos = [
            GithubRepository(
                id=i,
                project_id=project_id,
                github_url=f"https://github.com/testuser/repo{i}",
                repository_name=f"testuser/repo{i}",
                sync_enabled=True
            )
            for i, project_id in enumerate(project_ids, 1)
        ]
        
        # Mock 설정
        with patch.object(github_service, 'get_by_project_id', side_effect=repos), \
             patch.object(github_service, 'sync_repository', return_value=AsyncMock()):
            
            # When
            results = await github_service.bulk_sync_repositories(project_ids)
            
            # Then
            assert len(results) == 3
            assert all(r.get("success") for r in results)
    
    @pytest.mark.asyncio
    async def test_get_repository_commit_history(self, github_service):
        """GitHub 저장소 커밋 히스토리 조회 테스트"""
        # Given
        repository_id = 1
        limit = 10
        
        # 기존 저장소 Mock 데이터
        existing_repo = GithubRepository(
            id=repository_id,
            project_id=1,
            github_url="https://github.com/testuser/test-repo",
            repository_name="testuser/test-repo"
        )
        
        mock_commits = [
            {
                "sha": "abc123",
                "commit": {
                    "message": "Initial commit",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2024-01-01T00:00:00Z"
                    }
                },
                "html_url": "https://github.com/testuser/test-repo/commit/abc123"
            }
        ]
        
        with patch.object(github_service, 'get_by_id', return_value=existing_repo), \
             patch.object(github_service, '_fetch_commits', return_value=mock_commits):
            
            # When
            commits = await github_service.get_commit_history(repository_id, limit=limit)
            
            # Then
            assert len(commits) == 1
            assert commits[0].sha == "abc123"
            assert commits[0].message == "Initial commit"
            assert commits[0].author_name == "Test User"
    
    @pytest.mark.asyncio
    async def test_validate_github_repository_access(self, github_service):
        """GitHub 저장소 접근 권한 검증 테스트"""
        # Given
        github_url = "https://github.com/testuser/private-repo"
        access_token = "ghp_test_token"
        
        # When - 접근 가능한 경우
        with patch.object(github_service, '_check_repository_access', 
                         return_value=True):
            result = await github_service.validate_repository_access(
                github_url, access_token
            )
            assert result is True
        
        # When - 접근 불가능한 경우
        with patch.object(github_service, '_check_repository_access', 
                         return_value=False):
            result = await github_service.validate_repository_access(
                github_url, access_token
            )
            assert result is False