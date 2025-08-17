"""
대시보드 API 테스트
Dashboard API endpoint tests
"""

import pytest
from datetime import datetime, date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.note import Note, NoteType


@pytest.mark.api
@pytest.mark.dashboard
class TestDashboardAPI:
    """대시보드 API 엔드포인트 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_dashboard_stats_unauthorized(self, async_client: AsyncClient):
        """인증 없이 대시보드 통계 조회 시 401 오류"""
        response = await async_client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Authorization token required"
        
    @pytest.mark.asyncio
    async def test_get_dashboard_stats_success(
        self, 
        authenticated_client: AsyncClient, 
        test_user: User,
        test_db
    ):
        """대시보드 기본 통계 조회 성공"""
        # 테스트 데이터 생성
        project = Project(
            owner_id=test_user.id,
            title="Dashboard Test Project",
            slug="dashboard-test",
            description="Test project for dashboard",
            view_count=150,
            like_count=20,
            tech_stack=["Python", "FastAPI"],
            categories=["Backend"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        
        # API 호출
        response = await authenticated_client.get("/api/v1/dashboard/stats")
        
        # 디버깅용 출력
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Response headers: {dict(response.headers)}")
        
        # 검증
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        
        stats = data["data"]
        assert "total_projects" in stats
        assert "total_notes" in stats
        assert "total_views" in stats
        assert "total_likes" in stats
        assert "recent_activities" in stats
        
        assert stats["total_projects"] == 1
        assert stats["total_views"] == 150
        assert stats["total_likes"] == 20
        
    @pytest.mark.asyncio
    async def test_get_dashboard_stats_with_activities(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
        test_db
    ):
        """활동 포함 대시보드 통계 조회"""
        # 테스트 데이터 생성
        project = Project(
            owner_id=test_user.id,
            title="Activity Test Project",
            slug="activity-test",
            description="Test project for activities",
            view_count=200,
            like_count=25,
            tech_stack=["JavaScript", "React"],
            categories=["Frontend"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(project)
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/stats?include_activities=true"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        stats = data["data"]
        assert "recent_activities" in stats
        assert isinstance(stats["recent_activities"], list)
        assert stats["total_projects"] == 1
        assert stats["total_views"] == 200
        assert stats["total_likes"] == 25
        
    @pytest.mark.asyncio
    async def test_get_project_stats_by_period(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """프로젝트 통계 조회 - 기간별"""
        # 테스트 프로젝트 생성
        project = Project(
            owner_id=test_user.id,
            title="Period Stats Project",
            slug="period-stats",
            description="Test project for period stats",
            view_count=300,
            like_count=30,
            tech_stack=["Python", "Django"],
            categories=["Backend"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(project)
        await test_db.commit()
        
        # 일별 통계
        response = await authenticated_client.get(
            "/api/v1/dashboard/projects/stats",
            params={"period": "daily", "days": 7}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        stats = data["data"]
        
        assert "stats_by_date" in stats
        assert "total_projects" in stats
        assert "total_views" in stats
        assert "total_likes" in stats
        assert isinstance(stats["stats_by_date"], list)
        
        # 실제 프로젝트 통계 확인
        assert stats["total_projects"] == 1
        assert stats["total_views"] == 300
        assert stats["total_likes"] == 30
        
        if stats["stats_by_date"]:
            daily_stat = stats["stats_by_date"][0]
            assert "date" in daily_stat
            assert "project_count" in daily_stat
            assert "view_count" in daily_stat
            assert "like_count" in daily_stat
            assert "note_count" in daily_stat
            
    @pytest.mark.asyncio
    async def test_get_activity_timeline(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """활동 타임라인 조회"""
        # 테스트 데이터 생성 (활동 생성을 위한 프로젝트)
        project = Project(
            owner_id=test_user.id,
            title="Timeline Test Project",
            slug="timeline-test",
            description="Test project for timeline",
            view_count=100,
            like_count=10,
            tech_stack=["Vue.js"],
            categories=["Frontend"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        
        # 노트 생성 (활동 생성)
        note = Note(
            project_id=project.id,
            type=NoteType.LEARN,
            title="Timeline Test Note",
            content={"blocks": [{"type": "paragraph", "data": {"text": "Timeline test content"}}]}
        )
        test_db.add(note)
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/activities",
            params={"limit": 10}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        activities = data["data"]
        
        assert "items" in activities
        assert "total" in activities
        assert "has_more" in activities
        assert isinstance(activities["items"], list)
        
        if activities["items"]:
            activity = activities["items"][0]
            assert "id" in activity
            assert "type" in activity  # project_created, note_added, etc.
            assert "title" in activity
            assert "description" in activity
            assert "created_at" in activity
            assert "metadata" in activity
            
    @pytest.mark.asyncio
    async def test_get_popular_projects(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """인기 프로젝트 통계"""
        # 인기도가 다른 여러 프로젝트 생성
        projects_data = [
            {"title": "Most Popular", "slug": "most-popular", "view_count": 1000, "like_count": 100},
            {"title": "Second Popular", "slug": "second-popular", "view_count": 500, "like_count": 50},
            {"title": "Third Popular", "slug": "third-popular", "view_count": 200, "like_count": 20}
        ]
        
        for project_data in projects_data:
            project = Project(
                owner_id=test_user.id,
                title=project_data["title"],
                slug=project_data["slug"],
                description="Test popular project",
                view_count=project_data["view_count"],
                like_count=project_data["like_count"],
                tech_stack=["Node.js"],
                categories=["Backend"],
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC
            )
            test_db.add(project)
        
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/projects/popular",
            params={"limit": 5}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        projects = data["data"]
        
        assert "items" in projects
        assert isinstance(projects["items"], list)
        assert len(projects["items"]) == 3  # 생성한 프로젝트 수
        
        # 조회수 순으로 정렬되었는지 확인
        items = projects["items"]
        assert items[0]["title"] == "Most Popular"
        assert items[0]["view_count"] == 1000
        assert items[1]["title"] == "Second Popular"
        assert items[1]["view_count"] == 500
        
        # 필드 검증
        project = projects["items"][0]
        assert "id" in project
        assert "title" in project
        assert "slug" in project
        assert "view_count" in project
        assert "like_count" in project
            
    @pytest.mark.asyncio
    async def test_get_tech_stack_distribution(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """기술 스택 분포 통계"""
        # 다양한 기술 스택을 가진 프로젝트 생성
        tech_projects = [
            {"tech_stack": ["Python", "FastAPI", "PostgreSQL"]},
            {"tech_stack": ["Python", "Django"]},
            {"tech_stack": ["JavaScript", "React", "Node.js"]},
            {"tech_stack": ["Python", "Flask"]}
        ]
        
        for i, project_data in enumerate(tech_projects):
            project = Project(
                owner_id=test_user.id,
                title=f"Tech Project {i+1}",
                slug=f"tech-project-{i+1}",
                description="Tech stack test project",
                tech_stack=project_data["tech_stack"],
                categories=["Backend"],
                view_count=100,
                like_count=10,
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC
            )
            test_db.add(project)
        
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/stats/tech-stack"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        tech_stats = data["data"]
        
        assert "distribution" in tech_stats
        assert "total_projects" in tech_stats
        assert tech_stats["total_projects"] == 4
        assert isinstance(tech_stats["distribution"], list)
        
        # Python이 가장 많이 사용되었는지 확인 (3번)
        distribution = tech_stats["distribution"]
        python_entry = next((item for item in distribution if item["name"] == "Python"), None)
        assert python_entry is not None
        assert python_entry["count"] == 3
        
        if tech_stats["distribution"]:
            tech = tech_stats["distribution"][0]
            assert "name" in tech
            assert "count" in tech
            assert "percentage" in tech
            
    @pytest.mark.asyncio
    async def test_get_category_distribution(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """카테고리 분포 통계"""
        # 다양한 카테고리를 가진 프로젝트 생성
        category_projects = [
            {"categories": ["Backend", "API"]},
            {"categories": ["Frontend", "Web"]},
            {"categories": ["Backend", "Database"]},
            {"categories": ["Mobile", "iOS"]}
        ]
        
        for i, project_data in enumerate(category_projects):
            project = Project(
                owner_id=test_user.id,
                title=f"Category Project {i+1}",
                slug=f"category-project-{i+1}",
                description="Category test project",
                categories=project_data["categories"],
                tech_stack=["Python"],
                view_count=100,
                like_count=10,
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC
            )
            test_db.add(project)
        
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/stats/categories"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        category_stats = data["data"]
        
        assert "distribution" in category_stats
        assert "total_projects" in category_stats
        assert category_stats["total_projects"] == 4
        assert isinstance(category_stats["distribution"], list)
        
        # Backend가 가장 많이 사용되었는지 확인 (2번)
        distribution = category_stats["distribution"]
        backend_entry = next((item for item in distribution if item["name"] == "Backend"), None)
        assert backend_entry is not None
        assert backend_entry["count"] == 2
        
        if category_stats["distribution"]:
            category = category_stats["distribution"][0]
            assert "name" in category
            assert "count" in category
            assert "percentage" in category
            
    @pytest.mark.asyncio
    async def test_get_note_stats_by_type(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """노트 타입별 통계"""
        # 테스트 프로젝트 생성
        project = Project(
            owner_id=test_user.id,
            title="Note Stats Project",
            slug="note-stats-project",
            description="Test project for note stats",
            tech_stack=["Python"],
            categories=["Backend"],
            view_count=100,
            like_count=10,
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        
        # 다양한 타입의 노트 생성
        note_types_data = [
            {"type": NoteType.LEARN, "count": 3},
            {"type": NoteType.CHANGE, "count": 2},
            {"type": NoteType.RESEARCH, "count": 1}
        ]
        
        for note_type_data in note_types_data:
            for i in range(note_type_data["count"]):
                note = Note(
                    project_id=project.id,
                    type=note_type_data["type"],
                    title=f"{note_type_data['type'].value} Note {i+1}",
                    content={"blocks": [{"type": "paragraph", "data": {"text": "Test content"}}]}
                )
                test_db.add(note)
        
        await test_db.commit()
        
        response = await authenticated_client.get(
            "/api/v1/dashboard/notes/stats"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        note_stats = data["data"]
        
        assert "by_type" in note_stats
        assert "total" in note_stats
        assert note_stats["total"] == 6  # 3 + 2 + 1
        assert "learn" in note_stats["by_type"]
        assert "change" in note_stats["by_type"]
        assert "research" in note_stats["by_type"]
        
        # learn 타입 확인
        learn_stats = note_stats["by_type"]["learn"]
        assert learn_stats["count"] == 3
        assert learn_stats["percentage"] == 50.0  # 3/6 * 100
        
        # 각 타입별 통계 확인
        for note_type in ["learn", "change", "research"]:
            type_stat = note_stats["by_type"][note_type]
            assert "count" in type_stat
            assert "recent_count" in type_stat  # 최근 7일
            assert "percentage" in type_stat
            
    @pytest.mark.asyncio
    async def test_get_dashboard_stats_no_data(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """데이터 없는 경우 대시보드 통계 조회"""
        response = await authenticated_client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        stats = data["data"]
        
        # 빈 데이터 검증
        assert stats["total_projects"] == 0
        assert stats["total_notes"] == 0
        assert stats["total_views"] == 0
        assert stats["total_likes"] == 0
        assert stats["recent_activities"] == []
        
    @pytest.mark.asyncio
    async def test_get_popular_projects_limit(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """인기 프로젝트 제한 테스트"""
        # 5개의 프로젝트 생성
        for i in range(5):
            project = Project(
                owner_id=test_user.id,
                title=f"Project {i+1}",
                slug=f"project-{i+1}",
                description="Test project",
                view_count=1000 - (i * 100),  # 내림차순으로 조회수 설정
                like_count=100 - (i * 10),
                tech_stack=["Python"],
                categories=["Backend"],
                status=ProjectStatus.ACTIVE,
                visibility=ProjectVisibility.PUBLIC
            )
            test_db.add(project)
        
        await test_db.commit()
        
        # 상위 3개만 조회
        response = await authenticated_client.get(
            "/api/v1/dashboard/projects/popular",
            params={"limit": 3}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        projects = data["data"]
        assert len(projects["items"]) == 3
        
        # 조회수 순으로 정렬 확인
        items = projects["items"]
        for i in range(len(items) - 1):
            assert items[i]["view_count"] >= items[i+1]["view_count"]
            
    @pytest.mark.asyncio
    async def test_get_tech_stack_distribution_empty(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """기술 스택이 없는 경우 분포 조회"""
        response = await authenticated_client.get(
            "/api/v1/dashboard/stats/tech-stack"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        tech_stats = data["data"]
        
        assert tech_stats["distribution"] == []
        assert tech_stats["total_projects"] == 0
        
    @pytest.mark.asyncio
    async def test_get_category_distribution_empty(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """카테고리가 없는 경우 분포 조회"""
        response = await authenticated_client.get(
            "/api/v1/dashboard/stats/categories"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        category_stats = data["data"]
        
        assert category_stats["distribution"] == []
        assert category_stats["total_projects"] == 0
        
    @pytest.mark.asyncio
    async def test_get_note_stats_empty(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """노트가 없는 경우 타입별 통계"""
        response = await authenticated_client.get(
            "/api/v1/dashboard/notes/stats"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        note_stats = data["data"]
        
        assert note_stats["total"] == 0
        assert "by_type" in note_stats
        
        # 모든 타입이 0이어야 함
        for note_type in ["learn", "change", "research"]:
            if note_type in note_stats["by_type"]:
                type_stat = note_stats["by_type"][note_type]
                assert type_stat["count"] == 0
                assert type_stat["percentage"] == 0.0
                
    @pytest.mark.asyncio
    async def test_get_activity_timeline_pagination(
        self, authenticated_client: AsyncClient, test_user: User, test_db
    ):
        """활동 타임라인 페이지네이션 테스트"""
        # 첫 페이지
        response = await authenticated_client.get(
            "/api/v1/dashboard/activities",
            params={"limit": 5, "offset": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        activities = data["data"]
        
        assert "items" in activities
        assert "total" in activities
        assert "has_more" in activities
        assert len(activities["items"]) <= 5
        
        # 두 번째 페이지
        if activities["has_more"]:
            response2 = await authenticated_client.get(
                "/api/v1/dashboard/activities",
                params={"limit": 5, "offset": 5}
            )
            
            assert response2.status_code == 200
            data2 = response2.json()
            activities2 = data2["data"]
            
            # 다른 활동이 조회되어야 함
            if activities["items"] and activities2["items"]:
                assert activities["items"][0]["id"] != activities2["items"][0]["id"]
                
    @pytest.mark.asyncio
    async def test_api_error_handling(
        self, authenticated_client: AsyncClient
    ):
        """API 오류 처리 테스트"""
        # 잘못된 파라미터로 기간별 통계 조회
        response = await authenticated_client.get(
            "/api/v1/dashboard/projects/stats",
            params={"period": "invalid", "days": -1}
        )
        
        # 400 오류가 발생하거나 빈 결과를 반환해야 함
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            # 잘못된 파라미터의 경우 빈 stats_by_date를 반환
            assert "stats_by_date" in data["data"]
            
    @pytest.mark.asyncio
    async def test_unauthorized_access_all_endpoints(
        self, async_client: AsyncClient
    ):
        """모든 대시보드 엔드포인트 인증 확인"""
        endpoints = [
            "/api/v1/dashboard/stats",
            "/api/v1/dashboard/projects/stats",
            "/api/v1/dashboard/projects/popular", 
            "/api/v1/dashboard/stats/tech-stack",
            "/api/v1/dashboard/stats/categories",
            "/api/v1/dashboard/notes/stats",
            "/api/v1/dashboard/activities"
        ]
        
        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            assert response.status_code == 401
            
            data = response.json()
            # FastAPI 기본 오류 형식 확인
            assert "detail" in data
            assert data["detail"] == "Authorization token required"
            
    @pytest.mark.asyncio
    async def test_cross_user_data_isolation(
        self, test_db: AsyncSession, authenticated_client: AsyncClient, test_user: User
    ):
        """사용자 간 데이터 격리 테스트"""
        # 다른 사용자 생성
        other_user = User(
            email="other@example.com",
            name="Other User",
            github_username="otheruser",
            role=UserRole.USER,
            is_verified=True
        )
        test_db.add(other_user)
        await test_db.commit()
        await test_db.refresh(other_user)
        
        # 다른 사용자의 프로젝트 생성
        other_project = Project(
            owner_id=other_user.id,
            title="Other User Project",
            slug="other-project",
            description="Should not appear in stats",
            view_count=999,
            like_count=99,
            tech_stack=["Java"],
            categories=["Other"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC
        )
        test_db.add(other_project)
        await test_db.commit()
        
        # 현재 사용자의 통계 조회
        response = await authenticated_client.get("/api/v1/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        stats = data["data"]
        
        # 다른 사용자의 데이터가 포함되지 않았는지 확인
        assert stats["total_projects"] == 0  # test_user는 프로젝트가 없음
        assert stats["total_views"] == 0
        assert stats["total_likes"] == 0