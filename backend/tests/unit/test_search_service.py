"""
검색 서비스 단위 테스트
TDD 방식으로 작성 - Red 단계
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User
from app.services.search import SearchService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestSearchService:
    """검색 서비스 단위 테스트"""

    @pytest.fixture
    def mock_db(self):
        """Mock 데이터베이스 세션"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def search_service(self, mock_db):
        """검색 서비스 인스턴스"""
        return SearchService(mock_db)

    @pytest.fixture
    def sample_projects(self):
        """샘플 프로젝트 데이터"""
        return [
            Project(
                id=1,
                title="React Portfolio Project",
                description="A modern portfolio built with React",
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC,
                owner_id=1,
                slug="react-portfolio",
                tech_stack=["React", "TypeScript"],
                categories=["frontend"],
                tags=["portfolio", "react"],
            ),
            Project(
                id=2,
                title="Python API Backend",
                description="FastAPI backend for portfolio manager",
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC,
                owner_id=1,
                slug="python-api",
                tech_stack=["Python", "FastAPI"],
                categories=["backend"],
                tags=["api", "python"],
            ),
        ]

    @pytest.fixture
    def sample_notes(self):
        """샘플 노트 데이터"""
        return [
            Note(
                id=1,
                title="React Hooks Tutorial",
                content={"text": "Learn about React hooks and their usage"},
                type=NoteType.LEARN,
                project_id=1,
                tags=["react", "hooks"],
            ),
            Note(
                id=2,
                title="FastAPI Best Practices",
                content={"text": "Best practices for building FastAPI applications"},
                type=NoteType.LEARN,
                project_id=2,
                tags=["fastapi", "python"],
            ),
        ]

    @pytest.fixture
    def sample_users(self):
        """샘플 사용자 데이터"""
        return [
            User(
                id=1,
                email="test@example.com",
                username="testuser",
                name="Test User",
                bio="Full-stack developer",
            ),
            User(
                id=2,
                email="dev@example.com",
                username="devuser",
                name="Developer User",
                bio="React and Python developer",
            ),
        ]

    @pytest.mark.asyncio
    async def test_search_all_with_empty_query_should_return_empty_results(
        self, search_service
    ):
        """빈 검색어로 검색 시 빈 결과 반환"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar.return_value = 0
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(query="")

        # Then
        assert result["projects"] == []
        assert result["notes"] == []
        assert result["users"] == []
        assert result["total_count"] == 0
        assert result["query"] == ""

    @pytest.mark.asyncio
    async def test_search_all_with_projects_only(self, search_service, sample_projects):
        """프로젝트만 검색하는 경우"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_projects[
            :1
        ]  # 첫 번째 프로젝트만
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(
            query="React", content_types=["project"]
        )

        # Then
        assert len(result["projects"]) == 1
        assert result["projects"][0].title == "React Portfolio Project"
        assert result["notes"] == []
        assert result["users"] == []
        assert result["total_count"] == 1

    @pytest.mark.asyncio
    async def test_search_all_with_notes_only(self, search_service, sample_notes):
        """노트만 검색하는 경우"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_notes[
            :1
        ]  # 첫 번째 노트만
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(query="React", content_types=["note"])

        # Then
        assert len(result["notes"]) == 1
        assert result["notes"][0].title == "React Hooks Tutorial"
        assert result["projects"] == []
        assert result["users"] == []
        assert result["total_count"] == 1

    @pytest.mark.asyncio
    async def test_search_all_with_users_only(self, search_service, sample_users):
        """사용자만 검색하는 경우"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_users[
            1:2
        ]  # 두 번째 사용자만
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(
            query="Developer", content_types=["user"]
        )

        # Then
        assert len(result["users"]) == 1
        assert result["users"][0].name == "Developer User"
        assert result["projects"] == []
        assert result["notes"] == []
        assert result["total_count"] == 1

    @pytest.mark.asyncio
    async def test_search_all_with_all_content_types(
        self, search_service, sample_projects, sample_notes, sample_users
    ):
        """모든 콘텐츠 타입 검색"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.side_effect = [
            sample_projects[:1],  # 프로젝트 검색 결과 (첫 번째만)
            sample_notes[:1],  # 노트 검색 결과 (첫 번째만)
            sample_users[1:2],  # 사용자 검색 결과 (두 번째만)
        ]
        mock_result.scalar.side_effect = [1, 1, 1]  # 각각 1개씩
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(query="React")

        # Then
        assert len(result["projects"]) == 1
        assert len(result["notes"]) == 1
        assert len(result["users"]) == 1
        assert result["total_count"] == 3

    @pytest.mark.asyncio
    async def test_search_all_with_invalid_content_types_should_raise_error(
        self, search_service
    ):
        """잘못된 콘텐츠 타입으로 검색 시 에러"""
        # When & Then
        with pytest.raises(ValueError):
            await search_service.search_all(
                query="test", content_types=["invalid_type"]
            )

    @pytest.mark.asyncio
    async def test_search_all_with_pagination(self, search_service, sample_projects):
        """페이지네이션 테스트"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_projects[:1]
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service.search_all(
            query="React", content_types=["project"], limit=1, offset=0
        )

        # Then
        assert len(result["projects"]) == 1
        assert result["total_count"] == 1

    @pytest.mark.asyncio
    async def test_get_autocomplete_suggestions(self, search_service):
        """자동완성 제안 테스트"""
        # Given
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("React Hooks",), ("React Router",)]
        search_service.db.execute.return_value = mock_result

        # When
        suggestions = await search_service.get_autocomplete_suggestions(
            query="React", content_type="all", limit=5
        )

        # Then
        assert len(suggestions) == 2
        assert "React Hooks" in suggestions
        assert "React Router" in suggestions

    @pytest.mark.asyncio
    async def test_get_autocomplete_suggestions_with_invalid_type_should_raise_error(
        self, search_service
    ):
        """잘못된 타입으로 자동완성 요청 시 에러"""
        # When & Then
        with pytest.raises(ValueError):
            await search_service.get_autocomplete_suggestions(
                query="test", content_type="invalid_type", limit=5
            )

    @pytest.mark.asyncio
    async def test_get_popular_searches(self, search_service):
        """인기 검색어 조회 테스트"""
        # Given
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("React", 15),
            ("Python", 12),
            ("FastAPI", 8),
        ]
        search_service.db.execute.return_value = mock_result

        # When
        popular_searches = await search_service.get_popular_searches(limit=3)

        # Then
        assert len(popular_searches) == 3
        assert popular_searches[0]["keyword"] == "React"
        assert popular_searches[0]["count"] == 15

    @pytest.mark.asyncio
    async def test_get_search_stats(self, search_service):
        """검색 통계 조회 테스트"""
        # Given
        mock_result = MagicMock()
        mock_result.scalar.side_effect = [50, 120, 30]  # projects, notes, users
        search_service.db.execute.return_value = mock_result

        # When
        stats = await search_service.get_search_stats()

        # Then
        assert stats["total_projects"] == 50
        assert stats["total_notes"] == 120
        assert stats["total_users"] == 30
        assert stats["indexable_content"] == 170

    @pytest.mark.asyncio
    async def test_search_projects_with_category_filter(
        self, search_service, sample_projects
    ):
        """카테고리 필터가 적용된 프로젝트 검색"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_projects[:1]
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service._search_projects(
            query="React", categories=["frontend"], limit=10, offset=0
        )

        # Then
        assert len(result["projects"]) == 1
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_search_notes_with_user_filter(self, search_service, sample_notes):
        """사용자 필터가 적용된 노트 검색"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_notes[
            :1
        ]  # 첫 번째 노트만
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service._search_notes(
            query="React", user_id=1, limit=10, offset=0
        )

        # Then
        assert len(result["notes"]) == 1
        assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_search_users_with_public_only(self, search_service, sample_users):
        """공개 사용자만 검색"""
        # Given
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_users[
            1:2
        ]  # 두 번째 사용자만
        mock_result.scalar.return_value = 1
        search_service.db.execute.return_value = mock_result

        # When
        result = await search_service._search_users(
            query="Developer", limit=10, offset=0
        )

        # Then
        assert len(result["users"]) == 1
        assert result["count"] == 1
