"""
대시보드 서비스 단위 테스트
Dashboard service unit tests
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.models.note import Note
from app.models.project import Project
from app.models.user import User
from app.services.dashboard import DashboardService
from sqlalchemy.ext.asyncio import AsyncSession


class TestDashboardService:
    """대시보드 서비스 단위 테스트"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def dashboard_service(self, mock_db):
        """Dashboard service instance"""
        return DashboardService(mock_db)

    @pytest.fixture
    def mock_user(self):
        """Mock user"""
        user = MagicMock(spec=User)
        user.id = "user-123"
        user.email = "test@example.com"
        user.name = "Test User"
        return user

    @pytest.mark.asyncio
    async def test_get_user_stats_basic(self, dashboard_service, mock_db, mock_user):
        """사용자 기본 통계 조회"""
        # Mock 데이터 설정
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5  # 프로젝트 수
        mock_db.execute.return_value = mock_result

        # 서비스 호출
        stats = await dashboard_service.get_user_stats(mock_user.id)

        # 검증
        assert stats is not None
        assert "total_projects" in stats
        assert "total_notes" in stats
        assert "total_views" in stats
        assert "total_likes" in stats

    @pytest.mark.asyncio
    async def test_get_user_stats_with_recent_activities(
        self, dashboard_service, mock_db, mock_user
    ):
        """최근 활동 포함 통계 조회"""
        # Mock 활동 데이터
        mock_activities = [
            {
                "id": "act-1",
                "type": "project_created",
                "title": "새 프로젝트",
                "description": "프로젝트를 생성했습니다",
                "created_at": datetime.now(),
                "metadata": {"project_id": "proj-1"},
            }
        ]

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_get_recent_activities",
            new_callable=AsyncMock,
            return_value=mock_activities,
        ):
            stats = await dashboard_service.get_user_stats(
                mock_user.id, include_activities=True
            )

            assert "recent_activities" in stats
            assert len(stats["recent_activities"]) > 0

    @pytest.mark.asyncio
    async def test_get_project_stats_by_period_daily(
        self, dashboard_service, mock_db, mock_user
    ):
        """일별 프로젝트 통계 조회"""
        # 7일간의 통계 데이터 생성
        today = date.today()
        daily_stats = []

        for i in range(7):
            stat_date = today - timedelta(days=i)
            daily_stats.append(
                {
                    "date": stat_date,
                    "project_count": 2 + i,
                    "view_count": 100 + (i * 10),
                    "like_count": 5 + i,
                    "note_count": 3 + i,
                }
            )

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_aggregate_daily_stats",
            new_callable=AsyncMock,
            return_value=daily_stats,
        ):
            stats = await dashboard_service.get_project_stats_by_period(
                user_id=mock_user.id, period="daily", days=7
            )

            assert "stats_by_date" in stats
            assert len(stats["stats_by_date"]) == 7
            assert stats["stats_by_date"][0]["date"] == today

    @pytest.mark.asyncio
    async def test_get_project_stats_by_period_monthly(
        self, dashboard_service, mock_db, mock_user
    ):
        """월별 프로젝트 통계 조회"""
        stats = await dashboard_service.get_project_stats_by_period(
            user_id=mock_user.id, period="monthly", months=3
        )

        assert "stats_by_date" in stats
        assert "total_projects" in stats
        assert "total_views" in stats
        assert "total_likes" in stats

    @pytest.mark.asyncio
    async def test_get_popular_projects(self, dashboard_service, mock_db, mock_user):
        """인기 프로젝트 조회"""
        # Mock 프로젝트 데이터
        mock_projects = [
            {
                "id": "proj-1",
                "title": "Popular Project 1",
                "slug": "popular-1",
                "view_count": 500,
                "like_count": 50,
            },
            {
                "id": "proj-2",
                "title": "Popular Project 2",
                "slug": "popular-2",
                "view_count": 300,
                "like_count": 30,
            },
        ]

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_get_top_projects",
            new_callable=AsyncMock,
            return_value=mock_projects,
        ):
            popular = await dashboard_service.get_popular_projects(
                user_id=mock_user.id, limit=5
            )

            assert "items" in popular
            assert len(popular["items"]) == 2
            assert popular["items"][0]["view_count"] > popular["items"][1]["view_count"]

    @pytest.mark.asyncio
    async def test_get_tech_stack_distribution(
        self, dashboard_service, mock_db, mock_user
    ):
        """기술 스택 분포 조회"""
        # Mock 기술 스택 데이터
        mock_distribution = [
            {"name": "Python", "count": 10, "percentage": 40.0},
            {"name": "JavaScript", "count": 8, "percentage": 32.0},
            {"name": "TypeScript", "count": 7, "percentage": 28.0},
        ]

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_calculate_tech_distribution",
            new_callable=AsyncMock,
            return_value=mock_distribution,
        ):
            distribution = await dashboard_service.get_tech_stack_distribution(
                user_id=mock_user.id
            )

            assert "distribution" in distribution
            assert len(distribution["distribution"]) == 3
            assert distribution["distribution"][0]["name"] == "Python"

            # 퍼센트 합계 검증
            total_percentage = sum(
                tech["percentage"] for tech in distribution["distribution"]
            )
            assert total_percentage == 100.0

    @pytest.mark.asyncio
    async def test_get_category_distribution(
        self, dashboard_service, mock_db, mock_user
    ):
        """카테고리 분포 조회"""
        # Mock 카테고리 데이터
        mock_distribution = [
            {"name": "Backend", "count": 12, "percentage": 48.0},
            {"name": "Frontend", "count": 8, "percentage": 32.0},
            {"name": "DevOps", "count": 5, "percentage": 20.0},
        ]

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_calculate_category_distribution",
            new_callable=AsyncMock,
            return_value=mock_distribution,
        ):
            distribution = await dashboard_service.get_category_distribution(
                user_id=mock_user.id
            )

            assert "distribution" in distribution
            assert len(distribution["distribution"]) == 3
            assert distribution["distribution"][0]["name"] == "Backend"

    @pytest.mark.asyncio
    async def test_get_note_type_stats(self, dashboard_service, mock_db, mock_user):
        """노트 타입별 통계 조회"""
        # Mock 노트 통계 데이터
        mock_stats = {
            "by_type": {
                "learn": {"count": 10, "recent_count": 3, "percentage": 40.0},
                "change": {"count": 8, "recent_count": 2, "percentage": 32.0},
                "research": {"count": 7, "recent_count": 1, "percentage": 28.0},
            },
            "total": 25,
        }

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_calculate_note_type_stats",
            new_callable=AsyncMock,
            return_value=mock_stats,
        ):
            stats = await dashboard_service.get_note_type_stats(user_id=mock_user.id)

            assert "by_type" in stats
            assert "total" in stats
            assert stats["total"] == 25
            assert "learn" in stats["by_type"]
            assert "change" in stats["by_type"]
            assert "research" in stats["by_type"]

    @pytest.mark.asyncio
    async def test_get_activity_timeline(self, dashboard_service, mock_db, mock_user):
        """활동 타임라인 조회"""
        # Mock 활동 데이터
        mock_activities = [
            {
                "id": "act-1",
                "type": "project_created",
                "title": "프로젝트 생성",
                "description": "새 프로젝트를 만들었습니다",
                "created_at": datetime.now(),
                "metadata": {},
            },
            {
                "id": "act-2",
                "type": "note_added",
                "title": "노트 추가",
                "description": "학습 노트를 추가했습니다",
                "created_at": datetime.now() - timedelta(hours=1),
                "metadata": {},
            },
        ]

        # Mock 설정
        with patch.object(
            dashboard_service,
            "_get_user_activities",
            new_callable=AsyncMock,
            return_value=mock_activities,
        ):
            timeline = await dashboard_service.get_activity_timeline(
                user_id=mock_user.id, limit=10, offset=0
            )

            assert "items" in timeline
            assert "total" in timeline
            assert "has_more" in timeline
            assert len(timeline["items"]) == 2

    @pytest.mark.asyncio
    async def test_calculate_project_trend(self, dashboard_service):
        """프로젝트 트렌드 계산 테스트"""
        # 상승 트렌드
        current_stats = {"view_count": 150, "like_count": 15}
        previous_stats = {"view_count": 100, "like_count": 10}

        trend = dashboard_service._calculate_trend(current_stats, previous_stats)
        assert trend["trend"] == "up"
        assert trend["percentage"] > 0

        # 하락 트렌드
        current_stats = {"view_count": 80, "like_count": 8}
        previous_stats = {"view_count": 100, "like_count": 10}

        trend = dashboard_service._calculate_trend(current_stats, previous_stats)
        assert trend["trend"] == "down"
        assert trend["percentage"] < 0

        # 안정 트렌드
        current_stats = {"view_count": 100, "like_count": 10}
        previous_stats = {"view_count": 100, "like_count": 10}

        trend = dashboard_service._calculate_trend(current_stats, previous_stats)
        assert trend["trend"] == "stable"
        assert trend["percentage"] == 0
