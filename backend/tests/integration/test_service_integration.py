"""
서비스 레이어 통합 테스트
실제 데이터베이스를 사용하지 않고 서비스 로직만 테스트
"""

from unittest.mock import AsyncMock, Mock

import pytest
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User, UserRole
from app.services.note import NoteService
from app.services.project import ProjectService


@pytest.mark.integration
class TestServiceIntegration:
    """서비스 통합 테스트"""

    def test_project_service_initialization(self):
        """프로젝트 서비스 초기화 테스트"""
        mock_db = Mock()
        service = ProjectService(mock_db)
        assert service.db == mock_db

    def test_note_service_initialization(self):
        """노트 서비스 초기화 테스트"""
        mock_db = Mock()
        service = NoteService(mock_db)
        assert service.db == mock_db

    @pytest.mark.asyncio
    async def test_project_creation_logic(self):
        """프로젝트 생성 로직 테스트 (데이터베이스 없이)"""
        # 모의 데이터베이스 설정
        mock_db = AsyncMock()
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # 프로젝트 서비스 초기화
        service = ProjectService(mock_db)

        # 테스트 데이터
        user = User(
            id=1,
            email="test@example.com",
            name="Test User",
            github_username="testuser",
            role=UserRole.USER,
            is_verified=True,
        )

        project_data = {
            "slug": "test-project",
            "title": "Test Project",
            "description": "Test description",
            "status": ProjectStatus.ACTIVE,
            "visibility": ProjectVisibility.PUBLIC,
        }

        # 프로젝트 생성 (실제 서비스 메서드가 있다면)
        # result = await service.create_project(user.id, project_data)

        # 현재는 서비스 메서드가 구현되지 않았으므로 모델 생성만 테스트
        project = Project(owner_id=user.id, **project_data)

        # 검증
        assert project.owner_id == user.id
        assert project.slug == "test-project"
        assert project.title == "Test Project"
        assert project.status == ProjectStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_note_creation_logic(self):
        """노트 생성 로직 테스트 (데이터베이스 없이)"""
        # 모의 데이터베이스 설정
        mock_db = AsyncMock()
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        # 노트 서비스 초기화
        service = NoteService(mock_db)

        # 테스트 데이터
        project = Project(
            id=1,
            owner_id=1,
            slug="test-project",
            title="Test Project",
        )

        note_data = {
            "type": NoteType.LEARN,
            "title": "Test Note",
            "content": {"content": "Test content"},
            "tags": ["test", "learning"],
        }

        # 노트 생성 (실제 서비스 메서드가 있다면)
        # result = await service.create_note(project.id, note_data)

        # 현재는 서비스 메서드가 구현되지 않았으므로 모델 생성만 테스트
        note = Note(project_id=project.id, **note_data)

        # 검증
        assert note.project_id == project.id
        assert note.type == NoteType.LEARN
        assert note.title == "Test Note"
        assert note.content["content"] == "Test content"

    def test_model_relationships_logic(self):
        """모델 관계 로직 테스트 (메모리상에서)"""
        # 사용자 생성
        user = User(
            id=1,
            email="test@example.com",
            name="Test User",
            github_username="testuser",
        )

        # 프로젝트 생성
        project = Project(
            id=1,
            owner_id=user.id,
            slug="test-project",
            title="Test Project",
        )

        # 노트 생성
        note = Note(
            id=1,
            project_id=project.id,
            type=NoteType.LEARN,
            title="Test Note",
            content={"content": "Test content"},
        )

        # 관계 검증
        assert project.owner_id == user.id
        assert note.project_id == project.id

        # 프로퍼티 메서드 테스트
        assert project.is_public is False  # 기본값은 PRIVATE
        assert note.is_learn_note is True
        assert note.is_change_note is False

    def test_business_logic_validation(self):
        """비즈니스 로직 검증 테스트"""
        # 프로젝트 상태별 로직 테스트
        draft_project = Project(
            id=1,
            owner_id=1,
            slug="draft-project",
            title="Draft Project",
            status=ProjectStatus.DRAFT,
            visibility=ProjectVisibility.PRIVATE,
        )

        active_project = Project(
            id=2,
            owner_id=1,
            slug="active-project",
            title="Active Project",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
        )

        # 상태별 검증
        assert draft_project.status == ProjectStatus.DRAFT
        assert not draft_project.is_public

        assert active_project.status == ProjectStatus.ACTIVE
        assert active_project.is_public

        # 노트 타입별 로직 테스트
        learn_note = Note(
            id=1,
            project_id=1,
            type=NoteType.LEARN,
            title="Learn Note",
            content={"content": "Learning content"},
        )

        change_note = Note(
            id=2,
            project_id=1,
            type=NoteType.CHANGE,
            title="Change Note",
            content={"content": "Change content"},
        )

        research_note = Note(
            id=3,
            project_id=1,
            type=NoteType.RESEARCH,
            title="Research Note",
            content={"content": "Research content"},
        )

        # 타입별 프로퍼티 검증
        assert learn_note.is_learn_note
        assert not learn_note.is_change_note
        assert not learn_note.is_research_note

        assert not change_note.is_learn_note
        assert change_note.is_change_note
        assert not change_note.is_research_note

        assert not research_note.is_learn_note
        assert not research_note.is_change_note
        assert research_note.is_research_note
