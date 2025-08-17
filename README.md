# 포트폴리오 매니저 (Portfolio Manager)

> **한 줄 소개: AI 시대, 폭발적으로 늘어나는 당신의 프로젝트에 '스토리'와 '맥락'을 부여하는 통합 포트폴리오 플랫폼**

---

## 🚀 왜 이 프로젝트인가? (Why This Project?)

AI 도구 덕분에 누구나 쉽게 프로젝트를 만드는 시대가 왔습니다. 하지만 이런 변화는 새로운 문제를 낳았습니다.

- **관리의 문제**: GitHub, Vercel 등에 흩어진 수십 개의 프로젝트. "내가 이걸 왜, 어떻게 만들었더라?"
- **설명의 문제**: AI로 만든 결과물은 있지만, "어떤 고민을 했고, 어떻게 해결했나요?" 라는 질문에 답하기 어렵습니다.
- **증명의 문제**: 나의 진짜 실력인 '문제 해결 과정'과 '학습 기록'이 사라지고 있습니다.

**Portfolio Manager는 단순한 관리 도구를 넘어, 당신의 모든 창작 과정과 성장 스토리를 기록하고 증명하는 'AI 시대의 새로운 이력서'입니다.**

## 🎯 핵심 타겟 및 가치 (Target & USP)

- **주요 타겟**: **AI 네이티브 창작자** (AI 도구로 프로젝트를 만드는 개발자, 디자이너, 학생, 기획자)
- **핵심 가치**:
  1. **AI 프로젝트 컨텍스트 보존**: 어떤 AI 프롬프트를 썼고, 무엇을 배웠는지 프로젝트와 함께 기록합니다.
  2. **프로젝트 스토리텔링**: 기술적 과정을 비개발자도 이해할 수 있는 매력적인 스토리로 만듭니다.
  3. **통합 관리**: 코드(GitHub), 배포(Vercel), 문서(Notion)를 하나의 프로젝트 단위로 통합 관리합니다.

## ✨ 핵심 경험 (Core Experiences)

- **AI 컨텍스트 노트**: AI와의 대화, 프롬프트를 프로젝트의 맥락과 함께 기록하고 자산화합니다.
- **프로젝트 스토리텔링**: 클릭 몇 번으로 당신의 기술적 성과를 매력적인 스토리로 전환합니다.
- **통합 대시보드**: 흩어져 있던 코드, 배포, 문서를 하나의 프로젝트 단위로 완벽하게 통합 관리합니다.
- **실시간 협업**: PWA와 실시간 기능을 통해 언제 어디서든 동료와 함께 포트폴리오를 개선합니다.
- **지능형 포트폴리오**: AI가 당신의 프로젝트를 분석하여 면접 질문을 예측하고 개선점을 제안합니다.

> 기술적 세부사항과 구현 계획은 아래 로드맵에서 확인하세요.

## 기술 스택 (현업 기술 폭넓게 활용)

### 프론트엔드

- **코어**: Next.js 14 (App Router), React 18, TypeScript
- **상태관리**: Zustand (글로벌), TanStack Query (서버 상태)
- **스타일링**: Tailwind CSS, shadcn/ui, Framer Motion (애니메이션)
- **PWA**: next-pwa, Workbox, Web Push API, WebSocket (실시간)

### 백엔드 (마이크로서비스)

- **API 게이트웨이**: Kong / Traefik
- **서비스**:
  - Auth Service: FastAPI + Keycloak (엔터프라이즈 IAM)
  - Portfolio Service: FastAPI + GraphQL (Strawberry)
  - Notification Service: Node.js + Socket.io
  - Analytics Service: Go + Gin (고성능)
- **메시지 큐**: Apache Kafka (이벤트 스트리밍), RabbitMQ (작업 큐)
- **캐싱**: Redis (세션/캐시), Redis Pub/Sub (실시간 알림)

### 데이터 저장소

