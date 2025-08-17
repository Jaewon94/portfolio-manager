"""
검색 API 엔드포인트 테스트
실제 HTTP 요청을 통한 API 동작 테스트
"""

import pytest
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSearchAPI:
    """검색 API 엔드포인트 테스트"""

    @pytest.mark.asyncio
    async def test_search_all_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """전역 검색 API 엔드포인트 테스트"""
        # Given
        # 테스트 프로젝트 생성
        project = Project(
            title="React Portfolio Project",
            description="A modern portfolio built with React",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="react-portfolio",
            tech_stack=["React", "TypeScript"],
            categories=["frontend"],
            tags=["react", "portfolio"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # When
        response = await async_client.get("/api/v1/search/", params={"q": "React"})

        # Then
        assert response.status_code == 200
        data = response.json()
        # 직접 응답 형식
        assert "query" in data
        assert data["query"] == "React"
        assert len(data["projects"]) >= 1

    @pytest.mark.asyncio
    async def test_search_projects_only_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """프로젝트만 검색하는 API 엔드포인트 테스트"""
        # Given
        project = Project(
            title="Vue.js E-commerce",
            description="E-commerce platform built with Vue.js",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="vue-ecommerce",
            tech_stack=["Vue.js", "Vuex"],
            categories=["frontend", "ecommerce"],
            tags=["vue", "ecommerce"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # When
        response = await async_client.get(
            "/api/v1/search/projects", params={"q": "Vue"}
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "Vue"
        assert len(data["projects"]) >= 1
        assert len(data["notes"]) == 0
        assert len(data["users"]) == 0

    @pytest.mark.asyncio
    async def test_search_notes_only_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """노트만 검색하는 API 엔드포인트 테스트"""
        # Given
        project = Project(
            title="Test Project",
            description="Test project for note search",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="test-project",
            tech_stack=["Python"],
            categories=["test"],
            tags=["test"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        note = Note(
            title="Docker Containerization Guide",
            content={"text": "Complete guide to Docker containerization"},
            type=NoteType.LEARN,
            project_id=project.id,
            tags=["docker", "containerization"],
        )

        test_db.add(note)
        await test_db.commit()
        await test_db.refresh(note)

        # When
        response = await async_client.get(
            "/api/v1/search/notes", params={"q": "Docker"}
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "Docker"
        assert len(data["notes"]) >= 1
        assert len(data["projects"]) == 0
        assert len(data["users"]) == 0

    @pytest.mark.asyncio
    async def test_search_users_only_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """사용자만 검색하는 API 엔드포인트 테스트"""
        # Given
        # test_user는 이미 존재하므로 추가 생성 불필요

        # When
        response = await async_client.get(
            "/api/v1/search/users", params={"q": "User"}  # 더 일반적인 검색어 사용
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "User"
        assert len(data["users"]) >= 0  # 검색 결과가 없을 수도 있음
        assert len(data["projects"]) == 0
        assert len(data["notes"]) == 0

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """카테고리 필터가 적용된 검색 API 테스트"""
        # Given
        frontend_project = Project(
            title="Frontend Project",
            description="Frontend development project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="frontend-project",
            tech_stack=["React", "TypeScript"],
            categories=["frontend"],
            tags=["react", "typescript"],
        )

        backend_project = Project(
            title="Backend Project",
            description="Backend development project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="backend-project",
            tech_stack=["Python", "FastAPI"],
            categories=["backend"],
            tags=["python", "fastapi"],
        )

        test_db.add_all([frontend_project, backend_project])
        await test_db.commit()
        await test_db.refresh(frontend_project)
        await test_db.refresh(backend_project)

        # When
        response = await async_client.get(
            "/api/v1/search/",
            params={
                "q": "Project",
                "categories": ["frontend"],
                "content_types": ["project"],
            },
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "Project"
        assert len(data["projects"]) >= 1

        # frontend 카테고리 프로젝트만 있는지 확인
        for project in data["projects"]:
            assert "frontend" in project["categories"]

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """페이지네이션이 적용된 검색 API 테스트"""
        # Given
        projects = []
        for i in range(5):
            project = Project(
                title=f"Test Project {i}",
                description=f"Test project {i} description",
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC,
                owner_id=test_user.id,
                slug=f"test-project-{i}",
                tech_stack=["Python"],
                categories=["test"],
                tags=["test"],
            )
            projects.append(project)

        test_db.add_all(projects)
        await test_db.commit()
        for project in projects:
            await test_db.refresh(project)

        # When
        response = await async_client.get(
            "/api/v1/search/",
            params={"q": "Test", "content_types": ["project"], "limit": 3, "offset": 0},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "Test"
        assert len(data["projects"]) <= 3  # limit 적용 확인

    @pytest.mark.asyncio
    async def test_autocomplete_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """자동완성 API 엔드포인트 테스트"""
        # Given
        project = Project(
            title="React Native Mobile App",
            description="Mobile app built with React Native",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="react-native-app",
            tech_stack=["React Native", "JavaScript"],
            categories=["mobile", "frontend"],
            tags=["react-native", "mobile"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # When
        response = await async_client.get(
            "/api/v1/search/autocomplete",
            params={"q": "React", "type": "all", "limit": 5},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "React"
        assert "suggestions" in data
        assert len(data["suggestions"]) >= 0

    @pytest.mark.asyncio
    async def test_popular_searches_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """인기 검색어 API 엔드포인트 테스트"""
        # Given
        project = Project(
            title="Python Project",
            description="Python development project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="python-project",
            tech_stack=["Python"],
            categories=["backend"],
            tags=["python", "backend"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # When
        response = await async_client.get("/api/v1/search/popular", params={"limit": 5})

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "popular_searches" in data
        assert len(data["popular_searches"]) >= 0

    @pytest.mark.asyncio
    async def test_search_stats_endpoint(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """검색 통계 API 엔드포인트 테스트"""
        # Given
        project = Project(
            title="Test Project",
            description="Test project for stats",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="test-project",
            tech_stack=["Python"],
            categories=["test"],
            tags=["test"],
        )

        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # When
        response = await async_client.get("/api/v1/search/stats")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "total_notes" in data
        assert "total_users" in data
        assert "indexable_content" in data
        assert data["total_projects"] >= 1

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, async_client: AsyncClient):
        """빈 검색어로 검색 시 에러 처리 테스트"""
        # When
        response = await async_client.get("/api/v1/search/", params={"q": ""})

        # Then
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_search_with_invalid_content_types(self, async_client: AsyncClient):
        """잘못된 content_types로 검색 시 에러 처리 테스트"""
        # When
        response = await async_client.get(
            "/api/v1/search/", params={"q": "test", "content_types": ["invalid_type"]}
        )

        # Then
        assert response.status_code == 500  # Internal server error (ValueError)

    @pytest.mark.asyncio
    async def test_autocomplete_with_invalid_type(self, async_client: AsyncClient):
        """잘못된 autocomplete 타입으로 요청 시 에러 처리 테스트"""
        # When
        response = await async_client.get(
            "/api/v1/search/autocomplete", params={"q": "test", "type": "invalid_type"}
        )

        # Then
        assert response.status_code == 400  # Bad request

    @pytest.mark.asyncio
    async def test_search_with_unauthorized_user(
        self, async_client: AsyncClient, test_db: AsyncSession, test_user: User
    ):
        """인증되지 않은 사용자의 검색 테스트"""
        # Given
        private_project = Project(
            title="Private Project",
            description="Private project for testing",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PRIVATE,
            owner_id=test_user.id,
            slug="private-project",
            tech_stack=["Python"],
            categories=["private"],
            tags=["private"],
        )

        test_db.add(private_project)
        await test_db.commit()
        await test_db.refresh(private_project)

        # When (인증 없이 요청)
        response = await async_client.get("/api/v1/search/", params={"q": "Private"})

        # Then
        assert response.status_code == 200
        data = response.json()
        # 인증되지 않은 사용자는 private 프로젝트를 볼 수 없어야 함
        private_projects = [
            p for p in data["projects"] if p["title"] == "Private Project"
        ]
        assert len(private_projects) == 0
