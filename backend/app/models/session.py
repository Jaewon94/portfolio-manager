from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .user import User


class Session(Base, TimestampMixin):
    """
    세션 관리 모델
    CLAUDE.md 명세: (id, userId, session_token, expires, ip_address, user_agent)
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 세션 정보
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # 클라이언트 정보
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 지원
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 세션 활동 정보
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=datetime.utcnow
    )

    # 관계 설정
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, expires={self.expires})>"

    def is_expired(self) -> bool:
        """세션이 만료되었는지 확인"""
        return datetime.utcnow() > self.expires