#!/bin/bash

# PostgreSQL 테스트 환경 설정 스크립트

echo "🔧 PostgreSQL 테스트 환경 설정 중..."

# 1. 테스트용 PostgreSQL 컨테이너 시작
echo "📦 테스트용 PostgreSQL 컨테이너 시작..."
cd /Users/jaewon/portfolio/portfolio-manager
docker-compose --profile test up -d postgres-test

# 2. PostgreSQL 연결 대기
echo "⏳ PostgreSQL 연결 대기 중..."
until docker-compose exec postgres-test pg_isready -U postgres; do
  echo "PostgreSQL 시작 대기..."
  sleep 2
done

echo "✅ PostgreSQL 테스트 환경 준비 완료!"
echo "📍 테스트 DB URL: postgresql+asyncpg://postgres:postgres@localhost:5433/portfolio_manager_test"

# 3. 테스트 실행 (선택적)
if [ "$1" = "--run-tests" ]; then
    echo "🧪 테스트 실행 중..."
    cd backend
    python -m pytest tests/ -v
fi

echo ""
echo "💡 테스트 실행 방법:"
echo "   cd backend"
echo "   python -m pytest tests/ -v"
echo ""
echo "🛑 테스트 완료 후 정리:"
echo "   docker-compose --profile test down"