"""
인증 관련 Pydantic 스키마
토큰, 사용자 정보, 로그인 요청/응답 모델
"""

from datetime import datetime
from typing import Optional

from app.models.user import UserRole
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """로그인 요청 (개발/테스트용)"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Refresh token 요청"""

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """사용자 정보 응답"""

    id: int
    email: str
    name: str
    bio: Optional[str] = None
    github_username: Optional[str] = None
    role: UserRole
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy 모델과 호환


class TokenResponse(BaseModel):
    """토큰 발급 응답"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class OAuthUserInfo(BaseModel):
    """OAuth 제공자에서 받은 사용자 정보"""

    provider_user_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    github_username: Optional[str] = None


class SessionInfo(BaseModel):
    """세션 정보"""

    id: str
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# 기존 스키마 (하위 호환성)
class Token(BaseModel):
    """토큰 응답 스키마 (기존 호환용)"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """토큰 페이로드 스키마 (내부 사용)"""

    sub: int
    type: str
