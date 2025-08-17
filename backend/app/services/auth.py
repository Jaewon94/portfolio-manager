"""
인증 서비스
OAuth 로그인, 사용자 관리, 세션 관리
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_token
from app.models.auth_account import AuthAccount
from app.models.session import Session as UserSession
from app.models.user import User, UserRole
from app.schemas.auth import OAuthUserInfo
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer(auto_error=False)


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_oauth_user_info(
        self, provider: str, oauth_code: str
    ) -> OAuthUserInfo:
        """
        OAuth 제공자에서 사용자 정보 가져오기

        Args:
            provider: 'github', 'google', 또는 'kakao'
            oauth_code: OAuth authorization code

        Returns:
            OAuthUserInfo: 사용자 정보
        """
        if provider == "github":
            return await self._get_github_user_info(oauth_code)
        elif provider == "google":
            return await self._get_google_user_info(oauth_code)
        elif provider == "kakao":
            return await self._get_kakao_user_info(oauth_code)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OAuth provider",
            )

    async def _get_github_user_info(self, oauth_code: str) -> OAuthUserInfo:
        """GitHub OAuth 사용자 정보 조회 (GitHub API v3/v4)"""
        async with httpx.AsyncClient() as client:
            # 1. Access token 요청
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": oauth_code,
                    "scope": "user:email",  # 이메일 접근 권한 명시적 요청
                },
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth token exchange failed: {token_response.text}",
                )

            token_data = await token_response.json()

            if "access_token" not in token_data:
                error_description = token_data.get("error_description", "Unknown error")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth token exchange failed: {error_description}",
                )

            access_token = token_data["access_token"]
            token_type = token_data.get("token_type", "token")

            # GitHub API 헤더 (User-Agent 필수)
            api_headers = {
                "Authorization": f"{token_type} {access_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Portfolio-Manager/1.0",
            }

            # 2. 사용자 정보 조회
            user_response = await client.get(
                "https://api.github.com/user", headers=api_headers
            )

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub user info retrieval failed: {user_response.text}",
                )

            user_data = await user_response.json()

            # 3. 이메일 정보 조회 (별도 API 호출 필요)
            email_response = await client.get(
                "https://api.github.com/user/emails", headers=api_headers
            )

            if email_response.status_code != 200:
                # 이메일 API 접근 실패 시 public 이메일 사용
                primary_email = user_data.get("email")
                if not primary_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="GitHub user email access denied or unavailable",
                    )
            else:
                emails_data = await email_response.json()

                # Primary이고 verified된 이메일 우선 선택
                primary_email = None
                verified_email = None

                for email_info in emails_data:
                    if email_info.get("primary", False) and email_info.get(
                        "verified", False
                    ):
                        primary_email = email_info["email"]
                        break
                    elif email_info.get("verified", False):
                        verified_email = email_info["email"]

                # 우선순위: Primary+Verified > Verified > Primary > 첫 번째
                if primary_email:
                    email = primary_email
                elif verified_email:
                    email = verified_email
                elif emails_data and emails_data[0].get("email"):
                    email = emails_data[0]["email"]
                else:
                    # 마지막 폴백: public email
                    email = user_data.get("email")

                if not email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="GitHub user email not found or not accessible",
                    )

                primary_email = email

            return OAuthUserInfo(
                provider_user_id=str(user_data["id"]),
                email=primary_email,
                name=user_data.get("name") or user_data.get("login"),
                avatar_url=user_data.get("avatar_url"),
                github_username=user_data.get("login"),
            )

    async def _get_google_user_info(self, oauth_code: str) -> OAuthUserInfo:
        """Google OAuth 사용자 정보 조회 (Google People API v1 사용)"""
        async with httpx.AsyncClient() as client:
            # 1. Access token 요청
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": oauth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google OAuth token exchange failed: {token_response.text}",
                )

            token_data = await token_response.json()

            if "access_token" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google OAuth token exchange failed - no access token",
                )

            access_token = token_data["access_token"]

            # 2. 사용자 정보 조회 (Google People API v1 - 더 정확한 정보 제공)
            user_response = await client.get(
                "https://people.googleapis.com/v1/people/me",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"personFields": "names,emailAddresses,photos"},
            )

            if user_response.status_code != 200:
                # 폴백: userinfo v2 API 사용
                user_response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Google user info retrieval failed",
                    )

                user_data = await user_response.json()
                return OAuthUserInfo(
                    provider_user_id=user_data["id"],
                    email=user_data["email"],
                    name=user_data.get("name", user_data["email"].split("@")[0]),
                    avatar_url=user_data.get("picture"),
                )

            # People API 응답 파싱
            user_data = await user_response.json()

            # 이름 추출 (우선순위: displayName > givenName familyName)
            name = None
            if "names" in user_data and user_data["names"]:
                primary_name = next(
                    (
                        n
                        for n in user_data["names"]
                        if n.get("metadata", {}).get("primary")
                    ),
                    user_data["names"][0],
                )
                name = primary_name.get("displayName")
                if not name:
                    given_name = primary_name.get("givenName", "")
                    family_name = primary_name.get("familyName", "")
                    name = f"{given_name} {family_name}".strip()

            # 이메일 추출
            email = None
            if "emailAddresses" in user_data and user_data["emailAddresses"]:
                primary_email = next(
                    (
                        e
                        for e in user_data["emailAddresses"]
                        if e.get("metadata", {}).get("primary")
                    ),
                    user_data["emailAddresses"][0],
                )
                email = primary_email.get("value")

            # 프로필 사진 추출
            avatar_url = None
            if "photos" in user_data and user_data["photos"]:
                primary_photo = next(
                    (
                        p
                        for p in user_data["photos"]
                        if p.get("metadata", {}).get("primary")
                    ),
                    user_data["photos"][0],
                )
                avatar_url = primary_photo.get("url")

            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google user email not found",
                )

            # 사용자 ID는 resourceName에서 추출 (예: people/123456789)
            resource_name = user_data.get("resourceName", "")
            user_id = (
                resource_name.replace("people/", "")
                if resource_name
                else email.split("@")[0]
            )

            return OAuthUserInfo(
                provider_user_id=user_id,
                email=email,
                name=name or email.split("@")[0],
                avatar_url=avatar_url,
            )

    async def _get_kakao_user_info(self, oauth_code: str) -> OAuthUserInfo:
        """카카오 OAuth 사용자 정보 조회"""
        async with httpx.AsyncClient() as client:
            # 1. Access token 요청
            token_response = await client.post(
                "https://kauth.kakao.com/oauth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.KAKAO_CLIENT_ID,
                    "client_secret": settings.KAKAO_CLIENT_SECRET,
                    "redirect_uri": settings.KAKAO_REDIRECT_URI,
                    "code": oauth_code,
                },
            )
            token_data = await token_response.json()

            if "access_token" not in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Kakao OAuth token exchange failed",
                )

            access_token = token_data["access_token"]

            # 2. 사용자 정보 조회
            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_data = await user_response.json()

            # 카카오 사용자 정보 파싱
            kakao_account = user_data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})

            # 이메일은 선택적 동의 항목이라 없을 수 있음
            email = kakao_account.get("email")
            if not email:
                # 이메일 없이는 회원가입 불가 - 임시 이메일 생성
                user_id = str(user_data["id"])
                email = f"kakao_{user_id}@kakao.local"

            # 닉네임 우선, 없으면 이메일에서 추출
            name = profile.get("nickname")
            if not name:
                name = (
                    email.split("@")[0] if "@" in email else f"kakao_{user_data['id']}"
                )

            return OAuthUserInfo(
                provider_user_id=str(user_data["id"]),
                email=email,
                name=name,
                avatar_url=profile.get("profile_image_url"),
            )

    async def create_or_update_oauth_user(
        self, provider: str, user_info: OAuthUserInfo
    ) -> User:
        """
        OAuth 사용자 생성 또는 업데이트

        Args:
            provider: OAuth 제공자
            user_info: OAuth에서 받은 사용자 정보

        Returns:
            User: 생성되거나 업데이트된 사용자
        """
        # 1. 기존 OAuth 계정 확인
        stmt = select(AuthAccount).where(
            AuthAccount.provider == provider,
            AuthAccount.provider_account_id == user_info.provider_user_id,
        )
        result = await self.db.execute(stmt)
        auth_account = result.scalar_one_or_none()

        if auth_account:
            # 기존 사용자 업데이트
            user_stmt = select(User).where(User.id == auth_account.user_id)
            user_result = await self.db.execute(user_stmt)
            user = user_result.scalar_one()

            # 사용자 정보 업데이트 (이름, GitHub 사용자명 등)
            user.name = user_info.name
            if user_info.github_username:
                user.github_username = user_info.github_username
            user.updated_at = datetime.now(timezone.utc)

        else:
            # 이메일로 기존 사용자 확인
            email_stmt = select(User).where(User.email == user_info.email)
            email_result = await self.db.execute(email_stmt)
            existing_user = email_result.scalar_one_or_none()

            if existing_user:
                # 기존 사용자에 OAuth 계정 연결
                user = existing_user
                new_auth_account = AuthAccount(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    provider=provider,
                    provider_account_id=user_info.provider_user_id,
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(new_auth_account)
            else:
                # 새 사용자 생성
                user_id = str(uuid.uuid4())
                user = User(
                    id=user_id,
                    email=user_info.email,
                    name=user_info.name,
                    github_username=user_info.github_username,
                    role=UserRole.USER,
                    is_verified=True,  # OAuth 사용자는 자동 인증
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.db.add(user)

                # OAuth 계정 정보 저장
                auth_account = AuthAccount(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    provider=provider,
                    provider_account_id=user_info.provider_user_id,
                    created_at=datetime.now(timezone.utc),
                )
                self.db.add(auth_account)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_user_session(
        self, user_id: int, access_token: str, ip_address: str, user_agent: str
    ) -> UserSession:
        """
        사용자 세션 생성

        Args:
            user_id: 사용자 ID
            access_token: JWT access token
            ip_address: 클라이언트 IP
            user_agent: 클라이언트 User-Agent

        Returns:
            UserSession: 생성된 세션
        """
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_token=access_token[:32],  # 토큰 앞부분만 저장
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def invalidate_user_sessions(self, user_id: int) -> None:
        """
        사용자의 모든 세션 무효화

        Args:
            user_id: 사용자 ID
        """
        stmt = delete(UserSession).where(UserSession.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """사용자 ID로 조회"""
        try:
            # 문자열 user_id를 정수로 변환 (User 모델의 id는 integer)
            user_id_int = int(user_id)
            stmt = select(User).where(User.id == user_id_int)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except ValueError:
            # user_id가 정수로 변환할 수 없는 경우
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, name: str, password: str) -> User:
        """
        일반 사용자 생성 (회원가입용)

        Args:
            email: 이메일
            name: 이름
            password: 패스워드

        Returns:
            User: 생성된 사용자
        """
        user = User(
            email=email,
            name=name,
            username=email.split("@")[0],  # 이메일에서 username 생성
            hashed_password=get_password_hash(password),
            role=UserRole.USER,
            is_verified=True,  # 개발 중에는 자동 인증
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_test_user(self, email: str, name: str, password: str) -> User:
        """
        개발/테스트용 사용자 생성

        Args:
            email: 이메일
            name: 이름
            password: 패스워드

        Returns:
            User: 생성된 사용자
        """
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            hashed_password=get_password_hash(password),
            role=UserRole.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


async def get_current_user(
    authorization: Optional[str] = Depends(security), db: AsyncSession = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 조회 (필수)
    """
    user = await get_current_user_optional(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
        )
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Depends(security), db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    현재 인증된 사용자 조회 (선택사항)

    Args:
        authorization: HTTP Bearer 토큰 (선택사항)
        db: 데이터베이스 세션

    Returns:
        Optional[User]: 인증된 사용자 또는 None
    """
    if not authorization:
        print("DEBUG: No authorization header provided")
        return None

    try:
        # Bearer 토큰에서 실제 토큰 추출
        token = authorization.credentials
        print(f"DEBUG: Received token: {token[:50] if token else 'None'}...")

        # 토큰 검증 및 사용자 ID 추출
        user_id = verify_token(token, token_type="access")
        print(f"DEBUG: Token verified, user_id: {user_id}")

        # 사용자 조회
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        print(f"DEBUG: User found: {user.email if user else 'None'}")

        return user

    except Exception as e:
        print(f"DEBUG: Authentication error: {e}")
        # 인증 오류 시 None 반환 (오류 발생시키지 않음)
        return None
