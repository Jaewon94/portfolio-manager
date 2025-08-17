"""
대시보드 통계 서비스
Dashboard statistics service
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from app.models.media import Media
from app.models.note import Note
from app.models.project import Project
from app.models.user import User
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


class DashboardService:
    """대시보드 통계 서비스"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_stats(
        self, user_id: int, include_activities: bool = False
    ) -> Dict[str, Any]:
        """사용자 기본 통계 조회"""

        # 프로젝트 수 조회
        project_count_query = select(func.count(Project.id)).where(
            Project.owner_id == user_id
        )
        project_count_result = await self.db.execute(project_count_query)
        total_projects = project_count_result.scalar() or 0

        # 노트 수 조회
        note_count_query = (
            select(func.count(Note.id))
            .join(Project, Note.project_id == Project.id)
            .where(Project.owner_id == user_id)
        )
        note_count_result = await self.db.execute(note_count_query)
        total_notes = note_count_result.scalar() or 0

        # 총 조회수 집계
        view_count_query = select(func.sum(Project.view_count)).where(
            Project.owner_id == user_id
        )
        view_count_result = await self.db.execute(view_count_query)
        total_views = view_count_result.scalar() or 0

        # 총 좋아요 수 집계
        like_count_query = select(func.sum(Project.like_count)).where(
            Project.owner_id == user_id
        )
        like_count_result = await self.db.execute(like_count_query)
        total_likes = like_count_result.scalar() or 0

        stats = {
            "total_projects": total_projects,
            "total_notes": total_notes,
            "total_views": total_views,
            "total_likes": total_likes,
            "recent_activities": [],
        }

        # 최근 활동 포함 시
        if include_activities:
            stats["recent_activities"] = await self._get_recent_activities(
                user_id, limit=5
            )

        return stats

    async def get_project_stats_by_period(
        self,
        user_id: int,
        period: str = "daily",
        days: Optional[int] = None,
        months: Optional[int] = None,
    ) -> Dict[str, Any]:
        """기간별 프로젝트 통계 조회"""

        if period == "daily" and days:
            stats_by_date = await self._aggregate_daily_stats(user_id, days)
        elif period == "monthly" and months:
            stats_by_date = await self._aggregate_monthly_stats(user_id, months)
        else:
            stats_by_date = []

        # 전체 통계도 함께 반환
        user_stats = await self.get_user_stats(user_id)

        return {
            "stats_by_date": stats_by_date,
            "total_projects": user_stats["total_projects"],
            "total_views": user_stats["total_views"],
            "total_likes": user_stats["total_likes"],
        }

    async def get_popular_projects(
        self, user_id: int, limit: int = 5
    ) -> Dict[str, Any]:
        """인기 프로젝트 조회"""

        projects = await self._get_top_projects(user_id, limit)

        # 트렌드 계산 (지난 주 대비)
        projects_with_trend = []
        for project in projects:
            trend_data = await self._calculate_project_trend(project["id"])
            project.update(trend_data)
            projects_with_trend.append(project)

        return {"items": projects_with_trend}

    async def get_tech_stack_distribution(self, user_id: int) -> Dict[str, Any]:
        """기술 스택 분포 조회"""

        distribution = await self._calculate_tech_distribution(user_id)
        total_projects = await self._get_total_projects(user_id)

        return {"distribution": distribution, "total_projects": total_projects}

    async def get_category_distribution(self, user_id: int) -> Dict[str, Any]:
        """카테고리 분포 조회"""

        distribution = await self._calculate_category_distribution(user_id)
        total_projects = await self._get_total_projects(user_id)

        return {"distribution": distribution, "total_projects": total_projects}

    async def get_note_type_stats(self, user_id: int) -> Dict[str, Any]:
        """노트 타입별 통계 조회"""

        stats = await self._calculate_note_type_stats(user_id)
        return stats

    async def get_note_stats_by_type(self, user_id: int) -> Dict[str, Any]:
        """노트 타입별 통계 조회 (API 엔드포인트용)"""

        stats = await self._calculate_note_type_stats(user_id)
        return stats

    async def get_activity_timeline(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """활동 타임라인 조회"""

        activities = await self._get_user_activities(user_id, limit, offset)
        total = await self._get_total_activities(user_id)
        has_more = (offset + limit) < total

        return {"items": activities, "total": total, "has_more": has_more}

    # Private helper methods

    async def _get_recent_activities(
        self, user_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """최근 활동 조회"""

        # 실제 구현에서는 활동 로그 테이블에서 조회
        # 현재는 mock 데이터 반환
        activities = [
            {
                "id": i,
                "type": "project_created",
                "title": f"프로젝트 생성 {i}",
                "description": f"새로운 프로젝트를 생성했습니다 {i}",
                "created_at": datetime.now() - timedelta(hours=i),
                "metadata": {"project_id": i},
            }
            for i in range(limit)
        ]
        return activities

    async def _aggregate_daily_stats(
        self, user_id: int, days: int
    ) -> List[Dict[str, Any]]:
        """일별 통계 집계"""

        stats = []
        today = date.today()

        for i in range(days):
            stat_date = today - timedelta(days=i)

            # 실제 구현에서는 DB 집계 쿼리 사용
            daily_stat = {
                "date": stat_date,
                "project_count": 1 + i,  # Mock 데이터
                "view_count": 50 + (i * 10),
                "like_count": 5 + i,
                "note_count": 2 + i,
            }
            stats.append(daily_stat)

        return stats

    async def _aggregate_monthly_stats(
        self, user_id: int, months: int
    ) -> List[Dict[str, Any]]:
        """월별 통계 집계"""

        stats = []
        today = date.today()

        for i in range(months):
            # 월의 첫 날 계산
            month_date = today.replace(day=1) - timedelta(days=i * 30)

            monthly_stat = {
                "date": month_date,
                "project_count": 10 + i,  # Mock 데이터
                "view_count": 500 + (i * 100),
                "like_count": 50 + (i * 10),
                "note_count": 25 + (i * 5),
            }
            stats.append(monthly_stat)

        return stats

    async def _get_top_projects(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """인기 프로젝트 조회"""

        query = (
            select(
                Project.id,
                Project.title,
                Project.slug,
                Project.view_count,
                Project.like_count,
            )
            .where(Project.owner_id == user_id)
            .order_by(desc(Project.view_count), desc(Project.like_count))
            .limit(limit)
        )

        result = await self.db.execute(query)
        projects = []

        for row in result:
            projects.append(
                {
                    "id": str(row.id),
                    "title": row.title,
                    "slug": row.slug,
                    "view_count": row.view_count,
                    "like_count": row.like_count,
                }
            )

        return projects

    async def _calculate_project_trend(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 트렌드 계산"""

        # 실제 구현에서는 과거 데이터와 비교
        # 현재는 mock 트렌드 반환
        return {"trend": "up", "trend_percentage": 15.5}

    async def _calculate_tech_distribution(self, user_id: int) -> List[Dict[str, Any]]:
        """기술 스택 분포 계산"""

        # PostgreSQL array 함수 사용하여 tech_stack 집계
        query = text(
            """
            SELECT 
                unnest(tech_stack) as tech,
                COUNT(*) as count
            FROM projects 
            WHERE owner_id = :user_id 
            GROUP BY unnest(tech_stack)
            ORDER BY count DESC
        """
        )

        result = await self.db.execute(query, {"user_id": user_id})
        tech_counts = result.fetchall()

        if not tech_counts:
            return []

        total = sum(row.count for row in tech_counts)
        distribution = []

        for row in tech_counts:
            percentage = (row.count / total) * 100 if total > 0 else 0
            distribution.append(
                {
                    "name": row.tech,
                    "count": row.count,
                    "percentage": round(percentage, 1),
                }
            )

        return distribution

    async def _calculate_category_distribution(
        self, user_id: int
    ) -> List[Dict[str, Any]]:
        """카테고리 분포 계산"""

        # PostgreSQL array 함수 사용하여 categories 집계
        query = text(
            """
            SELECT 
                unnest(categories) as category,
                COUNT(*) as count
            FROM projects 
            WHERE owner_id = :user_id 
            GROUP BY unnest(categories)
            ORDER BY count DESC
        """
        )

        result = await self.db.execute(query, {"user_id": user_id})
        category_counts = result.fetchall()

        if not category_counts:
            return []

        total = sum(row.count for row in category_counts)
        distribution = []

        for row in category_counts:
            percentage = (row.count / total) * 100 if total > 0 else 0
            distribution.append(
                {
                    "name": row.category,
                    "count": row.count,
                    "percentage": round(percentage, 1),
                }
            )

        return distribution

    async def _calculate_note_type_stats(self, user_id: int) -> Dict[str, Any]:
        """노트 타입별 통계 계산"""

        # 전체 노트 수 조회
        total_query = (
            select(func.count(Note.id))
            .join(Project, Note.project_id == Project.id)
            .where(Project.owner_id == user_id)
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # 타입별 집계
        from app.models.note import NoteType

        type_stats = {}
        note_types = [NoteType.LEARN, NoteType.CHANGE, NoteType.RESEARCH]

        for note_type in note_types:
            # 타입별 전체 수
            type_query = (
                select(func.count(Note.id))
                .join(Project, Note.project_id == Project.id)
                .where(and_(Project.owner_id == user_id, Note.type == note_type))
            )
            type_result = await self.db.execute(type_query)
            count = type_result.scalar() or 0

            # 최근 7일 수
            recent_query = (
                select(func.count(Note.id))
                .join(Project, Note.project_id == Project.id)
                .where(
                    and_(
                        Project.owner_id == user_id,
                        Note.type == note_type,
                        Note.created_at >= datetime.now() - timedelta(days=7),
                    )
                )
            )
            recent_result = await self.db.execute(recent_query)
            recent_count = recent_result.scalar() or 0

            percentage = (count / total) * 100 if total > 0 else 0

            type_stats[note_type.value] = {
                "count": count,
                "recent_count": recent_count,
                "percentage": round(percentage, 1),
            }

        return {"by_type": type_stats, "total": total}

    async def _get_user_activities(
        self, user_id: int, limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """사용자 활동 조회"""

        # 실제 구현에서는 활동 로그 테이블에서 조회
        # 현재는 mock 데이터 반환
        activities = []
        for i in range(limit):
            activities.append(
                {
                    "id": offset + i,
                    "type": "project_created" if i % 2 == 0 else "note_added",
                    "title": f"활동 {offset + i}",
                    "description": f"활동 설명 {offset + i}",
                    "created_at": datetime.now() - timedelta(hours=i),
                    "metadata": {},
                }
            )

        return activities

    async def _get_total_activities(self, user_id: int) -> int:
        """전체 활동 수 조회"""
        # Mock 데이터
        return 50

    async def _get_total_projects(self, user_id: int) -> int:
        """총 프로젝트 수 조회"""
        query = select(func.count(Project.id)).where(Project.owner_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    def _calculate_trend(
        self, current: Dict[str, int], previous: Dict[str, int]
    ) -> Dict[str, Any]:
        """트렌드 계산 (공통 유틸리티)"""

        current_total = current.get("view_count", 0) + current.get("like_count", 0)
        previous_total = previous.get("view_count", 0) + previous.get("like_count", 0)

        if previous_total == 0:
            if current_total > 0:
                return {"trend": "up", "percentage": 100.0}
            else:
                return {"trend": "stable", "percentage": 0.0}

        percentage_change = ((current_total - previous_total) / previous_total) * 100

        if percentage_change > 5:
            trend = "up"
        elif percentage_change < -5:
            trend = "down"
        else:
            trend = "stable"

        return {"trend": trend, "percentage": round(percentage_change, 1)}
