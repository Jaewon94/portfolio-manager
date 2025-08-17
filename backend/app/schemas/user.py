from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """사용자 기본 스키마"""

    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """사용자 생성 스키마"""

    password: str


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """데이터베이스의 사용자 스키마"""

    id: int
    hashed_password: str
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """사용자 응답 스키마"""

    id: int
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)
