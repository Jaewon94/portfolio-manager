"""
대시보드 스키마 단위 테스트
Dashboard schemas: 통계 데이터 검증
"""

from datetime import date, datetime

import pytest

# 스키마가 아직 없으므로 먼저 테스트를 작성 (TDD)
from app.schemas.dashboard import (
    ActivityItem,
    ActivityTimelineResponse,
    CategoryDistribution,
    DashboardStats,
    DashboardStatsResponse,
    DateRangeStats,
    NoteTypeStats,
    PopularProject,
    ProjectStats,
    ProjectStatsResponse,
    TechStackDistribution,
)
from pydantic import ValidationError


class TestDashboardSchemas:
    """대시보드 스키마 단위 테스트"""

    def test_dashboard_stats_schema_valid(self):
        """DashboardStats 스키마 - 유효한 데이터"""
        valid_data = {
            "total_projects": 10,
            "total_notes": 25,
            "total_views": 1500,
            "total_likes": 45,
            "recent_activities": [],
        }

        stats = DashboardStats(**valid_data)
        assert stats.total_projects == 10
        assert stats.total_notes == 25
        assert stats.total_views == 1500
        assert stats.total_likes == 45
        assert stats.recent_activities == []

    def test_dashboard_stats_schema_invalid_negative(self):
        """DashboardStats 스키마 - 음수 값 검증"""
        invalid_data = {
            "total_projects": -1,  # 음수는 허용 안됨
            "total_notes": 25,
            "total_views": 1500,
            "total_likes": 45,
            "recent_activities": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            DashboardStats(**invalid_data)
        assert "greater than or equal to 0" in str(exc_info.value).lower()

    def test_activity_item_schema(self):
        """ActivityItem 스키마 검증"""
        activity_data = {
            "id": 1,
            "type": "project_created",
            "title": "새 프로젝트 생성",
            "description": "포트폴리오 프로젝트를 생성했습니다",
            "created_at": datetime.now(),
            "metadata": {"project_id": "proj-123"},
        }

        activity = ActivityItem(**activity_data)
        assert activity.id == 1
        assert activity.type == "project_created"
        assert activity.title == "새 프로젝트 생성"
        assert isinstance(activity.metadata, dict)

    def test_activity_type_validation(self):
        """ActivityItem 타입 검증"""
        valid_types = [
            "project_created",
            "project_updated",
            "project_deleted",
            "note_added",
            "note_updated",
            "note_deleted",
            "media_uploaded",
        ]

        for activity_type in valid_types:
            activity = ActivityItem(
                id=1,
                type=activity_type,
                title="Test",
                description="Test",
                created_at=datetime.now(),
                metadata={},
            )
            assert activity.type == activity_type

        # 잘못된 타입
        with pytest.raises(ValidationError):
            ActivityItem(
                id=1,
                type="invalid_type",
                title="Test",
                description="Test",
                created_at=datetime.now(),
                metadata={},
            )

    def test_tech_stack_distribution(self):
        """TechStackDistribution 스키마 검증"""
        tech_data = {"name": "Python", "count": 15, "percentage": 35.5}

        tech = TechStackDistribution(**tech_data)
        assert tech.name == "Python"
        assert tech.count == 15
        assert tech.percentage == 35.5

    def test_tech_stack_percentage_validation(self):
        """TechStackDistribution 퍼센트 검증"""
        # 0-100 사이값만 허용
        with pytest.raises(ValidationError):
            TechStackDistribution(name="Python", count=15, percentage=101.0)  # 100 초과

        with pytest.raises(ValidationError):
            TechStackDistribution(name="Python", count=15, percentage=-1.0)  # 음수

    def test_note_type_stats(self):
        """NoteTypeStats 스키마 검증"""
        note_stats = {
            "by_type": {
                "learn": {"count": 10, "recent_count": 3, "percentage": 40.0},
                "change": {"count": 8, "recent_count": 2, "percentage": 32.0},
                "research": {"count": 7, "recent_count": 1, "percentage": 28.0},
            },
            "total": 25,
        }

        stats = NoteTypeStats(**note_stats)
        assert stats.total == 25
        assert stats.by_type["learn"]["count"] == 10
        assert stats.by_type["change"]["count"] == 8
        assert stats.by_type["research"]["count"] == 7

    def test_date_range_stats(self):
        """DateRangeStats 스키마 검증"""
        date_stats = {
            "date": date.today(),
            "project_count": 5,
            "view_count": 150,
            "like_count": 10,
            "note_count": 8,
        }

        stats = DateRangeStats(**date_stats)
        assert stats.date == date.today()
        assert stats.project_count == 5
        assert stats.view_count == 150
        assert stats.like_count == 10
        assert stats.note_count == 8

    def test_popular_project_schema(self):
        """PopularProject 스키마 검증"""
        project_data = {
            "id": 123,
            "title": "인기 프로젝트",
            "slug": "popular-project",
            "view_count": 500,
            "like_count": 25,
            "trend": "up",
            "trend_percentage": 15.5,
        }

        project = PopularProject(**project_data)
        assert project.id == 123
        assert project.trend == "up"
        assert project.trend_percentage == 15.5

    def test_popular_project_trend_validation(self):
        """PopularProject 트렌드 검증"""
        valid_trends = ["up", "down", "stable"]

        for trend in valid_trends:
            project = PopularProject(
                id=1,
                title="Test",
                slug="test",
                view_count=100,
                like_count=10,
                trend=trend,
                trend_percentage=0,
            )
            assert project.trend == trend

        # 잘못된 트렌드
        with pytest.raises(ValidationError):
            PopularProject(
                id=1,
                title="Test",
                slug="test",
                view_count=100,
                like_count=10,
                trend="invalid",
                trend_percentage=0,
            )

    def test_response_schemas(self):
        """응답 스키마 검증"""
        # DashboardStatsResponse
        dashboard_response = DashboardStatsResponse(
            success=True,
            data={
                "total_projects": 10,
                "total_notes": 25,
                "total_views": 1500,
                "total_likes": 45,
                "recent_activities": [],
            },
        )
        assert dashboard_response.success is True
        assert dashboard_response.data.total_projects == 10

        # ProjectStatsResponse
        project_response = ProjectStatsResponse(
            success=True,
            data={
                "stats_by_date": [],
                "total_projects": 10,
                "total_views": 1500,
                "total_likes": 45,
            },
        )
        assert project_response.success is True
        assert project_response.data.total_projects == 10

        # ActivityTimelineResponse
        activity_response = ActivityTimelineResponse(
            success=True, data={"items": [], "total": 0, "has_more": False}
        )
        assert activity_response.success is True
        assert activity_response.data.has_more is False
