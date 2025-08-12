## 포트폴리오 매니저 (Portfolio Manager)

한 줄 소개: 당신의 프로젝트/경력/성과를 체계적으로 수집·정리·배포하는 포트폴리오 운영 도구.

---

### 왜 이 프로젝트인가

- 문제 정의: 다수의 포트폴리오(프로젝트 사이트)가 흩어져 있고 각각 로그인/배포/변경·학습 기록이 분산되어 추적과 검색이 어렵다.
- 대상 사용자: 개인 개발자/디자이너, 소규모 팀, 에이전시 내부 운영자.
- 핵심 가치(USP): 단일 대시보드에서 모든 포트폴리오와 노트를 통합 관리, 중앙 인증/SSO로 모든 사이트 로그인 일원화, 프로젝트별 서브도메인 자동 라우팅과 배포 오케스트레이션.

### 주요 기능 (초안)

- 중앙 인증/SSO: 모든 포트폴리오 사이트의 회원가입/로그인/세션을 단일 Auth 서비스에서 관리(JWT/쿠키 선택형). 사이트 간 SSO 지원.
- 프로젝트/사이트 관리: 포트폴리오 생성, 상태/가시성(공개/비공개), 배포 타깃(서브도메인) 설정, 접근/유입 로그 요약.
- 좌측 내비·탭 기반 노트: 프로젝트 목록과 탭(학습, 변경, 조사)으로 작업/지식 기록을 구조화.
- 글로벌 검색: 노트/프로젝트/태그 전역 검색(Elasticsearch 기반)과 필터.
- 배포 오케스트레이션: 로컬은 Docker Compose, 프로덕션은 Kubernetes. Traefik/Ingress로 서브도메인 자동 라우팅.
- 권한/팀: 소유자/편집자/뷰어 역할, 프로젝트별 접근 제어.
- 템플릿: Next.js 기반 포트폴리오 사이트 템플릿 생성/클론, 공통 UI 라이브러리 제공.
- 감사 로그/버전: 주요 변경 감사 추적, 노트 이력.
- API/웹훅: 외부 자동화/동기화를 위한 REST API와 이벤트 웹훅.
- PWA 지원: 
  - 오프라인 모드: Service Worker로 캐싱, IndexedDB로 노트 로컬 저장
  - 모바일 앱 경험: 홈 화면 추가, 전체화면 모드, 푸시 알림
  - 백그라운드 동기화: 오프라인 작성 내용 자동 동기화
  - 반응형 UI: 모바일/태블릿/데스크톱 최적화
- Notion 통합:
  - 문서 자동 동기화: 프로젝트 문서를 Notion에 자동 백업
  - 현업 템플릿: PRD, TDD, API 문서, Post-mortem 등
  - 지식 관리: 학습 노트와 기술 리서치 Notion 연동
  - 팀 위키: 실시간 협업 문서 관리

> 추가하고 싶은 기능을 아래 로드맵에 체크박스로 적어주세요.

### 기술 스택 (현업 기술 폭넓게 활용)

#### 프론트엔드
- **코어**: Next.js 14 (App Router), React 18, TypeScript
- **상태관리**: Zustand (글로벌), TanStack Query (서버 상태)
- **스타일링**: Tailwind CSS, shadcn/ui, Framer Motion (애니메이션)
- **PWA**: next-pwa, Workbox, Web Push API, WebSocket (실시간)

#### 백엔드 (마이크로서비스)
- **API 게이트웨이**: Kong / Traefik
- **서비스**:
  - Auth Service: FastAPI + Keycloak (엔터프라이즈 IAM)
  - Portfolio Service: FastAPI + GraphQL (Strawberry)
  - Notification Service: Node.js + Socket.io
  - Analytics Service: Go + Gin (고성능)
- **메시지 큐**: Apache Kafka (이벤트 스트리밍), RabbitMQ (작업 큐)
- **캐싱**: Redis (세션/캐시), Redis Pub/Sub (실시간 알림)

#### 데이터 저장소
- **주 DB**: PostgreSQL (OLTP) + TimescaleDB (시계열 분석)
- **NoSQL**: MongoDB (유연한 스키마), Elasticsearch (전문 검색)
- **객체 저장소**: MinIO (S3 호환) / AWS S3
- **벡터 DB**: Qdrant (AI 임베딩 검색 - 선택적)

