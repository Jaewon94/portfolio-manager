"""
애플리케이션 예외 클래스 정의
"""

from typing import Optional, Any, Dict


class BaseException(Exception):
    """기본 예외 클래스"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseException):
    """유효성 검증 실패 예외"""
    pass


class NotFoundException(BaseException):
    """리소스를 찾을 수 없는 예외"""
    pass


class DuplicateException(BaseException):
    """중복된 리소스 예외"""
    pass


class PermissionException(BaseException):
    """권한 없음 예외"""
    pass


class ExternalAPIException(BaseException):
    """외부 API 호출 실패 예외"""
    pass


class DatabaseException(BaseException):
    """데이터베이스 작업 실패 예외"""
    pass


class AuthenticationException(BaseException):
    """인증 실패 예외"""
    pass


class ConfigurationException(BaseException):
    """설정 오류 예외"""
    pass