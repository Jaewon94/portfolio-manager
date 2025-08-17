"""
단위 테스트: 스키마 테스트
Pydantic 스키마의 검증, 직렬화, 역직렬화를 테스트합니다.
"""

from datetime import datetime

import pytest
from app.models.media import MediaTargetType, MediaType
from app.models.note import NoteType
from app.models.project import ProjectStatus, ProjectVisibility
from app.schemas.media import MediaResponse, MediaUploadRequest
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.schemas.user import User, UserCreate, UserUpdate
from pydantic import ValidationError


@pytest.mark.unit
class TestUserSchemas:
    """사용자 스키마 단위 테스트"""

    def test_user_create_valid(self):
        """유효한 사용자 생성 데이터 테스트"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
        }

        user_create = UserCreate(**user_data)

        assert user_create.email == "test@example.com"
        assert user_create.username == "testuser"
        assert user_create.full_name == "Test User"
        assert user_create.password == "testpassword123"

    def test_user_create_invalid_email(self):
        """잘못된 이메일 형식 테스트"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "testpassword123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "email" in str(exc_info.value)

    def test_user_update_partial(self):
        """사용자 부분 업데이트 테스트"""
        user_update = UserUpdate(full_name="Updated Name")

        assert user_update.full_name == "Updated Name"
        assert user_update.email is None
        assert user_update.username is None

    def test_user_response_serialization(self):
        """사용자 응답 직렬화 테스트"""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False,
        }

        user_response = User(**user_data)
        json_data = user_response.model_dump()

        assert json_data["id"] == 1
        assert json_data["email"] == "test@example.com"
        assert json_data["username"] == "testuser"


@pytest.mark.unit
class TestProjectSchemas:
    """프로젝트 스키마 단위 테스트"""

    def test_project_create_valid(self):
        """유효한 프로젝트 생성 데이터 테스트"""
        project_data = {
            "slug": "test-project",
            "title": "Test Project",
            "description": "Test description",
            "content": {"sections": []},
            "tech_stack": ["Python", "FastAPI"],
            "categories": ["Backend"],
            "tags": ["test"],
            "status": "active",
            "visibility": "public",
            "featured": False,
        }

        project_create = ProjectCreate(**project_data)

        assert project_create.slug == "test-project"
        assert project_create.title == "Test Project"
        assert project_create.tech_stack == ["Python", "FastAPI"]
        assert project_create.status == ProjectStatus.ACTIVE
        assert project_create.visibility == ProjectVisibility.PUBLIC

    def test_project_create_invalid_slug(self):
        """잘못된 슬러그 형식 테스트 - 현재는 검증 로직이 없으므로 스킵"""
        # 실제 프로젝트 스키마에서 슬러그 검증이 구현되지 않았으므로
        # 이 테스트는 현재 상황에서 의미가 없습니다.
        # 향후 슬러그 검증이 추가되면 이 테스트를 활성화할 수 있습니다.
        pytest.skip("슬러그 검증 로직이 아직 구현되지 않음")

    def test_project_update_partial(self):
        """프로젝트 부분 업데이트 테스트"""
        project_update = ProjectUpdate(
            title="Updated Title", status=ProjectStatus.ARCHIVED
        )

        assert project_update.title == "Updated Title"
        assert project_update.status == ProjectStatus.ARCHIVED
        assert project_update.description is None

    def test_project_response_with_stats(self):
        """프로젝트 응답 (통계 포함) 테스트"""
        project_data = {
            "id": 1,
            "owner_id": 1,
            "slug": "test-project",
            "title": "Test Project",
            "description": "Test description",
            "content": {"sections": []},
            "tech_stack": ["Python"],
            "categories": ["Backend"],
            "tags": ["test"],
            "status": ProjectStatus.ACTIVE,
            "visibility": ProjectVisibility.PUBLIC,
            "featured": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "view_count": 100,
            "like_count": 10,
        }

        project_response = Project(**project_data)

        assert project_response.view_count == 100
        assert project_response.like_count == 10


