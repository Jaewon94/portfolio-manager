"""
테스트 설정 및 공통 fixtures

Portfolio Manager 백엔드 테스트를 위한 공통 설정과 fixtures를 제공합니다.
테스트 유형별로 최적화된 설정을 제공하며, PostgreSQL 테스트 데이터베이스를 사용합니다.
"""

import asyncio
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 테스트 환경 변수 설정 및 로드
os.environ["ENVIRONMENT"] = "test"
load_dotenv(".env.test")

from alembic import command
from alembic.config import Config
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.media import Media, MediaTargetType, MediaType
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User, UserRole

# =============================================================================
# 세션 레벨 설정
# =============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """세션 단위 이벤트 루프 생성"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_test_database() -> AsyncGenerator[None, None]:
    """테스트 데이터베이스 초기 설정"""
    # 관리용 데이터베이스 연결
    admin_url = settings.TEST_DATABASE_URL.replace(
        "/portfolio_manager_test", "/postgres"
    )
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        async with admin_engine.connect() as conn:
            # 테스트 데이터베이스가 존재하는지 확인
            result = await conn.execute(
                text(
                    "SELECT 1 FROM pg_database WHERE datname = 'portfolio_manager_test'"
                )
            )
            if not result.fetchone():
                # 테스트 데이터베이스 생성
                await conn.execute(text("CREATE DATABASE portfolio_manager_test"))
                print("테스트 데이터베이스 'portfolio_manager_test' 생성됨")
    except Exception as e:
        print(f"테스트 데이터베이스 설정 중 오류: {e}")
        pass
    finally:
        await admin_engine.dispose()

    # 테스트 데이터베이스에 마이그레이션 적용
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.TEST_DATABASE_URL)

    try:
        command.upgrade(alembic_cfg, "head")
        print("테스트 데이터베이스에 마이그레이션 적용 완료")
    except Exception as e:
        print(f"마이그레이션 적용 중 오류: {e}")

    yield


# =============================================================================
# 데이터베이스 관련 Fixtures
# =============================================================================


@pytest_asyncio.fixture(scope="function")
async def test_db(setup_test_database):
    """테스트용 PostgreSQL 데이터베이스 세션 (각 테스트마다 새로운 세션)"""
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )

    # 세션 생성
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # 테스트 후 데이터 정리
    try:
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(
                    text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE")
                )
    except Exception as e:
        print(f"테스트 데이터 정리 중 오류: {e}")
    finally:
        await engine.dispose()


# =============================================================================
# 테스트 데이터 Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """테스트용 사용자 생성"""
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
    return user


@pytest_asyncio.fixture
async def admin_user(test_db: AsyncSession) -> User:
    """테스트용 관리자 사용자 생성"""
    user = User(
        email="admin@example.com",
        username="adminuser",
        name="Admin User",
        github_username="adminuser",
        role=UserRole.ADMIN,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_project(test_db: AsyncSession, test_user: User) -> Project:
    """테스트용 프로젝트 생성"""
    project = Project(
        owner_id=test_user.id,
        slug="test-project",
        title="Test Project",
        description="Test project description",
        content={"sections": []},
        tech_stack=["Python", "FastAPI"],
        categories=["Backend"],
        tags=["test"],
        status=ProjectStatus.ACTIVE,
        visibility=ProjectVisibility.PUBLIC,
        featured=False,
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest_asyncio.fixture
async def private_project(test_db: AsyncSession, test_user: User) -> Project:
    """테스트용 비공개 프로젝트 생성"""
    project = Project(
        owner_id=test_user.id,
        slug="private-project",
        title="Private Project",
        description="Private project description",
        content={"sections": []},
        tech_stack=["Python"],
        categories=["Backend"],
        tags=["private"],
        status=ProjectStatus.ACTIVE,
        visibility=ProjectVisibility.PRIVATE,
        featured=False,
    )
    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)
    return project


@pytest_asyncio.fixture
async def test_note(test_db: AsyncSession, test_project: Project) -> Note:
    """테스트용 노트 생성"""
    note = Note(
        project_id=test_project.id,
        type=NoteType.LEARN,
        title="Test Note",
        content={"content": "Test note content", "sections": []},
        tags=["test"],
        is_pinned=False,
        is_archived=False,
    )
    test_db.add(note)
    await test_db.commit()
    await test_db.refresh(note)
    return note


# =============================================================================
# API 테스트용 Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 클라이언트 (API 테스트용)"""

    # 테스트용 DB 의존성 오버라이드
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # 의존성 오버라이드 정리
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(
    async_client: AsyncClient, test_user: User
) -> AsyncClient:
    """인증된 클라이언트 (토큰 포함)"""
    from app.core.security import create_access_token

    token = create_access_token(subject=str(test_user.id))
    async_client.headers.update({"Authorization": f"Bearer {token}"})

    # 디버깅용 출력
    print(f"Created token for user_id: {test_user.id}")
    print(f"Token: {token[:50]}...")
    print(f"Authorization header: Bearer {token[:50]}...")

    return async_client


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient, admin_user: User) -> AsyncClient:
    """관리자 인증된 클라이언트"""
    from app.core.security import create_access_token

    token = create_access_token(subject=str(admin_user.id))
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    return async_client


# =============================================================================
# 미디어 테스트용 Fixtures
# =============================================================================


@pytest.fixture
def temp_media_dir() -> Generator[Path, None, None]:
    """임시 미디어 디렉토리 생성"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # 정리
    import shutil

    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_image_file():
    """테스트용 이미지 파일 생성"""
    from io import BytesIO

    from PIL import Image

    def _create_image(
        width: int = 800, height: int = 600, format: str = "PNG"
    ) -> BytesIO:
        image = Image.new("RGB", (width, height), color="red")
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    return _create_image


@pytest.fixture
def test_text_file():
    """테스트용 텍스트 파일 생성"""
    from io import BytesIO

    def _create_file(content: str = "test content") -> BytesIO:
        buffer = BytesIO()
        buffer.write(content.encode())
        buffer.seek(0)
        return buffer

    return _create_file


# =============================================================================
# Mock 관련 Fixtures
# =============================================================================


@pytest.fixture
def mock_upload_file():
    """UploadFile 모의 객체 생성"""

    class MockUploadFile:
        def __init__(self, filename: str, content: BytesIO, content_type: str):
            self.filename = filename
            self.content_type = content_type
            self.file = content
            self.size = len(content.getvalue())

        async def read(self, size: int = -1) -> bytes:
            return self.file.read(size)

        async def seek(self, offset: int, whence: int = 0) -> int:
            return self.file.seek(offset, whence)

        async def close(self):
            self.file.close()

    return MockUploadFile


# =============================================================================
# 테스트 마커 및 설정
# =============================================================================


def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "unit: 단위 테스트 (빠른 실행, 외부 의존성 없음)"
    )
    config.addinivalue_line("markers", "integration: 통합 테스트 (DB 및 서비스 연동)")
    config.addinivalue_line("markers", "api: API 테스트 (HTTP 엔드포인트)")
    config.addinivalue_line("markers", "e2e: E2E 테스트 (전체 워크플로우)")
    config.addinivalue_line("markers", "slow: 느린 테스트 (선택적 실행)")


# =============================================================================
# 테스트 후 정리
# =============================================================================


@pytest_asyncio.fixture(autouse=True)
async def cleanup_after_test():
    """각 테스트 후 자동 정리"""
    yield
    # 필요시 추가 정리 작업