#### DevOps & 인프라
- **컨테이너화**: Docker, Docker Compose (개발)
- **오케스트레이션**: Kubernetes (K8s), Helm Charts
- **CI/CD**: GitLab CI / GitHub Actions + ArgoCD
- **모니터링**: 
  - Prometheus + Grafana (메트릭)
  - ELK Stack (로그: Elasticsearch, Logstash, Kibana)
  - Jaeger (분산 트레이싱)
- **인프라 관리**: Terraform (IaC), Ansible (구성 관리)

#### 추가 기술
- **API 문서화**: OpenAPI + Swagger UI, GraphQL Playground
- **테스팅**: Jest, Pytest, k6 (부하 테스트), Cypress (E2E)
- **보안**: Vault (시크릿 관리), OAuth2/OIDC, mTLS
- **백업**: Velero (K8s 백업), pg_dump 자동화

### 아키텍처 개요 (초안)

```mermaid
flowchart TB
  subgraph Users
    U1[나/관리자]
    U2[팀 멤버]
    U3[일반 방문자<br/>채용 담당자]
  end

  subgraph "Manager Web - portfolio.com"
    subgraph "공개 영역"
      PUB[공개 포트폴리오 목록<br/>프로젝트 쇼케이스]
      PUBP[공개 프로필<br/>경력/스킬 소개]
    end
    
    subgraph "인증 필요 영역"
      ADMIN[프로젝트 관리<br/>대시보드]
      NOTE[노트 관리<br/>학습/변경/조사]
      DEPLOY[배포 설정<br/>서브도메인 관리]
    end
  end

  subgraph "개별 포트폴리오 사이트"
    PS1[project1.portfolio.com<br/>공개 프로젝트 사이트]
    PS2[project2.portfolio.com<br/>공개 프로젝트 사이트]
    PS3[project3.portfolio.com<br/>비공개 프로젝트]
  end

  subgraph "API Layer"
    KONG[Kong/Traefik<br/>API Gateway]
    GQL[GraphQL<br/>Federation]
  end

  subgraph "마이크로서비스"
    AUTH[Auth Service<br/>Keycloak]
    PORT[Portfolio Service<br/>FastAPI]
    NOTIF[Notification Service<br/>Node.js + Socket.io]
    ANALYTICS[Analytics Service<br/>Go + Gin]
  end

  subgraph "메시지 브로커"
    KAFKA[Apache Kafka<br/>이벤트 스트리밍]
    RABBIT[RabbitMQ<br/>작업 큐]
    REDIS_PS[Redis Pub/Sub<br/>실시간 알림]
  end

  subgraph "데이터 저장소"
    PG[(PostgreSQL<br/>주 DB)]
    MONGO[(MongoDB<br/>NoSQL)]
    REDIS[(Redis<br/>캐시/세션)]
    ES[(Elasticsearch<br/>검색)]
    MINIO[MinIO<br/>S3 호환 저장소]
    TS[(TimescaleDB<br/>시계열)]
  end

  subgraph "모니터링"
    PROM[Prometheus]
    GRAF[Grafana]
    ELK[ELK Stack]
    JAEGER[Jaeger<br/>트레이싱]
  end

  U1 --> PUB
  U1 -->|로그인| ADMIN
  U2 -->|권한| ADMIN
  U3 --> PUB
  U3 --> PS1

  PUB --> KONG
  ADMIN --> KONG
  PS1 --> KONG
  PS2 --> KONG
  PS3 --> KONG

  KONG --> GQL
  GQL --> AUTH
  GQL --> PORT
  GQL --> NOTIF
  GQL --> ANALYTICS

  AUTH --> PG
  AUTH --> REDIS
  PORT --> PG
  PORT --> MONGO
  PORT --> MINIO
  NOTIF --> REDIS_PS
  ANALYTICS --> TS
  
  PORT --> KAFKA
  NOTIF --> KAFKA
  ANALYTICS --> KAFKA
  
  KAFKA --> ES
  
  PORT -.-> RABBIT
  NOTIF -.-> RABBIT
  
  AUTH --> PROM
  PORT --> PROM
  PROM --> GRAF
  
  KONG --> JAEGER
  GQL --> JAEGER
```

