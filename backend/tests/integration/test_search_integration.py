"""
검색 기능 통합 테스트
실제 데이터베이스와 SearchService 상호작용 테스트
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.search import SearchService
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.note import Note, NoteType
from app.models.user import User


class TestSearchIntegration:
    """검색 기능 통합 테스트"""

    @pytest.mark.asyncio
    async def test_search_all_with_real_database(
        self, test_db: AsyncSession, test_user: User
    ):
        """실제 데이터베이스에서 전역 검색 테스트"""
        # Given
        # 테스트 프로젝트 생성
        project1 = Project(
            title="React Portfolio Project",
            description="A modern portfolio built with React and TypeScript",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="react-portfolio",
            tech_stack=["React", "TypeScript", "Tailwind CSS"],
            categories=["frontend", "portfolio"],
            tags=["react", "typescript", "portfolio"]
        )
        project2 = Project(
            title="Python FastAPI Backend",
            description="RESTful API backend using FastAPI and PostgreSQL",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="python-fastapi",
            tech_stack=["Python", "FastAPI", "PostgreSQL"],
            categories=["backend", "api"],
            tags=["python", "fastapi", "postgresql"]
        )
        
        test_db.add_all([project1, project2])
        await test_db.commit()
        await test_db.refresh(project1)
        await test_db.refresh(project2)

        # 테스트 노트 생성
        note1 = Note(
            title="React Hooks Tutorial",
            content={"text": "Learn about React hooks and their usage patterns"},
            type=NoteType.LEARN,
            project_id=project1.id,
            tags=["react", "hooks", "tutorial"]
        )
        note2 = Note(
            title="FastAPI Best Practices",
            content={"text": "Best practices for building FastAPI applications"},
            type=NoteType.LEARN,
            project_id=project2.id,
            tags=["fastapi", "python", "best-practices"]
        )
        
        test_db.add_all([note1, note2])
        await test_db.commit()
        await test_db.refresh(note1)
        await test_db.refresh(note2)

        search_service = SearchService(test_db)

        # When
        result = await search_service.search_all(
            query="React",
            user_id=test_user.id,
            limit=10
        )

        # Then
        assert result["query"] == "React"
        assert len(result["projects"]) >= 1
        assert len(result["notes"]) >= 1
        assert result["total_count"] >= 2
        
        # React가 포함된 프로젝트 확인
        react_projects = [p for p in result["projects"] if "React" in p.title]
        assert len(react_projects) >= 1
        
        # React가 포함된 노트 확인
        react_notes = [n for n in result["notes"] if "React" in n.title]
        assert len(react_notes) >= 1

    @pytest.mark.asyncio
    async def test_search_projects_only(
        self, test_db: AsyncSession, test_user: User
    ):
        """프로젝트만 검색하는 통합 테스트"""
        # Given
        project = Project(
            title="Vue.js E-commerce",
            description="E-commerce platform built with Vue.js",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="vue-ecommerce",
            tech_stack=["Vue.js", "Vuex", "Vue Router"],
            categories=["frontend", "ecommerce"],
            tags=["vue", "ecommerce", "frontend"]
        )
        
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        search_service = SearchService(test_db)

        # When
        result = await search_service.search_all(
            query="Vue",
            content_types=["project"],
            user_id=test_user.id,
            limit=10
        )

        # Then
        assert result["query"] == "Vue"
        assert len(result["projects"]) >= 1
        assert len(result["notes"]) == 0
        assert len(result["users"]) == 0
        
        # Vue가 포함된 프로젝트 확인
        vue_projects = [p for p in result["projects"] if "Vue" in p.title]
        assert len(vue_projects) >= 1

    @pytest.mark.asyncio
    async def test_search_notes_only(
        self, test_db: AsyncSession, test_user: User
    ):
        """노트만 검색하는 통합 테스트"""
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
            tags=["test"]
        )
        
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        note = Note(
            title="Docker Containerization Guide",
            content={"text": "Complete guide to Docker containerization"},
            type=NoteType.LEARN,
            project_id=project.id,
            tags=["docker", "containerization", "guide"]
        )
        
        test_db.add(note)
        await test_db.commit()
        await test_db.refresh(note)

        search_service = SearchService(test_db)

        # When
        result = await search_service.search_all(
            query="Docker",
            content_types=["note"],
            user_id=test_user.id,
            limit=10
        )

        # Then
        assert result["query"] == "Docker"
        assert len(result["projects"]) == 0
        assert len(result["notes"]) >= 1
        assert len(result["users"]) == 0
        
        # Docker가 포함된 노트 확인
        docker_notes = [n for n in result["notes"] if "Docker" in n.title]
        assert len(docker_notes) >= 1

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self, test_db: AsyncSession, test_user: User
    ):
        """카테고리 필터가 적용된 검색 테스트"""
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
            tags=["react", "typescript"]
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
            tags=["python", "fastapi"]
        )
        
        test_db.add_all([frontend_project, backend_project])
        await test_db.commit()
        await test_db.refresh(frontend_project)
        await test_db.refresh(backend_project)

        search_service = SearchService(test_db)

        # When
        result = await search_service.search_all(
            query="Project",
            categories=["frontend"],
            content_types=["project"],
            user_id=test_user.id,
            limit=10
        )

        # Then
        assert result["query"] == "Project"
        assert len(result["projects"]) >= 1
        
        # frontend 카테고리 프로젝트만 있는지 확인
        for project in result["projects"]:
            assert "frontend" in project.categories

    @pytest.mark.asyncio
    async def test_autocomplete_suggestions(
        self, test_db: AsyncSession, test_user: User
    ):
        """자동완성 제안 통합 테스트"""
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
            tags=["react-native", "mobile", "javascript"]
        )
        
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        search_service = SearchService(test_db)

        # When
        suggestions = await search_service.get_autocomplete_suggestions(
            query="React",
            content_type="all",
            limit=5
        )

        # Then
        assert len(suggestions) >= 1
        assert any("React" in suggestion for suggestion in suggestions)

    @pytest.mark.asyncio
    async def test_popular_searches(
        self, test_db: AsyncSession, test_user: User
    ):
        """인기 검색어 통합 테스트"""
        # Given
        project1 = Project(
            title="Python Project",
            description="Python development project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="python-project",
            tech_stack=["Python"],
            categories=["backend"],
            tags=["python", "backend"]
        )
        
        project2 = Project(
            title="Another Python Project",
            description="Another Python development project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            owner_id=test_user.id,
            slug="another-python-project",
            tech_stack=["Python", "Django"],
            categories=["backend"],
            tags=["python", "django", "backend"]
        )
        
        test_db.add_all([project1, project2])
        await test_db.commit()
        await test_db.refresh(project1)
        await test_db.refresh(project2)

        search_service = SearchService(test_db)

        # When
        popular_searches = await search_service.get_popular_searches(limit=5)

        # Then
        assert len(popular_searches) >= 1
        # Python 태그가 인기 검색어에 포함되어야 함
        python_keywords = [item["keyword"] for item in popular_searches if "python" in item["keyword"].lower()]
        assert len(python_keywords) >= 1

    @pytest.mark.asyncio
    async def test_search_stats(
        self, test_db: AsyncSession, test_user: User
    ):
        """검색 통계 통합 테스트"""
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
            tags=["test"]
        )
        
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        search_service = SearchService(test_db)

        # When
        stats = await search_service.get_search_stats()

        # Then
        assert "total_projects" in stats
        assert "total_notes" in stats
        assert "total_users" in stats
        assert "indexable_content" in stats
        assert stats["total_projects"] >= 1
        assert stats["indexable_content"] >= 1

    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, test_db: AsyncSession, test_user: User
    ):
        """페이지네이션이 적용된 검색 테스트"""
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
                tags=["test"]
            )
            projects.append(project)
        
        test_db.add_all(projects)
        await test_db.commit()
        for project in projects:
            await test_db.refresh(project)

        search_service = SearchService(test_db)

        # When
        result = await search_service.search_all(
            query="Test",
            content_types=["project"],
            user_id=test_user.id,
            limit=3,
            offset=0
        )

        # Then
        assert result["query"] == "Test"
        assert len(result["projects"]) <= 3  # limit 적용 확인
        assert result["total_count"] >= 5  # 전체 개수는 5개 이상

        # 두 번째 페이지 테스트
        result_page2 = await search_service.search_all(
            query="Test",
            content_types=["project"],
            user_id=test_user.id,
            limit=3,
            offset=3
        )
        
        assert len(result_page2["projects"]) <= 3
        # 첫 번째 페이지와 두 번째 페이지의 프로젝트가 달라야 함
        page1_ids = {p.id for p in result["projects"]}
        page2_ids = {p.id for p in result_page2["projects"]}
        assert page1_ids.isdisjoint(page2_ids)  # 교집합이 없어야 함
