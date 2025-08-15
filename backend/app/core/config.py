from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    애플리케이션 설정

    Pydantic Settings는 자동으로 환경변수와 .env 파일에서 값을 읽어옵니다.
    우선순위: 환경변수 > .env 파일 > 아래 기본값

    예시: PROJECT_NAME 필드는 환경변수 PROJECT_NAME 또는 .env의 PROJECT_NAME= 값을 자동 매핑
    """

    # API 설정 (.env 파일에서 자동 로드)
    PROJECT_NAME: str = "Portfolio Manager API"  # 폴백 기본값
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS 설정 (.env의 ALLOWED_HOSTS 값으로 자동 치환)
    ALLOWED_HOSTS: str = "http://localhost:3000,http://localhost:8000"

    # 데이터베이스 설정 (.env의 DATABASE_URL 값으로 자동 치환)
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/portfolio_manager"
    )

    # JWT 설정 (.env의 SECRET_KEY 등으로 자동 치환)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis 설정 (.env의 REDIS_URL 값으로 자동 치환)
    REDIS_URL: str = "redis://localhost:6379"

    # 환경 설정 (.env의 ENVIRONMENT, LOG_LEVEL 값으로 자동 치환)
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_hosts_list(self) -> List[str]:
        """CORS용 호스트 리스트 반환"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    class Config:
        # 환경에 따른 .env 파일 선택
        env_file = (
            ".env.dev"
            if os.getenv("ENVIRONMENT", "development") == "development"
            else ".env.prod"
        )
        env_file_encoding = "utf-8"


settings = Settings()
