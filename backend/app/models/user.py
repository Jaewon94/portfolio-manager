import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .auth_account import AuthAccount
    from .project import Project
    from .session import Session


class UserRole(enum.Enum):
    """사용자 역할"""

    USER = "user"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """
    전역 사용자 모델
    CLAUDE.md 명세: (id, email, name, bio, github_username, role, is_verified)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )  # 사용자명/닉네임
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 실제 이름
    hashed_password: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # 해시된 비밀번호

    # ERD 추가 필드들
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 사용자 상태
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    # 관계 설정
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")
    auth_accounts: Mapped[list["AuthAccount"]] = relationship(
        "AuthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"
