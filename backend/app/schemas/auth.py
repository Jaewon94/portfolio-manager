from pydantic import BaseModel

class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """토큰 페이로드 스키마"""
    sub: str
    type: str

class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    username: str  # email 또는 username 둘 다 가능
    password: str