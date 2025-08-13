"""
보안 관련 유틸리티 함수들
JWT 토큰, 패스워드 해싱 등
"""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings

# 패스워드 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰 생성
    
    Args:
        subject: 토큰 주제 (보통 사용자 ID)
        expires_delta: 만료 시간 (기본값: 30분)
    
    Returns:
        JWT 토큰 문자열
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    리프레시 토큰 생성
    
    Args:
        subject: 토큰 주제 (보통 사용자 ID)
        expires_delta: 만료 시간 (기본값: 7일)
    
    Returns:
        JWT 토큰 문자열
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    토큰 검증 및 주제 추출
    
    Args:
        token: JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")
    
    Returns:
        사용자 ID 또는 None
    
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
            )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload invalid",
            )
        
        return user_id
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation error",
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 패스워드와 해시된 패스워드 비교
    
    Args:
        plain_password: 평문 패스워드
        hashed_password: 해시된 패스워드
    
    Returns:
        패스워드 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    패스워드 해싱
    
    Args:
        password: 평문 패스워드
    
    Returns:
        해시된 패스워드
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    패스워드 리셋 토큰 생성
    
    Args:
        email: 사용자 이메일
    
    Returns:
        리셋 토큰
    """
    delta = timedelta(hours=24)  # 24시간 유효
    now = datetime.utcnow()
    expire = now + delta
    
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset",
        "nbf": now,  # Not before
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    패스워드 리셋 토큰 검증
    
    Args:
        token: 리셋 토큰
    
    Returns:
        이메일 주소 또는 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
            
        email: str = payload.get("sub")
        return email
    
    except JWTError:
        return None