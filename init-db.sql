-- PostgreSQL 초기화 스크립트
-- 한국어 텍스트 검색을 위한 확장 설치

-- pg_trgm 확장 (유사도 검색, 한국어 지원)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- unaccent 확장 (악센트 제거, 다국어 지원)
CREATE EXTENSION IF NOT EXISTS unaccent;

-- PGroonga 확장 (한국어 전문 검색 지원)
CREATE EXTENSION IF NOT EXISTS pgroonga;

-- 데이터베이스 기본 설정
COMMENT ON DATABASE portfolio_manager IS 'Portfolio Manager Application Database';