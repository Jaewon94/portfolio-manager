"""
간단한 데이터베이스 연결 테스트
"""

import pytest
from app.models.user import User, UserRole
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestSimpleDatabase:
    """간단한 데이터베이스 테스트"""

    @pytest.mark.asyncio
    async def test_database_connection(self, test_db: AsyncSession):
        """데이터베이스 연결 테스트"""
        # 간단한 쿼리 실행
        result = await test_db.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row[0] == 1

    @pytest.mark.asyncio
    async def test_user_creation(self, test_db: AsyncSession):
        """사용자 생성 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            username="testuser",
            name="Test User",
            github_username="testuser",
            role=UserRole.USER,
            is_verified=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 검증
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