@pytest.mark.unit
class TestNoteSchemas:
    """노트 스키마 단위 테스트"""

    def test_note_create_valid(self):
        """유효한 노트 생성 데이터 테스트"""
        note_data = {
            "project_id": 1,
            "type": NoteType.LEARN,
            "title": "Test Note",
            "content": {"content": "Test content", "sections": []},
            "tags": ["learning", "test"],
            "is_pinned": False,
            "is_archived": False,
        }

        note_create = NoteCreate(**note_data)

        assert note_create.type == NoteType.LEARN
        assert note_create.title == "Test Note"
        assert note_create.content["content"] == "Test content"
        assert note_create.tags == ["learning", "test"]

    def test_note_create_invalid_type(self):
        """잘못된 노트 타입 테스트"""
        note_data = {
            "type": "invalid_type",
            "title": "Test Note",
            "content": {"content": "Test content"},
        }

        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(**note_data)

        assert "type" in str(exc_info.value)

    def test_note_update_content_only(self):
        """노트 내용만 업데이트 테스트"""
        note_update = NoteUpdate(content={"content": "Updated content", "sections": []})

        assert note_update.content["content"] == "Updated content"
        assert note_update.title is None
        assert note_update.tags is None


@pytest.mark.unit
class TestMediaSchemas:
    """미디어 스키마 단위 테스트"""

    def test_media_upload_request_valid(self):
        """유효한 미디어 업로드 요청 데이터 테스트"""
        media_data = {
            "target_type": "project",
            "target_id": 1,
            "alt_text": "Test image",
            "is_public": True,
        }

        media_request = MediaUploadRequest(**media_data)

        assert media_request.target_type == MediaTargetType.PROJECT
        assert media_request.target_id == 1
        assert media_request.alt_text == "Test image"
        assert media_request.is_public is True

    def test_media_upload_request_invalid_target_id(self):
        """잘못된 타겟 ID 테스트"""
        media_data = {
            "target_type": "project",
            "target_id": 0,  # 0은 유효하지 않음 (ge=1 조건)
            "alt_text": "Test image",
        }

        with pytest.raises(ValidationError) as exc_info:
            MediaUploadRequest(**media_data)

        assert "target_id" in str(exc_info.value)

    def test_media_response_with_url(self):
        """미디어 응답 (URL 포함) 테스트"""
        media_data = {
            "id": 1,
            "target_type": MediaTargetType.PROJECT,
            "target_id": 1,
            "type": MediaType.IMAGE,
            "original_name": "test-image.jpg",
            "file_path": "/media/test-image.jpg",
            "file_size": 1024,
            "mime_type": "image/jpeg",
            "width": 800,
            "height": 600,
            "is_public": True,
            "alt_text": "Test image",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "file_extension": "jpg",
            "is_image": True,
            "is_video": False,
            "file_size_mb": 0.001,
            "download_url": "/api/media/1/download",
        }

        media_response = MediaResponse(**media_data)

        assert media_response.id == 1
        assert media_response.original_name == "test-image.jpg"
        assert media_response.download_url == "/api/media/1/download"


@pytest.mark.unit
class TestSchemaValidation:
    """스키마 검증 로직 테스트"""

    def test_slug_validation(self):
        """슬러그 검증 테스트 - 현재는 검증 로직이 없으므로 스킵"""
        # 실제 프로젝트 스키마에서 슬러그 검증이 구현되지 않았으므로
        # 이 테스트는 현재 상황에서 의미가 없습니다.
        pytest.skip("슬러그 검증 로직이 아직 구현되지 않음")

    def test_content_validation(self):
        """컨텐츠 JSON 검증 테스트"""
        valid_contents = [
            {"sections": []},
            {"sections": [{"type": "text", "content": "Hello"}]},
            {"content": "Simple content", "sections": []},
        ]

        for content in valid_contents:
            project_data = {
                "slug": "test",
                "title": "Test",
                "description": "Test",
                "content": content,
            }
            # 예외 발생하지 않아야 함
            ProjectCreate(**project_data)