- **주 DB**: PostgreSQL (OLTP) + TimescaleDB (시계열 분석)
- **NoSQL**: MongoDB (유연한 스키마), Elasticsearch (전문 검색)
- **객체 저장소**: MinIO (S3 호환) / AWS S3
- **벡터 DB**: Qdrant (AI 임베딩 검색 - 선택적)

### DevOps & 인프라

- **컨테이너화**: Docker, Docker Compose (개발)
- **오케스트레이션**: Kubernetes (K8s), Helm Charts
- **CI/CD**: GitLab CI / GitHub Actions + ArgoCD
- **모니터링**:
  - Prometheus + Grafana (메트릭)
  - ELK Stack (로그: Elasticsearch, Logstash, Kibana)
  - Jaeger (분산 트레이싱)
- **인프라 관리**: Terraform (IaC), Ansible (구성 관리)

### 추가 기술

- **API 문서화**: OpenAPI + Swagger UI, GraphQL Playground
- **테스팅**: Jest, Pytest, k6 (부하 테스트), Cypress (E2E)
- **보안**: Vault (시크릿 관리), OAuth2/OIDC, mTLS
- **백업**: Velero (K8s 백업), pg_dump 자동화

## 아키텍처 개요 (초안)

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
>
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

## 📊 도메인 모델 (3NF 정규화 완료)

**설계 문서**: `docs/02.데이터베이스_ERD.md` (S-Class 평가 완료)

### MVP Phase 1 핵심 엔티티 (7개)

| 엔티티           | 핵심 필드                                                            | 비고                                    |
| ---------------- | -------------------------------------------------------------------- | --------------------------------------- |
| **User**         | id(UUID), email(UK), name, avatar_url, role, github_username        | 전역 사용자 + 소셜 프로필               |
| **AuthAccount**  | id, user_id(FK), provider, provider_account_id, access_token        | 소셜 로그인 연동 (GitHub/Google)        |
| **Session**      | id, user_id(FK), session_token(UK), expires, ip_address             | 세션/토큰 관리                          |
| **Project**      | id, owner_id(FK), slug, title, content(JSONB), tech_stack(Array)    | 포트폴리오 프로젝트 메타데이터          |
|                  | visibility(enum), status(enum), featured, view_count, like_count    | 공개/비공개, 상태 관리, 통계            |
| **GithubRepository** | id, project_id(FK,UK), github_url, stars, language, last_commit | GitHub 저장소 정보 (1:1, 3NF 준수)     |
| **Note**         | id, project_id(FK), type(enum), title, content(JSONB), tags(Array)  | 좌측 탭 기반 노트 (learn/change/research) |
| **Media**        | id, target_type(enum), target_id, file_path, file_size, mime_type   | 첨부 미디어 (project/note 연결)         |

### PostgreSQL 최적화 기능 활용

- **JSONB**: 프로젝트 콘텐츠, 노트 콘텐츠 (인덱싱 + 유연성)
- **배열 타입**: tech_stack, categories, tags (GIN 인덱스 지원)
- **ENUM 타입**: 상태/가시성/노트타입 (타입 안전성)
- **전문검색**: GIN 인덱스 + tsvector (Elasticsearch 대체 가능)
- **UUID 기본키**: 보안성 + 분산 시스템 대응

## 폴더 구조

### Phase 1-2: 기본 분리 구조

```plane
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

### Phase 3-4: 마이크로서비스 구조 (확장 시)

```plane
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

## 빠른 시작

### 1. 사전 준비 및 환경 검증

**필수 소프트웨어**:

- Node.js >= 20 (LTS 권장)
- pnpm (패키지 매니저)
- Python 3.11+
- Docker Desktop (최신 버전)
- Git

**환경 검증**:

```bash
# 버전 확인
node --version  # v20.x.x 이상
pnpm --version  # 8.x.x 이상
python --version  # 3.11.x 이상
docker --version  # 24.x.x 이상
```

#### 2. 프로젝트 설정

**저장소 클론**:

```bash
git clone <repository-url>
cd portfolio-manager
```

**의존성 설치**:

```bash
# 프론트엔드 의존성 (Next.js 14)
cd frontend
pnpm install
cd ..

# 백엔드 가상환경 설정 (FastAPI)
cd backend
python -m venv .venv

# 가상환경 활성화 (OS별)
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Python 의존성 설치
pip install -U pip
pip install -r requirements.txt
# 또는 개발용 패키지 설치:
# pip install fastapi uvicorn[standard] sqlalchemy pydantic alembic psycopg2-binary python-multipart python-jose[cryptography]
cd ..
```

### 3. 인프라 및 환경 설정

**Docker 서비스 시작**:

```bash
# PostgreSQL, Redis 등 로컬 서비스 기동
docker compose up -d

# 서비스 상태 확인
docker compose ps
```

**환경 변수 설정**:

```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (필수 값들)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/portfolio
AUTH_JWT_SECRET=your-super-secret-jwt-key-change-me
AUTH_COOKIE_DOMAIN=localhost
SEARCH_HOST=http://localhost:7700
SEARCH_API_KEY=masterKey
```

**데이터베이스 초기화** (백엔드 FastAPI 사용 시):

```bash
cd backend
source .venv/bin/activate  # 가상환경 활성화

# 데이터베이스 마이그레이션
alembic upgrade head

# 초기 데이터 시드 (선택적)
python scripts/seed_data.py
cd ..
```

### 4. 개발 서버 실행

**터미널 1 - 백엔드 서버**:

```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# ✅ 백엔드 서버: http://localhost:8000
# 📋 API 문서: http://localhost:8000/docs
```

**터미널 2 - 프론트엔드 서버**:

```bash
cd frontend
pnpm dev

# ✅ 프론트엔드 서버: http://localhost:3000
```

### 5. 초기 설정 완료

**관리자 계정 생성**:

```bash
# 방법 1: API 엔드포인트 사용
curl -X POST http://localhost:8000/admin/seed \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# 방법 2: 스크립트 실행
cd backend && python scripts/create_admin.py
```

**서비스 접근**:

- 🌐 **매니저 웹**: <http://localhost:3000>
- 🔧 **API 문서**: <http://localhost:8000/docs>
- 🗄️ **데이터베이스**: localhost:5432 (postgres/postgres)
- 📦 **Redis**: localhost:6379

### 6. 개발 환경 검증

**헬스체크**:

```bash
# 백엔드 API 상태 확인
curl http://localhost:8000/health

# 데이터베이스 연결 확인
curl http://localhost:8000/api/health/db

# 프론트엔드 접근 확인
curl http://localhost:3000
```

### 7. 문제 해결

**일반적인 문제**:

- **포트 충돌**: 3000, 8000, 5432, 6379 포트가 사용 중인지 확인
- **Docker 오류**: `docker compose down && docker compose up -d`로 재시작
- **Python 가상환경**: 올바른 가상환경 활성화 확인
- **권한 문제**: `sudo` 없이 Docker 실행 가능한지 확인

**로그 확인**:

```bash
# Docker 서비스 로그
docker compose logs -f postgres redis

# 백엔드 로그 (디버그 모드)
cd backend && PYTHONPATH=. python -m uvicorn app.main:app --reload --log-level debug

# 프론트엔드 상세 로그
cd frontend && pnpm dev --verbose
```

## 사용법 (초안)

### 공개 영역 (비로그인)

- 포트폴리오 둘러보기: `portfolio.com`에서 공개 프로젝트 목록 및 프로필 확인
- 프로젝트 상세보기: 개별 프로젝트 클릭 또는 `project-name.portfolio.com` 직접 접근
- 검색: 공개 프로젝트/노트에서 키워드 검색

### 관리 영역 (로그인 필요)

- 프로젝트 관리: 새 프로젝트 생성, 공개/비공개 설정, 서브도메인 지정
- 노트 작성: 학습/변경/조사 탭에서 프로젝트별 기록 관리
- 배포 관리: 프로젝트 빌드 및 서브도메인 자동 배포
- 팀 협업: 멤버 초대, 권한 설정 (편집자/뷰어)

### PWA 기능