> **핵심 특징**:
> - **Manager Web 이중 역할**:
>   - 공개 영역: 일반 방문자도 포트폴리오 목록과 프로필 열람 가능
>   - 관리 영역: 로그인 후 프로젝트 관리, 노트 작성, 배포 설정
> - **현업 기술 스택**:
>   - 마이크로서비스 아키텍처 (Kong, GraphQL Federation)
>   - 이벤트 드리븐 (Kafka, RabbitMQ, Redis Pub/Sub)
>   - 폴리글랏 퍼시스턴스 (PostgreSQL, MongoDB, Redis, Elasticsearch)
>   - 완벽한 모니터링 (Prometheus, Grafana, ELK, Jaeger)
> - **실시간 기능**: WebSocket, Kafka 스트리밍으로 실시간 업데이트
> - **확장성**: Kubernetes 오케스트레이션, 수평 확장 가능

### 도메인 모델 (초안)

| 엔티티      | 핵심 필드                                                           | 비고                                  |
| ----------- | ------------------------------------------------------------------- | ------------------------------------- |
| User        | id, email, name, role                                               | 전역 사용자                           |
| Project     | id, ownerId, slug, title, visibility, status                        | 포트폴리오 단위(프로젝트/사이트 묶음) |
| Site        | id, projectId, subdomain, deployedAt, repoUrl                       | 배포 가능한 사이트 인스턴스           |
| Note        | id, projectId, type[learn\|change\|research], title, content, tags  | 좌측 탭 기반 노트                     |
| Media       | id, targetType[note\|project], targetId, url, type                  | 첨부 미디어                           |
| AuthAccount | id, userId, provider, providerUserId                                | 소셜/외부 계정 연동                   |
| Session     | id, userId, createdAt, expiresAt, revokedAt                         | 세션/토큰 관리                        |
| Deployment  | id, projectId, env[local\|prod], status, url, startedAt, finishedAt | 배포 이력                             |
| SearchIndex | id, targetType, targetId, content, updatedAt                        | 검색 인덱스                           |

### 폴더 구조

#### Phase 1-2: 기본 분리 구조
```
portfolio-manager/
├── frontend/              # Next.js 14 관리 대시보드
│   ├── src/
│   │   ├── app/          # App Router 페이지
│   │   ├── components/   # UI 컴포넌트
│   │   ├── lib/          # 유틸리티, API 클라이언트
│   │   └── types/        # TypeScript 타입 정의
│   ├── public/           # 정적 파일
│   ├── package.json
│   └── next.config.js
├── backend/               # FastAPI 통합 서비스
│   ├── app/
│   │   ├── api/          # API 엔드포인트
│   │   ├── core/         # 설정, 보안, 데이터베이스
│   │   ├── models/       # SQLAlchemy 모델
│   │   ├── schemas/      # Pydantic 스키마
│   │   └── services/     # 비즈니스 로직
│   ├── alembic/          # 데이터베이스 마이그레이션
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── docs/                  # 프로젝트 문서
├── docker-compose.yml     # 로컬 개발 환경 (PostgreSQL, Redis)
├── .env.example
├── README.md
├── CLAUDE.md
└── .mcp.json
```

#### Phase 3-4: 마이크로서비스 구조 (확장 시)
```
portfolio-manager/
├── frontend/              # Next.js 관리 대시보드
├── services/              # 마이크로서비스들
│   ├── auth-service/      # 인증/SSO 서비스 (FastAPI)
│   ├── portfolio-service/ # 포트폴리오/노트 서비스 (FastAPI)
│   ├── notification-service/ # 알림 서비스 (Node.js)
│   └── analytics-service/ # 분석 서비스 (Go)
├── shared/                # 공통 라이브러리
│   ├── ui/               # 공유 UI 컴포넌트
│   ├── sdk/              # OpenAPI 기반 SDK
│   └── config/           # 공통 설정
├── infra/                 # 인프라 설정
│   ├── compose/          # Docker Compose
│   ├── k8s/              # Kubernetes 매니페스트
│   └── helm/             # Helm Charts
└── site-templates/        # 포트폴리오 사이트 템플릿
```

### 빠른 시작

1. 사전 준비

- Node.js >= 20, pnpm
- Python 3.11+, pip/uv
- Docker, Docker Compose

2. 설치

