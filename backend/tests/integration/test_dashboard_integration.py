"""
대시보드 통계 통합 테스트
Dashboard service integration tests with real database
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.dashboard import DashboardService
from app.models.user import User
from app.models.project import Project
from app.models.note import Note, NoteType
from app.models.media import Media


@pytest.mark.integration
@pytest.mark.dashboard
class TestDashboardIntegration:
    """대시보드 서비스 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_get_user_stats_with_real_data(
        self, test_db: AsyncSession, test_user: User
    ):
        """실제 데이터로 사용자 통계 조회"""
        dashboard_service = DashboardService(test_db)
        
        # 테스트 데이터 생성
        project1 = Project(
            owner_id=test_user.id,
            title="Test Project 1",
            slug="test-project-1",
            description="Test project description",
            view_count=100,
            like_count=10,
            tech_stack=["Python", "FastAPI"],
            categories=["Backend"]
        )
        
        project2 = Project(
            owner_id=test_user.id,
            title="Test Project 2", 
            slug="test-project-2",
            description="Another test project",
            view_count=200,
            like_count=20,
            tech_stack=["JavaScript", "React"],
            categories=["Frontend"]
        )
        
        test_db.add(project1)
        test_db.add(project2)
        await test_db.commit()
        await test_db.refresh(project1)
        await test_db.refresh(project2)
        
        # 노트 생성
        note1 = Note(
            project_id=project1.id,
            type=NoteType.LEARN,
            title="Learning Note",
            content={"blocks": [{"type": "paragraph", "data": {"text": "Test content"}}]}
        )
        
        note2 = Note(
            project_id=project2.id,
            type=NoteType.CHANGE,
            title="Change Note",
            content={"blocks": [{"type": "paragraph", "data": {"text": "Change content"}}]}
        )
        
        test_db.add(note1)
        test_db.add(note2)
        await test_db.commit()
        
        # 통계 조회
        stats = await dashboard_service.get_user_stats(test_user.id)
        
        # 검증
        assert stats["total_projects"] == 2
        assert stats["total_notes"] == 2
        assert stats["total_views"] == 300  # 100 + 200
        assert stats["total_likes"] == 30   # 10 + 20
        assert isinstance(stats["recent_activities"], list)
        
    @pytest.mark.asyncio
    async def test_get_popular_projects_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """인기 프로젝트 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 다양한 조회수/좋아요 수를 가진 프로젝트 생성
        projects_data = [
            {"title": "Most Popular", "slug": "most-popular", "view_count": 1000, "like_count": 100},
            {"title": "Second Popular", "slug": "second-popular", "view_count": 500, "like_count": 50},
            {"title": "Third Popular", "slug": "third-popular", "view_count": 200, "like_count": 20},
            {"title": "Least Popular", "slug": "least-popular", "view_count": 50, "like_count": 5}
        ]
        
        for project_data in projects_data:
            project = Project(
                owner_id=test_user.id,
                title=project_data["title"],
                slug=project_data["slug"],
                description="Test description",
                view_count=project_data["view_count"],
                like_count=project_data["like_count"],
                tech_stack=["Python"],
                categories=["Backend"]
            )
            test_db.add(project)
        
        await test_db.commit()
        
        # 인기 프로젝트 조회
        popular = await dashboard_service.get_popular_projects(test_user.id, limit=3)
        
        # 검증
        assert "items" in popular
        assert len(popular["items"]) == 3
        
        # 조회수 순으로 정렬되었는지 확인
        items = popular["items"]
        assert items[0]["title"] == "Most Popular"
        assert items[1]["title"] == "Second Popular"  
        assert items[2]["title"] == "Third Popular"
        
        # 조회수가 내림차순으로 정렬되었는지 확인
        assert items[0]["view_count"] >= items[1]["view_count"]
        assert items[1]["view_count"] >= items[2]["view_count"]
        
    @pytest.mark.asyncio
    async def test_tech_stack_distribution_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """기술 스택 분포 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 다양한 기술 스택을 가진 프로젝트 생성
        tech_projects = [
            {"tech_stack": ["Python", "FastAPI", "PostgreSQL"]},
            {"tech_stack": ["Python", "Django"]},
            {"tech_stack": ["JavaScript", "React", "Node.js"]},
            {"tech_stack": ["Python", "Flask"]},
            {"tech_stack": ["JavaScript", "Vue.js"]}
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
                like_count=10
            )
            test_db.add(project)
        
        await test_db.commit()
        
        # 기술 스택 분포 조회
        distribution = await dashboard_service.get_tech_stack_distribution(test_user.id)
        
        # 검증
        assert "distribution" in distribution
        assert "total_projects" in distribution
        assert distribution["total_projects"] == 5
        
        # 분포 데이터 확인
        tech_dist = distribution["distribution"]
        assert len(tech_dist) > 0
        
        # Python이 가장 많이 사용되었는지 확인 (3번)
        python_entry = next((item for item in tech_dist if item["name"] == "Python"), None)
        assert python_entry is not None
        assert python_entry["count"] == 3
        
        # 백분율 계산 확인
        total_percentage = sum(item["percentage"] for item in tech_dist)
        assert abs(total_percentage - 100.0) < 0.5  # 부동소수점 오차 허용
        
    @pytest.mark.asyncio
    async def test_category_distribution_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """카테고리 분포 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 다양한 카테고리를 가진 프로젝트 생성
        category_projects = [
            {"categories": ["Backend", "API"]},
            {"categories": ["Frontend", "Web"]},
            {"categories": ["Backend", "Database"]},
            {"categories": ["Mobile", "iOS"]},
            {"categories": ["Frontend", "React"]}
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
                like_count=10
            )
            test_db.add(project)
        
        await test_db.commit()
        
        # 카테고리 분포 조회
        distribution = await dashboard_service.get_category_distribution(test_user.id)
        
        # 검증
        assert "distribution" in distribution
        assert "total_projects" in distribution
        assert distribution["total_projects"] == 5
        
        # 분포 데이터 확인
        category_dist = distribution["distribution"]
        assert len(category_dist) > 0
        
        # Backend가 가장 많이 사용되었는지 확인 (2번)
        backend_entry = next((item for item in category_dist if item["name"] == "Backend"), None)
        assert backend_entry is not None
        assert backend_entry["count"] == 2
        
        # Frontend 확인 (2번)
        frontend_entry = next((item for item in category_dist if item["name"] == "Frontend"), None)
        assert frontend_entry is not None
        assert frontend_entry["count"] == 2
        
    @pytest.mark.asyncio
    async def test_note_type_stats_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """노트 타입별 통계 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 프로젝트 생성
        project = Project(
            owner_id=test_user.id,
            title="Note Test Project",
            slug="note-test-project",
            description="Test project for notes",
            tech_stack=["Python"],
            categories=["Backend"],
            view_count=100,
            like_count=10
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)
        
        # 다양한 타입의 노트 생성
        note_types_data = [
            {"type": NoteType.LEARN, "count": 5},
            {"type": NoteType.CHANGE, "count": 3},
            {"type": NoteType.RESEARCH, "count": 2}
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
        
        # 노트 타입별 통계 조회
        stats = await dashboard_service.get_note_type_stats(test_user.id)
        
        # 검증
        assert "by_type" in stats
        assert "total" in stats
        assert stats["total"] == 10  # 5 + 3 + 2
        
        # 타입별 통계 확인
        by_type = stats["by_type"]
        assert "learn" in by_type
        assert "change" in by_type
        assert "research" in by_type
        
        # learn 타입 확인
        learn_stats = by_type["learn"]
        assert learn_stats["count"] == 5
        assert learn_stats["percentage"] == 50.0  # 5/10 * 100
        
        # change 타입 확인
        change_stats = by_type["change"]
        assert change_stats["count"] == 3
        assert change_stats["percentage"] == 30.0  # 3/10 * 100
        
        # research 타입 확인
        research_stats = by_type["research"]
        assert research_stats["count"] == 2
        assert research_stats["percentage"] == 20.0  # 2/10 * 100
        
    @pytest.mark.asyncio
    async def test_activity_timeline_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """활동 타임라인 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 활동 타임라인 조회 (현재는 mock 데이터 반환)
        timeline = await dashboard_service.get_activity_timeline(
            user_id=test_user.id,
            limit=5,
            offset=0
        )
        
        # 검증
        assert "items" in timeline
        assert "total" in timeline
        assert "has_more" in timeline
        
        assert isinstance(timeline["items"], list)
        assert isinstance(timeline["total"], int)
        assert isinstance(timeline["has_more"], bool)
        
        # 활동 항목 구조 확인
        if timeline["items"]:
            activity = timeline["items"][0]
            assert "id" in activity
            assert "type" in activity
            assert "title" in activity
            assert "description" in activity
            assert "created_at" in activity
            assert "metadata" in activity
            
    @pytest.mark.asyncio
    async def test_project_stats_by_period_integration(
        self, test_db: AsyncSession, test_user: User
    ):
        """기간별 프로젝트 통계 통합 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 프로젝트 생성
        project = Project(
            owner_id=test_user.id,
            title="Period Stats Project",
            slug="period-stats-project",
            description="Test project for period stats",
            tech_stack=["Python"],
            categories=["Backend"],
            view_count=500,
            like_count=25
        )
        test_db.add(project)
        await test_db.commit()
        
        # 일별 통계 조회
        daily_stats = await dashboard_service.get_project_stats_by_period(
            user_id=test_user.id,
            period="daily",
            days=7
        )
        
        # 검증
        assert "stats_by_date" in daily_stats
        assert "total_projects" in daily_stats
        assert "total_views" in daily_stats
        assert "total_likes" in daily_stats
        
        assert daily_stats["total_projects"] == 1
        assert daily_stats["total_views"] == 500
        assert daily_stats["total_likes"] == 25
        
        # 일별 통계 데이터 확인
        stats_by_date = daily_stats["stats_by_date"]
        assert isinstance(stats_by_date, list)
        assert len(stats_by_date) == 7  # 7일간
        
        if stats_by_date:
            daily_stat = stats_by_date[0]
            assert "date" in daily_stat
            assert "project_count" in daily_stat
            assert "view_count" in daily_stat
            assert "like_count" in daily_stat
            assert "note_count" in daily_stat
            
        # 월별 통계 조회
        monthly_stats = await dashboard_service.get_project_stats_by_period(
            user_id=test_user.id,
            period="monthly",
            months=3
        )
        
        # 검증
        assert "stats_by_date" in monthly_stats
        monthly_stats_by_date = monthly_stats["stats_by_date"]
        assert isinstance(monthly_stats_by_date, list)
        assert len(monthly_stats_by_date) == 3  # 3개월간
        
    @pytest.mark.asyncio
    async def test_empty_user_stats(
        self, test_db: AsyncSession, test_user: User
    ):
        """빈 데이터에 대한 통계 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 프로젝트나 노트가 없는 상태에서 통계 조회
        stats = await dashboard_service.get_user_stats(test_user.id)
        
        # 검증 - 모든 값이 0이어야 함
        assert stats["total_projects"] == 0
        assert stats["total_notes"] == 0
        assert stats["total_views"] == 0
        assert stats["total_likes"] == 0
        assert stats["recent_activities"] == []
        
        # 기술 스택 분포도 빈 값이어야 함
        tech_distribution = await dashboard_service.get_tech_stack_distribution(test_user.id)
        assert tech_distribution["distribution"] == []
        assert tech_distribution["total_projects"] == 0
        
        # 카테고리 분포도 빈 값이어야 함
        category_distribution = await dashboard_service.get_category_distribution(test_user.id)
        assert category_distribution["distribution"] == []
        assert category_distribution["total_projects"] == 0
        
    @pytest.mark.asyncio
    async def test_calculate_trend_utility(self, test_db: AsyncSession):
        """트렌드 계산 유틸리티 함수 테스트"""
        dashboard_service = DashboardService(test_db)
        
        # 상승 트렌드
        current = {"view_count": 150, "like_count": 15}
        previous = {"view_count": 100, "like_count": 10}
        trend = dashboard_service._calculate_trend(current, previous)
        
        assert trend["trend"] == "up"
        assert trend["percentage"] > 0
        
        # 하락 트렌드
        current = {"view_count": 80, "like_count": 8}
        previous = {"view_count": 100, "like_count": 10}
        trend = dashboard_service._calculate_trend(current, previous)
        
        assert trend["trend"] == "down"
        assert trend["percentage"] < 0
        
        # 안정 트렌드
        current = {"view_count": 100, "like_count": 10}
        previous = {"view_count": 100, "like_count": 10}
        trend = dashboard_service._calculate_trend(current, previous)
        
        assert trend["trend"] == "stable"
        assert trend["percentage"] == 0