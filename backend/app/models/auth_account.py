from sqlalchemy import String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User


class AuthAccount(Base, TimestampMixin):
    """
    소셜 로그인 연동 정보
    CLAUDE.md 명세: (id, userId, provider, provider_account_id, tokens)
    """

    __tablename__ = "auth_accounts"
    __table_args__ = (
        UniqueConstraint('provider', 'provider_account_id', name='uq_provider_account'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 제공자 정보
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'github', 'google'
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 토큰 정보
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    token_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # 관계 설정
    user: Mapped["User"] = relationship("User", back_populates="auth_accounts")

    def __repr__(self):
        return f"<AuthAccount(id={self.id}, provider={self.provider}, user_id={self.user_id})>"