```bash
# 프론트엔드 (Next.js 14)
cd frontend && pnpm install

# 백엔드 (FastAPI)
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn[standard] sqlalchemy pydantic alembic psycopg2-binary python-multipart python-jose[cryptography]
```

3. 로컬 인프라 기동

```bash
docker compose up -d  # PostgreSQL, Redis 등
```

4. 환경 변수
   `.env.example`을 복사하여 `.env` 생성:

```
# 공통
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/portfolio

# Auth
AUTH_JWT_SECRET=change-me
AUTH_COOKIE_DOMAIN=localhost

# Search
SEARCH_HOST=http://localhost:7700
SEARCH_API_KEY=masterKey
```

5. 개발 서버 실행

```bash
# 백엔드 (FastAPI)
cd backend && uvicorn app.main:app --reload --port 8000

# 프론트엔드 (Next.js)
cd frontend && pnpm dev
```

6. 관리자 계정 생성

- 백엔드에서 관리용 스크립트 또는 `/admin/seed` 엔드포인트로 초기 관리자 발급

### 사용법 (초안)

#### 공개 영역 (비로그인)
- 포트폴리오 둘러보기: `portfolio.com`에서 공개 프로젝트 목록 및 프로필 확인
- 프로젝트 상세보기: 개별 프로젝트 클릭 또는 `project-name.portfolio.com` 직접 접근
- 검색: 공개 프로젝트/노트에서 키워드 검색

#### 관리 영역 (로그인 필요)
- 프로젝트 관리: 새 프로젝트 생성, 공개/비공개 설정, 서브도메인 지정
- 노트 작성: 학습/변경/조사 탭에서 프로젝트별 기록 관리
- 배포 관리: 프로젝트 빌드 및 서브도메인 자동 배포
- 팀 협업: 멤버 초대, 권한 설정 (편집자/뷰어)

#### PWA 기능
- 모바일 앱 설치: 브라우저에서 "홈 화면에 추가" 선택
- 오프라인 작업: 노트 작성/수정은 오프라인에서도 가능, 온라인 시 자동 동기화
- 푸시 알림: 프로젝트 업데이트, 팀 멤버 활동 알림

### 테스트

```bash
pnpm test
pnpm test:watch
```

- 범위: 유스케이스/서비스 단위 테스트, 스냅샷(선택)
- 경계값/예외: 기간 역전, 중복 태그, 큰 미디어 파일, 네트워크 실패

### 품질/보안/성능 체크리스트

- 입력 검증: Zod/DTO 스키마로 API 입력 강제
- 권한: 역할 기반 + 소유자 검증 이중화
- 비공개 항목 보호: 서명 URL, 만료 정책
- 캐시: 목록/검색 결과 캐시, CDN 헤더 최적화
- 성능: N+1 쿼리 방지, 인덱스 설계, e2e 지연 예산 문서화
- 인증 보안: JWT 서명/회전, Refresh 토큰/세션 블랙리스트, CSRF(쿠키 모드 시)
- 레이트 리미트/감사: 로그인/관리 엔드포인트에 레이트 리미트, 감사 로그 저장

### 배포 (예시)

- 프론트(매니저 웹): Vercel(Preview/Prod 브랜치 전략)
- 백엔드: Kubernetes(Ingress, HPA), 또는 Fly.io/Render/Cloud Run
- DB: Managed PostgreSQL + 마이그레이션 파이프라인
- 서브도메인 전략: `*.portfolio.example.com` 와일드카드 DNS → Ingress/Traefik 라우팅 → 프로젝트별 `slug.portfolio.example.com`
- Compose(로컬): Traefik 라벨 기반 라우팅, `.env`로 호스트네임 지정

## 🎯 현실적 구현 로드맵 (단계적 접근법)

### 📝 개발 워크플로우 및 문서 관리

#### 기능별 개발 사이클
1. **기능 설계**: Notion에서 기능 명세 작성 (PRD/TDD)
2. **코드 구현**: 효율적 개발 및 테스트 주도 개발(TDD)
3. **테스트 및 검증**: 자동화 테스트 및 품질 검증
4. **기능별 커밋**: 완성된 기능 단위로 의미있는 커밋 메시지
5. **문서 동기화**: Notion을 통한 자동 문서 업데이트 및 진행상황 추적

