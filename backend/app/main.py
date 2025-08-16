"""
FastAPI 메인 애플리케이션
Portfolio Manager API 서버
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api import api_router

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Portfolio Manager API - 포트폴리오 통합 관리 시스템",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level=settings.LOG_LEVEL.lower()
    )