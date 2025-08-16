"""
데이터베이스 연결 및 세션 관리
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base  # Base import 경로 수정

# Async 엔진 (메인 사용)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=not settings.is_production,  # 프로덕션에서는 쿼리 로깅 비활성화
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 추가 연결 허용 수
    pool_recycle=3600,  # 1시간마다 연결 재사용
)

# Sync 엔진 (Alembic용)
engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=not settings.is_production,
    future=True,
    pool_pre_ping=True,
    pool_size=5,  # Alembic용은 적은 연결로 충분
    max_overflow=10,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션 의존성
    FastAPI 의존성으로 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """
    동기 데이터베이스 세션 (테스트 또는 스크립트용)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """
    데이터베이스 초기화
    개발 환경에서만 사용, 프로덕션에서는 Alembic 사용
    """
    async with async_engine.begin() as conn:
        # 테이블 생성
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    데이터베이스 연결 종료
    """
    await async_engine.dispose()
