"""
인증 관련 API 엔드포인트
OAuth 로그인, JWT 토큰 발급/갱신, 로그아웃
"""

from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token, 
    verify_token,
    get_password_hash,
    verify_password
)
from app.models.user import User, UserRole
from app.models.auth_account import AuthAccount
from app.models.session import Session as UserSession
from app.schemas.auth import (
    TokenResponse,
    LoginRequest,
    UserResponse,
    RefreshTokenRequest
)
from app.services.auth import AuthService, get_current_user

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/login/{provider}", response_model=TokenResponse)
async def oauth_login(
    provider: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth 소셜 로그인 (GitHub, Google, Kakao)
    
    Args:
        provider: 'github', 'google', 또는 'kakao'
        request: FastAPI Request 객체
        db: 데이터베이스 세션
    
    Returns:
        TokenResponse: access_token, refresh_token, 사용자 정보
    """
    if provider not in ["github", "google", "kakao"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider. Supported: github, google, kakao"
        )
    
    # Authorization header에서 OAuth 코드 추출
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth authorization code required"
        )
    
    oauth_code = auth_header.replace("Bearer ", "")
    
    try:
        # OAuth 제공자에서 사용자 정보 가져오기
        auth_service = AuthService(db)
        user_info = await auth_service.get_oauth_user_info(provider, oauth_code)
        
        # 사용자 생성 또는 업데이트
        user = await auth_service.create_or_update_oauth_user(provider, user_info)
        
        # JWT 토큰 생성
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        # 세션 생성 (선택적 - 세션 기반 로그아웃 지원)
        await auth_service.create_user_session(
            user_id=user.id,
            access_token=access_token,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent", "")
        )
        
        # Refresh token을 HttpOnly 쿠키로 설정 (보안 강화)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax"
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                bio=user.bio,
                github_username=user.github_username,
                role=user.role,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh token으로 새로운 access token 발급
    
    Args:
        request: refresh_token 포함된 요청
        db: 데이터베이스 세션
    
    Returns:
        TokenResponse: 새로운 access_token과 기존 refresh_token
    """
    try:
        # Refresh token 검증
        user_id = verify_token(request.refresh_token, token_type="refresh")
        
        # 사용자 존재 확인
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # 새로운 access token 생성
        access_token = create_access_token(subject=user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # 기존 refresh token 유지
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                bio=user.bio,
                github_username=user.github_username,
                role=user.role,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    현재 인증된 사용자 정보 조회
    
    Args:
        current_user: 인증된 사용자 (의존성 주입)
    
    Returns:
        UserResponse: 현재 사용자 정보
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        bio=current_user.bio,
        github_username=current_user.github_username,
        role=current_user.role,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    로그아웃 - 세션 무효화 및 쿠키 제거
    
    Args:
        response: FastAPI Response 객체
        current_user: 인증된 사용자
        db: 데이터베이스 세션
    
    Returns:
        Dict: 로그아웃 성공 메시지
    """
    try:
        # 사용자의 모든 세션 무효화 (선택적)
        auth_service = AuthService(db)
        await auth_service.invalidate_user_sessions(current_user.id)
        
        # Refresh token 쿠키 제거
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax"
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/test-login", response_model=TokenResponse)
async def test_login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    개발/테스트용 이메일 로그인 (OAuth 없이 직접 로그인)
    프로덕션에서는 비활성화 권장
    
    Args:
        request: 이메일, 패스워드 포함된 요청
        db: 데이터베이스 세션
    
    Returns:
        TokenResponse: access_token, refresh_token, 사용자 정보
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test login not available in production"
        )
    
    try:
        auth_service = AuthService(db)
        
        # 사용자 조회
        user = await auth_service.get_user_by_email(request.email)
        
        if not user:
            # 테스트용 사용자 생성
            user = await auth_service.create_test_user(
                email=request.email,
                name=request.email.split("@")[0],
                password=request.password
            )
        else:
            # 패스워드 검증 (실제로는 해시된 패스워드와 비교)
            if not verify_password(request.password, user.hashed_password or ""):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
        
        # JWT 토큰 생성
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                bio=user.bio,
                github_username=user.github_username,
                role=user.role,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test login failed: {str(e)}"
        )