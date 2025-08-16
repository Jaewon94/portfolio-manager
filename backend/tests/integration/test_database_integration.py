"""
데이터베이스 통합 테스트
실제 데이터베이스를 사용한 모델 관계 및 CRUD 테스트
"""

import pytest
from app.models.media import Media, MediaTargetType, MediaType
from app.models.note import Note, NoteType
from app.models.project import Project, ProjectStatus, ProjectVisibility
from app.models.user import User, UserRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestDatabaseIntegration:
    """데이터베이스 통합 테스트"""

    @pytest.mark.asyncio
    async def test_user_project_relationship(self, test_db: AsyncSession):
        """사용자-프로젝트 관계 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
            role=UserRole.USER,
            is_verified=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 프로젝트 생성
        project = Project(
            owner_id=user.id,
            slug="test-project",
            title="Test Project",
            description="Test description",
            status=ProjectStatus.ACTIVE,
            visibility=ProjectVisibility.PUBLIC,
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # 관계 검증
        assert project.owner_id == user.id

        # 사용자의 프로젝트 조회
        result = await test_db.execute(
            select(Project).where(Project.owner_id == user.id)
        )
        user_projects = result.scalars().all()
        assert len(user_projects) == 1
        assert user_projects[0].id == project.id

    @pytest.mark.asyncio
    async def test_project_note_relationship(self, test_db: AsyncSession):
        """프로젝트-노트 관계 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 프로젝트 생성
        project = Project(
            owner_id=user.id,
            slug="test-project",
            title="Test Project",
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # 노트 생성
        note = Note(
            project_id=project.id,
            type=NoteType.LEARN,
            title="Test Note",
            content={"content": "Test content"},
        )
        test_db.add(note)
        await test_db.commit()
        await test_db.refresh(note)

        # 관계 검증
        assert note.project_id == project.id

        # 프로젝트의 노트 조회
        result = await test_db.execute(
            select(Note).where(Note.project_id == project.id)
        )
        project_notes = result.scalars().all()
        assert len(project_notes) == 1
        assert project_notes[0].id == note.id

    @pytest.mark.asyncio
    async def test_media_project_relationship(self, test_db: AsyncSession):
        """미디어-프로젝트 관계 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 프로젝트 생성
        project = Project(
            owner_id=user.id,
            slug="test-project",
            title="Test Project",
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # 미디어 생성
        media = Media(
            target_type=MediaTargetType.PROJECT,
            target_id=project.id,
            type=MediaType.IMAGE,
            original_name="test.jpg",
            file_name="processed_test.jpg",
            file_path="/media/processed_test.jpg",
            file_size=1024,
            mime_type="image/jpeg",
        )
        test_db.add(media)
        await test_db.commit()
        await test_db.refresh(media)

        # 관계 검증
        assert media.target_type == MediaTargetType.PROJECT
        assert media.target_id == project.id

        # 프로젝트의 미디어 조회
        result = await test_db.execute(
            select(Media).where(
                Media.target_type == MediaTargetType.PROJECT,
                Media.target_id == project.id,
            )
        )
        project_media = result.scalars().all()
        assert len(project_media) == 1
        assert project_media[0].id == media.id

    @pytest.mark.asyncio
    async def test_cascade_delete(self, test_db: AsyncSession):
        """연관 삭제 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 프로젝트 생성
        project = Project(
            owner_id=user.id,
            slug="test-project",
            title="Test Project",
        )
        test_db.add(project)
        await test_db.commit()
        await test_db.refresh(project)

        # 노트 생성
        note = Note(
            project_id=project.id,
            type=NoteType.LEARN,
            title="Test Note",
            content={"content": "Test content"},
        )
        test_db.add(note)
        await test_db.commit()
        await test_db.refresh(note)

        # 프로젝트 삭제
        await test_db.delete(project)
        await test_db.commit()

        # 연관된 노트도 삭제되었는지 확인
        result = await test_db.execute(
            select(Note).where(Note.project_id == project.id)
        )
        remaining_notes = result.scalars().all()
        assert len(remaining_notes) == 0

    @pytest.mark.asyncio
    async def test_unique_constraints(self, test_db: AsyncSession):
        """유니크 제약 조건 테스트"""
        # 사용자 생성
        user = User(
            email="test@example.com",
            name="Test User",
            github_username="testuser",
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # 첫 번째 프로젝트 생성
        project1 = Project(
            owner_id=user.id,
            slug="unique-slug",
            title="First Project",
        )
        test_db.add(project1)
        await test_db.commit()

        # 같은 슬러그로 두 번째 프로젝트 생성 시도
        project2 = Project(
            owner_id=user.id,
            slug="unique-slug",
            title="Second Project",
        )
        test_db.add(project2)

        # 유니크 제약 조건 위반으로 예외 발생해야 함
        with pytest.raises(Exception):  # IntegrityError 예상
            await test_db.commit()