- 모바일 앱 설치: 브라우저에서 "홈 화면에 추가" 선택
- 오프라인 작업: 노트 작성/수정은 오프라인에서도 가능, 온라인 시 자동 동기화
- 푸시 알림: 프로젝트 업데이트, 팀 멤버 활동 알림

## 테스트

### 프론트엔드 테스트
```bash
cd frontend
pnpm test
pnpm test:watch
```

### 백엔드 테스트 (PostgreSQL 환경)

```bash
# 1. 테스트용 PostgreSQL 컨테이너 시작
docker-compose --profile test up -d postgres-test

# 2. 테스트 실행
cd backend
python -m pytest tests/ -v

# 3. 테스트 완료 후 정리
docker-compose --profile test down
```

**자동 설정 스크립트 사용:**
```bash
cd backend
./test-db-setup.sh --run-tests  # 환경 설정 + 테스트 실행
```

**테스트 환경 특징:**
- **PostgreSQL**: 메인 DB와 동일한 groonga/pgroonga 이미지 사용
- **전문검색**: PGroonga 확장으로 실제 전문검색 기능 테스트
- **테스트 격리**: 각 테스트마다 데이터 자동 정리
- **빠른 실행**: tmpfs 인메모리 파일시스템 사용

**테스트 범위:**
- 도메인 로직 단위 테스트
- API 엔드포인트 통합 테스트  
- 미디어 업로드/처리 테스트
- 경계값/예외: 기간 역전, 중복 태그, 큰 미디어 파일, 네트워크 실패

## 품질/보안/성능 체크리스트

- 입력 검증: Zod/DTO 스키마로 API 입력 강제
- 권한: 역할 기반 + 소유자 검증 이중화
- 비공개 항목 보호: 서명 URL, 만료 정책
- 캐시: 목록/검색 결과 캐시, CDN 헤더 최적화
- 성능: N+1 쿼리 방지, 인덱스 설계, e2e 지연 예산 문서화
- 인증 보안: JWT 서명/회전, Refresh 토큰/세션 블랙리스트, CSRF(쿠키 모드 시)
- 레이트 리미트/감사: 로그인/관리 엔드포인트에 레이트 리미트, 감사 로그 저장

## 배포 (예시)

- 프론트(매니저 웹): Vercel(Preview/Prod 브랜치 전략)
- 백엔드: Kubernetes(Ingress, HPA), 또는 Fly.io/Render/Cloud Run
- DB: Managed PostgreSQL + 마이그레이션 파이프라인
- 서브도메인 전략: `*.portfolio.example.com` 와일드카드 DNS → Ingress/Traefik 라우팅 → 프로젝트별 `slug.portfolio.example.com`
- Compose(로컬): Traefik 라벨 기반 라우팅, `.env`로 호스트네임 지정

## 🎯 현실적 구현 로드맵 (단계적 성장 계획)

이 로드맵은 단순한 기능 구현을 넘어, 각 단계를 완료하며 **당신의 포트폴리오를 강화**할 수 있도록 설계되었습니다.

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
🎓 **학습 및 경력 어필 포인트**:

- "Next.js 14 풀스택 개발 및 PostgreSQL DB 설계 경험"
- "실무 수준의 반응형 웹 애플리케이션 구축 능력"

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
🎓 **학습 및 경력 어필 포인트**:

- "PWA 구현을 통한 네이티브 앱 수준의 사용자 경험 제공"
- "Redis 캐싱 및 실시간 통신 기술을 활용한 성능 최적화"

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
🎓 **학습 및 경력 어필 포인트**:

- "외부 API(Notion) 연동 및 CI/CD 파이프라인 구축 경험"
- "팀 단위 협업을 위한 권한 관리 시스템 설계 능력"

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
🎓 **학습 및 경력 어필 포인트**:

- "마이크로서비스 아키텍처 설계 및 Kafka 기반 이벤트 스트리밍 경험"
- "Kubernetes를 활용한 컨테이너 오케스트레이션 및 분산 시스템 운영 능력"

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
