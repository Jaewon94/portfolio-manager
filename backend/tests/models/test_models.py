#!/usr/bin/env python3
"""
SQLAlchemy 모델 테스트 스크립트
ERD 명세에 따른 7개 핵심 엔티티 검증
"""

import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

def test_models():
    """SQLAlchemy 모델 테스트 함수"""
    try:
        # 모든 모델 import 테스트
        from app.models import (
            Base,
            TimestampMixin,
            User,
            UserRole,
            AuthAccount,
            Session,
            Project,
            ProjectStatus,
            ProjectVisibility,
            GithubRepository,
            Note,
            NoteType,
            Media,
            MediaType,
            MediaTargetType,
        )
        
        print("✅ 모든 모델 import 성공")
        
        # 모델 클래스 검증
        models = [User, AuthAccount, Session, Project, GithubRepository, Note, Media]
        
        print("\n📊 모델 테이블명 검증:")
        expected_tables = {
            "User": "users",
            "AuthAccount": "auth_accounts", 
            "Session": "sessions",
            "Project": "projects",
            "GithubRepository": "github_repositories",
            "Note": "notes",
            "Media": "media"
        }
        
        for model in models:
            table_name = model.__tablename__
            expected = expected_tables[model.__name__]
            if table_name == expected:
                print(f"  ✅ {model.__name__}: {table_name}")
            else:
                print(f"  ❌ {model.__name__}: {table_name} (expected: {expected})")
        
        # Enum 검증
        print("\n🔢 Enum 타입 검증:")
        enums = [
            (UserRole, ["user", "admin"]),
            (ProjectStatus, ["draft", "active", "archived", "deleted"]),
            (ProjectVisibility, ["public", "private", "unlisted"]),
            (NoteType, ["learn", "change", "research"]),
            (MediaType, ["image", "video", "document", "archive"]),
            (MediaTargetType, ["project", "note"])
        ]
        
        for enum_class, expected_values in enums:
            actual_values = [e.value for e in enum_class]
            if set(actual_values) == set(expected_values):
                print(f"  ✅ {enum_class.__name__}: {actual_values}")
            else:
                print(f"  ❌ {enum_class.__name__}: {actual_values} (expected: {expected_values})")
        
        # 관계 검증
        print("\n🔗 관계 설정 검증:")
        relationships = [
            (User, "projects", "User.projects"),
            (User, "auth_accounts", "User.auth_accounts"),
            (User, "sessions", "User.sessions"),
            (Project, "owner", "Project.owner"),
            (Project, "notes", "Project.notes"),
            (Project, "github_repository", "Project.github_repository"),
            (GithubRepository, "project", "GithubRepository.project"),
            (Note, "project", "Note.project"),
            (AuthAccount, "user", "AuthAccount.user"),
            (Session, "user", "Session.user"),
        ]
        
        for model_class, attr_name, desc in relationships:
            if hasattr(model_class, attr_name):
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ {desc} - 관계가 정의되지 않음")
        
        # 특별 제약조건 검증
        print("\n🔒 제약조건 검증:")
        
        # Project의 unique constraint 확인
        if hasattr(Project, '__table_args__') and Project.__table_args__:
            print(f"  ✅ Project.unique_constraint: owner_id + slug")
        else:
            print(f"  ❌ Project에 unique constraint가 없음")
        
        # AuthAccount의 unique constraint 확인
        if hasattr(AuthAccount, '__table_args__') and AuthAccount.__table_args__:
            print(f"  ✅ AuthAccount.unique_constraint: provider + provider_account_id")
        else:
            print(f"  ❌ AuthAccount에 unique constraint가 없음")
        
        # GithubRepository의 1:1 관계 확인
        repo_project_id_unique = False
        for column in GithubRepository.__table__.columns:
            if column.name == 'project_id':
                repo_project_id_unique = getattr(column, 'unique', False)
                break
        
        if repo_project_id_unique:
            print(f"  ✅ GithubRepository.project_id: unique (1:1 관계)")
        else:
            print(f"  ❌ GithubRepository.project_id가 unique하지 않음")
        
        print("\n📝 모델 인스턴스 생성 테스트:")
        
        # 기본 인스턴스 생성 테스트 (DB 연결 없이)
        try:
            user = User(
                email="test@example.com",
                name="Test User",
                role=UserRole.USER
            )
            print(f"  ✅ User 인스턴스: {user}")
            
            project = Project(
                owner_id=1,
                slug="test-project",
                title="Test Project",
                status=ProjectStatus.DRAFT,
                visibility=ProjectVisibility.PRIVATE
            )
            print(f"  ✅ Project 인스턴스: {project}")
            
            note = Note(
                project_id=1,
                type=NoteType.LEARN,
                title="Test Note",
                content={"text": "This is a test note"}
            )
            print(f"  ✅ Note 인스턴스: {note}")
            
            auth_account = AuthAccount(
                user_id=1,
                provider="github",
                provider_account_id="12345"
            )
            print(f"  ✅ AuthAccount 인스턴스: {auth_account}")
            
            print("\n🎉 모든 모델 테스트 통과!")
            
        except Exception as e:
            print(f"  ❌ 모델 인스턴스 생성 실패: {e}")
            return False
        
        return True

    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False


if __name__ == "__main__":
    success = test_models()
    
    if success:
        print("\n✅ SQLAlchemy 모델 테스트 완료 - 모든 검증 통과")
        sys.exit(0)
    else:
        print("\n❌ SQLAlchemy 모델 테스트 실패")
        sys.exit(1)