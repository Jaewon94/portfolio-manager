"""
단위 테스트: 모델 테스트
SQLAlchemy 모델의 생성, 검증, 관계 등을 테스트합니다.
"""

from datetime import datetime, timezone

import pytest
from app.models.media import Media, MediaTargetType, MediaType
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.unit
class TestUserModel:
    """사용자 모델 단위 테스트"""

    def test_user_creation(self):
        """사용자 모델 객체 생성 테스트"""
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
            role=UserRole.USER,
            is_verified=True,
        )

        # 모델 객체 속성 검증
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.github_username == "testuser"
        assert user.role == UserRole.USER
        assert user.is_verified is True

    def test_user_with_explicit_values(self):
        """사용자 명시적 값 설정 테스트"""
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
            role=UserRole.ADMIN,
            is_verified=True,
            is_active=False,
        )

        # 명시적으로 설정한 값 검증
        assert user.role == UserRole.ADMIN
        assert user.is_verified is True
        assert user.is_active is False


@pytest.mark.unit
class TestProjectModel:
    """프로젝트 모델 단위 테스트"""

    def test_project_creation(self):
        """프로젝트 모델 객체 생성 테스트"""
        project = Project(
            owner_id=1,  # 테스트용 고정 ID
            slug="test-project",
            title="Test Project",
            description="Test description",
            content={"sections": []},
            tech_stack=["Python", "FastAPI"],
            categories=["Backend"],
            tags=["test", "api"],
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
            featured=True,
        )

        # 모델 객체 속성 검증
        assert project.owner_id == 1
        assert project.slug == "test-project"
        assert project.title == "Test Project"
        assert project.tech_stack == ["Python", "FastAPI"]
        assert project.status == ProjectStatus.ACTIVE
        assert project.visibility == ProjectVisibility.PUBLIC
        assert project.featured is True

    def test_project_with_explicit_values(self):
        """프로젝트 명시적 값 설정 테스트"""
        project = Project(
            owner_id=1,
            slug="test-project",
            title="Test Project",
            status=ProjectStatus.ARCHIVED,
            visibility=ProjectVisibility.UNLISTED,
            featured=True,
            view_count=100,
            like_count=50,
        )

        # 명시적으로 설정한 값 검증
        assert project.status == ProjectStatus.ARCHIVED
        assert project.visibility == ProjectVisibility.UNLISTED
        assert project.featured is True
        assert project.view_count == 100
        assert project.like_count == 50


@pytest.mark.unit
class TestNoteModel:
    """노트 모델 단위 테스트"""

    def test_note_creation(self):
        """노트 모델 객체 생성 테스트"""
        note = Note(
            project_id=1,  # 테스트용 고정 ID
            type=NoteType.LEARN,
            title="Test Note",
            content={"content": "Test content", "sections": []},
            tags=["learning", "test"],
            is_pinned=True,
            is_archived=False,
        )

        # 모델 객체 속성 검증
        assert note.project_id == 1
        assert note.type == NoteType.LEARN
        assert note.title == "Test Note"
        assert note.content["content"] == "Test content"
        assert note.tags == ["learning", "test"]
        assert note.is_pinned is True
        assert note.is_archived is False

    def test_note_with_explicit_values(self):
        """노트 명시적 값 설정 테스트"""
        note = Note(
            project_id=1,
            type=NoteType.RESEARCH,
            title="Research Note",
            content={"content": "Research content"},
            tags=["research", "analysis"],
            is_pinned=True,
            is_archived=True,
        )

        # 명시적으로 설정한 값 검증
        assert note.type == NoteType.RESEARCH
        assert note.tags == ["research", "analysis"]
        assert note.is_pinned is True
        assert note.is_archived is True


@pytest.mark.unit
class TestMediaModel:
    """미디어 모델 단위 테스트"""

    def test_media_creation(self):
        """미디어 모델 객체 생성 테스트"""
        media = Media(
            target_type=MediaTargetType.PROJECT,
            target_id=1,  # 테스트용 고정 ID
            type=MediaType.IMAGE,
            original_name="original.jpg",
            file_name="test-image.jpg",
            file_path="/media/test-image.jpg",
            file_size=1024,
            mime_type="image/jpeg",
            width=800,
            height=600,
        )

        # 모델 객체 속성 검증
        assert media.target_type == MediaTargetType.PROJECT
        assert media.target_id == 1
        assert media.type == MediaType.IMAGE
        assert media.file_name == "test-image.jpg"
        assert media.original_name == "original.jpg"
        assert media.file_size == 1024
        assert media.width == 800
        assert media.height == 600

    def test_media_properties(self):
        """미디어 모델 프로퍼티 테스트"""
        media = Media(
            target_type=MediaTargetType.PROJECT,
            target_id=1,
            type=MediaType.IMAGE,
            original_name="test-image.jpg",
            file_name="processed-image.jpg",
            file_path="/media/processed-image.jpg",
            file_size=1048576,  # 1MB
            mime_type="image/jpeg",
        )

        # 프로퍼티 검증
        assert media.file_extension == "jpg"
        assert media.is_image is True
        assert media.is_video is False
        assert media.file_size_mb == 1.0

    def test_media_with_explicit_values(self):
        """미디어 명시적 값 설정 테스트"""
        media = Media(
            target_type=MediaTargetType.NOTE,
            target_id=1,
            type=MediaType.VIDEO,
            original_name="video.mp4",
            file_name="processed-video.mp4",
            file_path="/media/processed-video.mp4",
            file_size=10485760,  # 10MB
            mime_type="video/mp4",
            width=1920,
            height=1080,
            duration=120,  # 2분
            is_public=True,
            alt_text="Test video description",
        )

        # 명시적으로 설정한 값 검증
        assert media.target_type == MediaTargetType.NOTE
        assert media.type == MediaType.VIDEO
        assert media.width == 1920
        assert media.height == 1080
        assert media.duration == 120
        assert media.is_public is True
        assert media.alt_text == "Test video description"


@pytest.mark.unit
class TestModelMethods:
    """모델 메서드 테스트"""

    def test_project_properties(self):
        """프로젝트 모델 프로퍼티 테스트"""
        # 공개 프로젝트
        public_project = Project(
            owner_id=1,
            slug="public-project",
            title="Public Project",
            visibility=ProjectVisibility.PUBLIC,
        )
        assert public_project.is_public is True

        # 비공개 프로젝트
        private_project = Project(
            owner_id=1,
            slug="private-project",
            title="Private Project",
            visibility=ProjectVisibility.PRIVATE,
        )
        assert private_project.is_public is False

    def test_note_type_properties(self):
        """노트 타입 프로퍼티 테스트"""
        learn_note = Note(
            project_id=1,
            type=NoteType.LEARN,
            title="Learn Note",
            content={"content": "Learning content"},
        )
        assert learn_note.is_learn_note is True
        assert learn_note.is_change_note is False
        assert learn_note.is_research_note is False

        change_note = Note(
            project_id=1,
            type=NoteType.CHANGE,
            title="Change Note",
            content={"content": "Change content"},
        )
        assert change_note.is_learn_note is False
        assert change_note.is_change_note is True
        assert change_note.is_research_note is False