#### 커밋 관리 전략
```bash
# 기능별 커밋 예시 (Conventional Commits 규칙 준수)
feat: 프로젝트 CRUD API 구현 (Phase 1)
feat: 노트 시스템 좌측 탭 UI 완성 (Phase 1)  
feat: PWA Service Worker 및 오프라인 모드 (Phase 2)
feat: Notion API 동기화 기능 (Phase 3)
feat: 마이크로서비스 아키텍처 구현 (Phase 4)

# 타입별 커밋 규칙
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드/패키지 설정
```

#### Notion 통합 문서 관리
- **자동 동기화**: 각 기능 완성시 Notion에 개발 로그 자동 생성
- **진행 상황 추적**: Phase별 체크리스트와 실시간 연동
- **아키텍처 결정 기록(ADR)**: 중요한 기술 선택 이유 문서화
- **API 문서**: OpenAPI 스펙과 Notion 자동 동기화
- **회고록**: 스프린트 완료 후 자동 회고 문서 생성
- **지식 관리**: 학습 노트와 기술 리서치 체계적 정리

### Phase 1: MVP - 실사용 가능한 포트폴리오 매니저 (2-3개월)
**목표**: 핵심 기능으로 실제 사용 가능한 서비스 구축

#### 📋 기술 스택 (최소한)
- **프론트엔드**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **백엔드**: Next.js API Routes 또는 FastAPI (단일 서비스)
- **데이터베이스**: PostgreSQL (Supabase 또는 Neon DB)
- **인증**: NextAuth.js 또는 Supabase Auth
- **배포**: Vercel (프론트), Railway/Fly.io (백엔드)
- **스토리지**: Supabase Storage
- **검색**: 기본 PostgreSQL 전문검색

#### ✅ 핵심 기능
- [x] 프로젝트 CRUD (생성, 수정, 삭제, 목록)
- [x] 공개/비공개 포트폴리오 전환
- [x] 좌측 탭 기반 노트 시스템 (학습/변경/조사)
- [x] 기본 검색 (제목, 내용)
- [x] 반응형 UI
- [x] 사용자 인증 및 세션 관리

**예상 비용**: 월 $0-20  
**포트폴리오 어필**: "Next.js 풀스택 개발", "PostgreSQL DB 설계", "반응형 웹 애플리케이션"

### Phase 2: PWA 및 중급 기능 (1-2개월)
**목표**: 사용자 경험 개선 및 오프라인 기능

#### 📋 추가 기술
- **PWA**: next-pwa, Service Worker, IndexedDB
- **실시간**: WebSocket 또는 Server-Sent Events  
- **캐싱**: Redis (Upstash 무료 플랜)
- **고급 검색**: Elasticsearch (Bonsai) 또는 MeiliSearch
- **상태관리**: Zustand (복잡한 상태 시 도입)

#### ✅ 추가 기능
- [x] PWA 지원 (오프라인 모드, 앱 설치)
- [x] 실시간 알림 및 업데이트
- [x] 고급 검색 (태그, 필터)
- [x] 노트 버전 관리
- [x] 미디어 파일 업로드 및 관리

**예상 비용**: 월 $20-50  
**포트폴리오 어필**: "PWA 구현", "Redis 캐싱", "실시간 기능", "오프라인 지원"

### Phase 3: 고급 기능 및 자동화 (2-3개월)
**목표**: 운영 효율성과 팀 협업 지원

#### 📋 추가 기술
- **메시지 큐**: Redis + Bull Queue (작업 큐)
- **모니터링**: Sentry (에러), Vercel Analytics
- **CI/CD**: GitHub Actions
- **Notion 통합**: Notion API를 통한 문서 동기화
- **배포 자동화**: 서브도메인별 자동 배포

#### ✅ 추가 기능
- [x] Notion 동기화 (문서 자동 백업)
- [x] 팀 협업 (권한 관리, 멤버 초대)
- [x] 배포 자동화 및 서브도메인 관리
- [x] 분석 대시보드 (방문자, 사용 통계)
- [x] 감사 로그 및 변경 이력

**예상 비용**: 월 $50-100  
**포트폴리오 어필**: "Notion API 통합", "CI/CD 파이프라인", "팀 협업 시스템", "분석 대시보드"

