"""
테스트 설정 및 공통 fixtures
"""

import pytest
import asyncio
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """세션 단위 이벤트 루프 생성"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """비동기 클라이언트 fixture"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# 기존 테스트와의 호환성을 위해 데이터베이스 재설정 fixture도 추가
@pytest.fixture(autouse=True)
async def reset_database():
    """각 테스트 후 데이터베이스 상태 정리"""
    yield
    # 실제 프로덕션에서는 데이터베이스 정리 로직 추가
    # 현재는 테스트 데이터만 사용하므로 생략