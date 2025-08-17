"""
FastAPI 메인 애플리케이션
Portfolio Manager API 서버
"""

from app.api.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException,
    BaseException,
    ConfigurationException,
    DatabaseException,
    DuplicateException,
    ExternalAPIException,
    NotFoundException,
    PermissionException,
    ValidationException,
)
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Portfolio Manager API - 포트폴리오 통합 관리 시스템",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 예외 핸들러 등록
@app.exception_handler(BaseException)
async def base_exception_handler(request, exc: BaseException):
    """기본 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    """유효성 검증 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc: NotFoundException):
    """리소스 없음 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(DuplicateException)
async def duplicate_exception_handler(request, exc: DuplicateException):
    """중복 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(PermissionException)
async def permission_exception_handler(request, exc: PermissionException):
    """권한 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(ExternalAPIException)
async def external_api_exception_handler(request, exc: ExternalAPIException):
    """외부 API 예외 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "details": exc.details,
            },
        },
    )


# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check 엔드포인트
@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "version": settings.VERSION}


# 루트 엔드포인트
@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower(),
    )