### Phase 4: 스케일업 및 현업 기술 도입 (3-6개월)
**목표**: 포트폴리오 어필을 위한 엔터프라이즈급 기술 경험

#### 📋 고급 기술 도입 (선택적)
- **마이크로서비스**: 필요시 Auth, Portfolio, Notification 서비스 분리
- **메시지 브로커**: Apache Kafka (Confluent Cloud) 또는 RabbitMQ
- **컨테이너**: Docker, Docker Compose (개발환경)
- **오케스트레이션**: Kubernetes (로컬 minikube) 학습 목적
- **모니터링**: Prometheus + Grafana (로컬 구성)
- **API Gateway**: Kong 또는 Traefik (로컬)

#### ✅ 엔터프라이즈 기능
- [x] 서비스 분리 및 마이크로서비스 아키텍처 경험
- [x] 이벤트 드리븐 아키텍처 (Kafka/RabbitMQ)
- [x] 컨테이너화 및 오케스트레이션 학습
- [x] 분산 모니터링 및 로깅
- [x] API Gateway를 통한 라우팅

**예상 비용**: 월 $100-200 (또는 로컬 환경으로 비용 절약)  
**포트폴리오 어필**: "마이크로서비스 아키텍처", "Kafka 이벤트 스트리밍", "Kubernetes 경험", "모니터링 시스템"

---

## 💰 비용 최적화 전략

### 무료/저비용 서비스 활용
- **Supabase/Neon**: PostgreSQL + Auth + Storage (무료 플랜)
- **Vercel**: 프론트엔드 배포 (무료 플랜)
- **Railway/Fly.io**: 백엔드 배포 ($5-10/월)
- **Upstash**: Redis 캐싱 (무료 플랜)
- **GitHub Actions**: CI/CD (무료 플랜)

### 로컬 개발로 학습 비용 절약
- **Docker Compose**: 로컬에서 복잡한 스택 구성
- **minikube**: Kubernetes 로컬 학습
- **로컬 Kafka/Redis**: 개발 환경에서 무료 경험

---

## 🎯 학습 및 경력 어필 포인트

### Phase 1 완료 후
- "Next.js 14 + TypeScript 풀스택 개발 경험"
- "PostgreSQL 데이터 모델링 및 쿼리 최적화"
- "RESTful API 설계 및 구현"

### Phase 2 완료 후  
- "PWA 개발 및 오프라인 기능 구현"
- "Redis를 활용한 성능 최적화"
- "실시간 웹 애플리케이션 개발 경험"

### Phase 3 완료 후
- "외부 API 통합 (Notion) 및 자동화"
- "CI/CD 파이프라인 구축 및 운영"
- "팀 협업 도구 및 권한 관리 시스템"

### Phase 4 완료 후
- "마이크로서비스 아키텍처 설계 및 구현"
- "이벤트 드리븐 시스템 (Kafka) 개발 경험"  
- "컨테이너 오케스트레이션 (Kubernetes) 실습"
- "분산 시스템 모니터링 및 운영"

---

### 기존 체크리스트 (Phase 1 우선)

- [ ] 도메인 확정 및 스키마 1차안(Project/Site/Note/Auth/Deployment)
- [ ] 인증 서비스(NextAuth.js) MVP: 회원가입/로그인, 세션 관리
- [ ] 매니저 웹(좌측 내비·탭) MVP: 프로젝트 목록, 노트(학습/변경/조사)
- [ ] 포트폴리오 API: 프로젝트/사이트 CRUD, 배포 메타
- [ ] 기본 검색: PostgreSQL 전문검색으로 시작
- [ ] 반응형 UI 구현 (모바일/태블릿/데스크톱)
- [ ] 배포 환경 구성 (Vercel + Supabase)
- [ ] (Phase 2) PWA 및 고급 검색 구현
- [ ] (Phase 3) Notion API 통합
- [ ] (Phase 4) 마이크로서비스 및 Kafka 도입

### 라이선스 / 문의

- 라이선스: <MIT/Apache-2.0/Private 중 선택>
- 문의: <이메일/이슈 트래커 링크>

---

작성 가이드: 위 꺾쇠(< >) 구간을 먼저 채우고, 기능/로드맵은 체크리스트를 조정하세요. 실제 스택과 폴더 구조가 정해지면 해당 섹션을 확정해 주세요.
