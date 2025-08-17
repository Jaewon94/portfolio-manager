# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 도움이 되는 가이드를 제공합니다.

## 📋 문서 역할 구분

- **README.md**: 사용자를 위한 프로젝트 소개, 설치 방법, 사용법
- **CLAUDE.md**: AI 협업을 위한 개발 가이드, 아키텍처, 제약사항, 작업 템플릿

## 프로젝트 개요

당신의 프로젝트/경력/성과를 체계적으로 수집·정리·배포하는 포트폴리오 운영 도구입니다. README.md에 따르면 이는 다수의 포트폴리오 사이트를 중앙에서 통합 관리하고, SSO를 통해 모든 사이트의 로그인을 일원화하는 포트폴리오 매니저입니다.

## 📊 핵심 도메인 모델 (3NF 준수 완료)

**설계 문서**: `docs/02.데이터베이스_ERD.md` (S-Class 평가 완료)

### MVP Phase 1 핵심 엔티티 (7개)
- **User**: 전역 사용자 (id, email, name, bio, github_username, role, is_verified)
- **AuthAccount**: 소셜 로그인 연동 (id, userId, provider, provider_account_id, tokens)
- **Session**: 세션/토큰 관리 (id, userId, session_token, expires, ip_address, user_agent)
- **Project**: 포트폴리오 단위 (id, owner_id, slug, title, description, content[JSONB], tech_stack[], categories[], tags[], status, visibility, featured, view_count, like_count)
- **GithubRepository**: GitHub 저장소 정보 (id, project_id, github_url, repository_name, stars, forks, language, license, last_commit_date, sync_enabled) - **3NF 준수를 위해 Project에서 분리**
- **Note**: 좌측 탭 기반 노트 (id, project_id, type[learn|change|research], title, content[JSONB], tags[], is_pinned, is_archived)
- **Media**: 첨부 미디어 (id, target_type[project|note], target_id, original_name, file_path, file_size, mime_type, type[image|video|document], width, height, is_public, alt_text)

### Phase 2+ 확장 엔티티
- **Site**: 배포된 사이트 (id, project_id, subdomain, custom_domain, deployed_at, status)
- **Deployment**: 배포 이력 (id, project_id, env[local|staging|production], status, url, build_time, error_message)
- **SearchIndex**: 전문 검색 인덱스 (PostgreSQL tsvector 기반)

## 주요 기능 구현 시 고려사항

1. **중앙 인증/SSO**
   - 모든 포트폴리오 사이트의 회원가입/로그인/세션을 단일 Auth 서비스에서 관리
   - JWT/쿠키 선택형, 사이트 간 SSO 지원

2. **프로젝트/사이트 관리**
   - 포트폴리오 생성, 상태/가시성(공개/비공개) 설정
   - 배포 타깃(서브도메인) 설정, 접근/유입 로그 요약

3. **좌측 내비·탭 기반 노트**
   - 프로젝트 목록과 탭(학습, 변경, 조사)으로 작업/지식 기록 구조화
   - 전역 검색: 노트/프로젝트/태그 전역 검색(Elasticsearch 기반)

4. **배포 오케스트레이션**
   - 로컬은 Docker Compose, 프로덕션은 Kubernetes
   - Traefik/Ingress로 서브도메인 자동 라우팅

5. **PWA 지원**
   - 오프라인 모드: Service Worker로 캐싱, IndexedDB로 노트 로컬 저장
   - 모바일 앱 경험: 홈 화면 추가, 전체화면 모드, 푸시 알림
   - 백그라운드 동기화: 오프라인 작성 내용 자동 동기화

6. **Notion 통합**
   - 문서 자동 동기화: 프로젝트 문서를 Notion에 자동 백업
   - 현업 템플릿: PRD, TDD, API 문서, Post-mortem 등
   - 지식 관리: 학습 노트와 기술 리서치 Notion 연동

## 기술 스택 옵션

### 현업 기술 폭넓게 활용

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

#### 데이터 저장소 (폴리글랏 퍼시스턴스)
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

### 프로젝트 구조

#### Phase 1-2: 기본 분리 구조 (현재)
```
portfolio-manager/
├── frontend/              # Next.js 14 관리 대시보드
│   ├── src/app/          # App Router 페이지
│   ├── src/components/   # UI 컴포넌트 
│   ├── src/lib/          # 유틸리티, API 클라이언트
│   └── src/types/        # TypeScript 타입 정의
├── backend/               # FastAPI 통합 서비스
│   ├── app/api/          # API 엔드포인트
│   ├── app/core/         # 설정, 보안, 데이터베이스
│   ├── app/models/       # SQLAlchemy 모델
│   └── app/services/     # 비즈니스 로직
├── docs/                  # 프로젝트 문서
├── docker-compose.yml     # 로컬 개발 환경
└── .mcp.json              # MCP 서버 설정
```

#### Phase 3-4: 마이크로서비스 확장 구조
```
portfolio-manager/
├── frontend/              # Next.js 관리 대시보드
├── services/              # 마이크로서비스들
│   ├── auth-service/      # 인증/SSO 서비스
│   ├── portfolio-service/ # 포트폴리오/노트 서비스
│   └── notification-service/ # 알림 서비스
├── shared/ui/             # 공유 UI 컴포넌트
├── infra/k8s/             # Kubernetes 매니페스트
└── site-templates/        # 포트폴리오 사이트 템플릿
```

## 🚨 Phase별 제약사항 및 안티-패턴

### 필수 원칙: YAGNI (You Aren't Gonna Need It)
> "지금 당장 필요하지 않으면 구현하지 마라. MVP부터 시작해서 실제 필요에 의해서만 확장하라."

### Phase별 기술 제약

#### ❌ Phase 1 금지 사항
```yaml
# 복잡한 인프라 도구 금지
Kubernetes: "개발 환경에도 K8s 사용 금지 → Docker Compose만 사용"
Kafka: "메시지 큐 불필요 → 직접 API 호출로 충분"
Microservices: "단일 Next.js 앱 또는 최대 2개 서비스까지만"
Elasticsearch: "PostgreSQL full-text search로 충분"
Redis: "인메모리 캐시나 DB 레벨 캐시로 시작"
GraphQL: "REST API부터 시작, 복잡도 증가 시에만 검토"

# 과도한 추상화 금지
Generic_Repository_Pattern: "직접 ORM 사용, 불필요한 레이어 생성 금지"
Complex_Factory_Pattern: "간단한 클래스 인스턴스화로 충분"
Event_Sourcing: "일반적인 CRUD부터 시작"
```

#### ⚠️ Phase 2-3 주의사항
```yaml
# 점진적 도입만 허용
PWA: "기본 기능 완성 후 오프라인 기능 추가"
Redis: "성능 병목이 실제 발생한 후에만 도입"
Message_Queue: "비동기 처리가 명확히 필요한 기능에만"
Monitoring: "기본 로깅부터 시작, 운영 이슈 발생 시 확장"
```

#### ✅ Phase 4 엔터프라이즈 허용
```yaml
# 학습 목적의 고급 기술 허용
Kubernetes: "포트폴리오 어필용, 로컬 minikube로 실습"
Microservices: "명확한 도메인 경계가 있는 경우만"
Kafka: "이벤트 드리븐 아키텍처 학습 목적"
Service_Mesh: "Istio 등은 선택적, 복잡도 고려"
```

### 공통 안티-패턴

#### 🚫 절대 금지
```bash
# 과도한 엔지니어링
❌ "확장성을 고려해서 처음부터 마이크로서비스로..."
✅ "MVP 완성 후 필요에 따라 서비스 분리 검토"

❌ "나중을 위해 Generic한 추상화 레이어를..."
✅ "현재 요구사항에 맞는 최소한의 구현"

❌ "모든 에러 케이스를 다 처리해야..."
✅ "핵심 플로우부터 구현, 에러 처리는 점진적 추가"

# 기술 스택 과욕
❌ "최신 기술 10개를 다 써봐야..."
✅ "익숙한 기술로 빠르게 MVP, 하나씩 점진적 추가"

❌ "완벽한 아키텍처 설계 후 개발 시작"
✅ "기본 구조로 시작해서 필요에 따라 리팩토링"
```

#### 📏 복잡도 측정 기준
```yaml
간단함_지표:
  - 새로운 기능을 1-2일 내에 추가 가능
  - 버그 수정이 30분 내에 완료
  - 신입 개발자가 2주 내에 기여 가능

복잡함_경고:
  - 설정 파일이 100줄 초과
  - 의존성이 20개 초과  
  - 서비스가 5개 초과
  - 빌드 시간이 5분 초과
```

## 📋 API 설계 요약 (개발 참조용)

**설계 문서**: `docs/03.API_엔드포인트_설계.md` (S-Class 평가 완료)

### 핵심 API 엔드포인트

#### 인증 API (v1)
- `POST /api/auth/login/{provider}` - 소셜 로그인 (GitHub/Google)
- `POST /api/auth/logout` - 로그아웃
- `GET /api/auth/me` - 현재 사용자 정보
- `POST /api/auth/refresh` - 토큰 갱신

#### 프로젝트 API (v1)
- `GET /api/projects` - 프로젝트 목록 (페이지네이션, 필터링)
- `POST /api/projects` - 프로젝트 생성
- `GET /api/projects/{id}` - 프로젝트 상세
- `PATCH /api/projects/{id}` - 프로젝트 수정
- `DELETE /api/projects/{id}` - 프로젝트 삭제

#### 노트 API (v1)
- `GET /api/projects/{projectId}/notes` - 노트 목록 (타입별)
- `POST /api/projects/{projectId}/notes` - 노트 생성
- `GET /api/notes/{id}` - 노트 상세
- `PATCH /api/notes/{id}` - 노트 수정
- `DELETE /api/notes/{id}` - 노트 삭제

#### 검색 API (v1)
- `GET /api/search` - 전역 검색 (프로젝트/노트/사용자)
- `GET /api/search/autocomplete` - 자동완성

### 표준 응답 형식
```typescript
interface SuccessResponse<T> {
  success: true;
  data: T;
  meta?: { total?: number; page?: number; pageSize?: number };
}

interface ErrorResponse {
  success: false;
  error: { code: string; message: string; details?: any };
  timestamp: string;
  path: string;
}
```

## 🎯 현실적 4단계 구현 로드맵

이 프로젝트는 현실적인 단계별 접근법을 통해 점진적으로 엔터프라이즈급 기술 스택을 학습하고 구현할 수 있도록 설계되었습니다.

### 📝 개발 워크플로우 및 문서 관리

#### 기능별 개발 사이클
1. **기능 설계**: Notion에서 기능 명세 작성 (PRD/TDD)
2. **코드 구현**: MCP 서버 활용한 효율적 개발
3. **테스트 및 검증**: Playwright를 통한 자동화 테스트
4. **기능별 커밋**: 완성된 기능 단위로 의미있는 커밋 메시지
5. **문서 동기화**: Notion MCP를 통한 자동 문서 업데이트

#### 커밋 관리 전략

```bash
# 기능별 커밋 예시
feat: 프로젝트 CRUD API 구현 (Phase 1)
feat: 노트 시스템 좌측 탭 UI 완성 (Phase 1)
feat: PWA Service Worker 및 오프라인 모드 (Phase 2)
feat: Notion API 동기화 기능 (Phase 3)

# Conventional Commits 규칙 준수
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포맷팅, 세미콜론 누락 등
refactor: 코드 리팩토링 (기능 변경 없음)
test: 테스트 코드 추가/수정
chore: 빌드 과정, 패키지 매니저 설정 등
```

#### Notion 문서 관리

- **자동 동기화**: 각 기능 완성시 Notion에 개발 로그 자동 생성
- **진행 상황 추적**: Phase별 체크리스트와 연동
- **아키텍처 결정 기록(ADR)**: 중요한 기술 선택 이유 문서화
- **API 문서**: OpenAPI 스펙과 Notion 동기화
- **회고록**: 스프린트 완료 후 자동 회고 문서 생성

#### 개발 프로세스 통합

```mermaid
flowchart LR
    A[기능 요구사항] --> B[Notion PRD 작성]
    B --> C[MCP 서버로 코드 구현]
    C --> D[Playwright 테스트]
    D --> E[기능별 커밋]
    E --> F[Notion 문서 동기화]
    F --> G[다음 기능으로 이동]
```

### Phase 1: MVP - 실사용 가능한 포트폴리오 매니저 (2-3개월)
**목표**: 핵심 기능으로 실제 사용 가능한 서비스 구축

#### 기술 스택 (최소한)
- **프론트엔드**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **백엔드**: Next.js API Routes 또는 FastAPI
- **데이터베이스**: PostgreSQL (Supabase/Neon DB)
- **인증**: NextAuth.js 또는 Supabase Auth
- **배포**: Vercel, Railway/Fly.io

#### 핵심 기능
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

#### 추가 기술
- **PWA**: next-pwa, Service Worker, IndexedDB
- **실시간**: WebSocket 또는 Server-Sent Events
- **캐싱**: Redis (Upstash 무료 플랜)
- **고급 검색**: Elasticsearch (Bonsai) 또는 MeiliSearch
- **상태관리**: Zustand (복잡한 상태 시 도입)

#### 추가 기능
- [x] PWA 지원 (오프라인 모드, 앱 설치)
- [x] 실시간 알림 및 업데이트
- [x] 고급 검색 (태그, 필터)
- [x] 노트 버전 관리
- [x] 미디어 파일 업로드 및 관리

**예상 비용**: 월 $20-50
**포트폴리오 어필**: "PWA 구현", "Redis 캐싱", "실시간 기능", "오프라인 지원"

### Phase 3: 고급 기능 및 자동화 (2-3개월)
**목표**: 운영 효율성과 팀 협업 지원

#### 추가 기술
- **메시지 큐**: Redis + Bull Queue (작업 큐)
- **모니터링**: Sentry (에러), Vercel Analytics
- **CI/CD**: GitHub Actions
- **Notion 통합**: Notion API를 통한 문서 동기화
- **배포 자동화**: 서브도메인별 자동 배포

#### 추가 기능
- [x] Notion 동기화 (문서 자동 백업)
- [x] 팀 협업 (권한 관리, 멤버 초대)
- [x] 배포 자동화 및 서브도메인 관리
- [x] 분석 대시보드 (방문자, 사용 통계)
- [x] 감사 로그 및 변경 이력

**예상 비용**: 월 $50-100
**포트폴리오 어필**: "Notion API 통합", "CI/CD 파이프라인", "팀 협업 시스템", "분석 대시보드"

### Phase 4: 스케일업 및 현업 기술 도입 (3-6개월)
**목표**: 포트폴리오 어필을 위한 엔터프라이즈급 기술 경험

#### 고급 기술 도입 (선택적)
- **마이크로서비스**: Auth, Portfolio, Notification 서비스 분리
- **메시지 브로커**: Apache Kafka (Confluent Cloud) 또는 RabbitMQ
- **컨테이너**: Docker, Docker Compose (개발환경)
- **오케스트레이션**: Kubernetes (로컬 minikube)
- **모니터링**: Prometheus + Grafana (로컬 구성)
- **API Gateway**: Kong 또는 Traefik

#### 엔터프라이즈 기능
- [x] 서비스 분리 및 마이크로서비스 아키텍처 경험
- [x] 이벤트 드리븐 아키텍처 (Kafka/RabbitMQ)
- [x] 컨테이너화 및 오케스트레이션 학습
- [x] 분산 모니터링 및 로깅
- [x] API Gateway를 통한 라우팅

**예상 비용**: 월 $100-200 (또는 로컬 환경으로 비용 절약)
**포트폴리오 어필**: "마이크로서비스 아키텍처", "Kafka 이벤트 스트리밍", "Kubernetes 경험", "모니터링 시스템"

## 품질 및 보안 체크리스트

- **입력 검증**: Zod 또는 class-validator로 DTO 검증
- **권한 검사**: 모든 API 엔드포인트에 역할 기반 접근 제어
- **미디어 보안**: 서명된 URL, 만료 정책 적용
- **성능 최적화**: N+1 쿼리 방지, 인덱스 설계, 캐싱 전략
- **에러 처리**: 구조화된 에러 응답, 로깅 시스템

## 테스트 전략

- 도메인 로직 단위 테스트
- API 엔드포인트 통합 테스트
- 내보내기 기능 E2E 테스트
- 외부 서비스 모킹

## 환경 변수 설정

```
DATABASE_URL=         # 데이터베이스 연결
AUTH_PROVIDER=        # 인증 제공자
STORAGE_BUCKET=       # 미디어 스토리지
EXTERNAL_API_KEYS=    # 외부 서비스 API 키
```

## 빠른 시작

1. **사전 준비**
   - Node.js >= 20, pnpm
   - Python 3.11+, pip/uv
   - Docker, Docker Compose

2. **설치**
   ```bash
   # 프론트엔드
   cd apps/manager-web && pnpm install
   
   # 백엔드(예시)
   cd ../../apps/portfolio-api && python -m venv .venv && source .venv/bin/activate
   pip install -U pip
   pip install fastapi uvicorn[standard] sqlalchemy pydantic alembic psycopg2-binary
   ```

3. **로컬 인프라 기동**
   ```bash
   docker compose -f infra/compose/docker-compose.yml up -d
   ```

4. **환경 변수**
   ```bash
   # 공통
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/portfolio
   
   # Auth
   AUTH_JWT_SECRET=change-me
   AUTH_COOKIE_DOMAIN=localhost
   
   # Search
   SEARCH_HOST=http://localhost:7700
   SEARCH_API_KEY=masterKey
   ```

5. **개발 서버 실행**
   ```bash
   # 포트폴리오 API
   cd apps/portfolio-api && uvicorn app.main:app --reload --port 8081
   
   # 인증 API  
   cd apps/auth-api && uvicorn app.main:app --reload --port 8082
   
   # 매니저 웹
   cd apps/manager-web && pnpm dev
   ```

## PWA 개발 가이드

### PWA 구현 체크리스트

1. **Service Worker 설정**
   ```javascript
   // next.config.js with next-pwa
   const withPWA = require('next-pwa')({
     dest: 'public',
     register: true,
     skipWaiting: true,
     disable: process.env.NODE_ENV === 'development'
   })
   ```

2. **Manifest 파일**
   - 앱 이름, 아이콘, 테마 색상 정의
   - 디스플레이 모드: standalone 또는 fullscreen
   - 시작 URL 및 범위 설정

3. **오프라인 전략**
   - 캐싱 전략: Cache First (정적 자원), Network First (API)
   - IndexedDB로 노트/프로젝트 로컬 저장
   - Background Sync API로 오프라인 변경사항 동기화

4. **푸시 알림**
   - Web Push API 구현
   - 알림 권한 요청 UX
   - 알림 카테고리: 프로젝트 업데이트, 팀 활동, 배포 상태

5. **성능 최적화**
   - App Shell 패턴 적용
   - 중요 리소스 사전 캐싱
   - 이미지 lazy loading 및 최적화

### Manager Web의 공개/비공개 영역 구조

#### 공개 영역 라우트 (인증 불필요)
- `/` - 홈페이지, 공개 포트폴리오 목록
- `/portfolio/[slug]` - 공개 프로젝트 상세
- `/profile` - 공개 프로필 페이지
- `/search` - 공개 콘텐츠 검색

#### 관리 영역 라우트 (인증 필요)
- `/dashboard` - 프로젝트 관리 대시보드
- `/notes` - 노트 관리 (학습/변경/조사)
- `/projects/new` - 새 프로젝트 생성
- `/projects/[id]/edit` - 프로젝트 편집
- `/projects/[id]/deploy` - 배포 설정
- `/team` - 팀 멤버 관리

### 개별 포트폴리오 사이트 접근 제어

- **공개 프로젝트**: 모든 사용자 접근 가능
- **비공개 프로젝트**: SSO 인증 후 권한 확인
- **제한적 공개**: 링크를 아는 사람만 접근 (선택적)

## 확장된 기술 스택 개발 가이드

### 마이크로서비스 아키텍처
- **Kong/Traefik**: API 게이트웨이로 라우팅, 인증, 레이트 리미팅
- **GraphQL Federation**: 여러 서비스를 하나의 GraphQL 엔드포인트로 통합
- **서비스 분리**: Auth, Portfolio, Notification, Analytics 독립 배포

### 이벤트 드리븐 아키텍처
```javascript
// Kafka 이벤트 발행 예시
await kafka.producer.send({
  topic: 'portfolio-events',
  messages: [{
    key: 'project.created',
    value: JSON.stringify({ projectId, userId, timestamp })
  }]
})
```

### 캐싱 전략
- **Redis 레이어**:
  - L1: 세션 스토어 (TTL: 30분)
  - L2: API 응답 캐시 (TTL: 5분)
  - L3: 정적 데이터 캐시 (TTL: 1시간)
- **Redis Pub/Sub**: 실시간 알림, WebSocket 브로드캐스트

### 데이터베이스 전략
- **PostgreSQL**: 트랜잭션 데이터 (User, Project, Note)
- **MongoDB**: 유연한 스키마 (노트 콘텐츠, 미디어 메타데이터)
- **Elasticsearch**: 전문 검색, 로그 분석
- **TimescaleDB**: 시계열 데이터 (방문 통계, 성능 메트릭)

### 모니터링 스택
- **Prometheus + Grafana**: 시스템 메트릭, 커스텀 대시보드
- **ELK Stack**: 중앙 집중식 로깅, 로그 분석
- **Jaeger**: 분산 트레이싱, 성능 병목 분석

### Kubernetes 배포
```yaml
# 예시: HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: portfolio-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: portfolio-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 상태 관리 (Zustand)
```typescript
// Zustand store 예시
const usePortfolioStore = create((set) => ({
  projects: [],
  notes: [],
  addProject: (project) => set((state) => ({
    projects: [...state.projects, project]
  })),
  syncWithServer: async () => {
    // Kafka/WebSocket 실시간 동기화
  }
}))
```

## Notion MCP 통합 가이드

### 문서 관리 자동화
- **기술 문서**: API 명세, 아키텍처 결정 기록 (ADR)
- **프로젝트 문서**: 요구사항 정의서, 설계 문서, 회고록
- **운영 문서**: 배포 가이드, 트러블슈팅 가이드, SOP
- **지식 베이스**: 학습 노트, 기술 리서치, 베스트 프랙티스

### Notion 동기화 워크플로우
1. 프로젝트 생성 시 자동으로 Notion 페이지 생성
2. 노트 작성 시 Notion 데이터베이스에 백업
3. 주간/월간 리포트 자동 생성 및 Notion 업로드
4. 팀 위키와 실시간 동기화

### 현업 문서 템플릿
- **PRD (Product Requirements Document)**
- **TDD (Technical Design Document)**
- **API Documentation (OpenAPI 기반)**
- **Post-mortem Report**
- **Sprint Planning & Retrospective**
- **Change Log & Release Notes**

## PostgreSQL 사용 이유

MySQL 대신 PostgreSQL을 사용하는 이유:

1. **JSONB 타입**: 노트 콘텐츠, 메타데이터를 유연하게 저장하면서도 인덱싱과 쿼리 지원
2. **전문 검색**: 내장 full-text search 기능으로 기본 검색 구현 가능
3. **배열 타입**: 태그 배열을 네이티브로 저장하고 쿼리 가능
4. **윈도우 함수**: 분석 대시보드용 고급 집계 쿼리 지원
5. **확장성**: PostGIS(지리정보), TimescaleDB(시계열) 등 확장 모듈 풍부
6. **트랜잭션**: ACID 특성이 MySQL보다 엄격하여 데이터 무결성 보장

## 프로젝트 구조 및 배포

- **폴더 구조**: `portfolio/portfolio-manager/`에서 개발
- **다른 프로젝트**: `portfolio/` 폴더에 별도 프로젝트들 위치
- **Docker Compose**: 개발 환경용은 `infra/compose/` 내에 위치
- **서브도메인 전략**: `*.portfolio.example.com` 와일드카드 DNS → Traefik 라우팅

## 파일명 수정 제안

`READMD.md`는 `README.md`로 변경하는 것을 권장합니다:
```bash
mv READMD.md README.md
```

## 🤖 MCP 서버 및 서브에이전트 활용 가이드

### 사용 가능한 MCP 서버 (.mcp.json 설정)

이 프로젝트는 다음 MCP 서버들을 활용하여 개발 효율성을 극대화합니다:

#### 핵심 MCP 서버
- **sequential-thinking**: 복잡한 마이크로서비스 아키텍처 분석, 4단계 로드맵 실행 계획
- **notion**: PRD, TDD, API 문서, 회고록 자동 생성 및 동기화  
- **upstash-context-7-mcp**: Next.js 14, FastAPI, Kubernetes 최신 문서 조회
- **playwright**: PWA E2E 테스트, 성능 측정, 크로스 브라우저 테스트
- **github**: 멀티 서비스 코드 관리, PR 리뷰, Phase별 이슈 트래킹
- **docker-mcp**: PostgreSQL, Redis, Elasticsearch 컨테이너 관리
- **memory**: 프로젝트 컨텍스트 및 아키텍처 결정 이력 보존

#### Phase별 MCP 활용 전략
```yaml
Phase 1 (MVP): filesystem, upstash-context-7-mcp, notion
Phase 2 (PWA): playwright, brave-search, sequential-thinking  
Phase 3 (자동화): github, docker-mcp, notion
Phase 4 (엔터프라이즈): sequential-thinking, memory, docker-mcp
```

### SuperClaude 서브에이전트 시스템

#### 전문 페르소나 에이전트 (11개)

**아키텍처 & 설계**:
- `--persona-architect`: 시스템 아키텍처, 마이크로서비스 설계, 확장성
- `--persona-analyzer`: 근본 원인 분석, 증거 기반 조사, 체계적 분석

**개발 전문가**:
- `--persona-frontend`: UI/UX, PWA, 반응형 디자인 (Magic MCP 연동)
- `--persona-backend`: API 개발, 데이터베이스, 마이크로서비스 (Context7 연동)
- `--persona-security`: 보안 분석, 취약점 평가, 준수성 (Sequential 연동)

**품질 & 최적화**:
- `--persona-performance`: 최적화, 병목 분석 (Playwright 연동)
- `--persona-qa`: 테스트 전략, E2E 테스트 (Playwright 연동)  
- `--persona-refactorer`: 코드 품질, 기술 부채 관리

**운영 & 문서화**:
- `--persona-devops`: 인프라, K8s 배포, 모니터링 (Docker MCP 연동)
- `--persona-mentor`: 교육적 설명, 지식 전달 (Context7 연동)
- `--persona-scribe=ko`: 한국어 전문 문서화 (Notion 연동)

#### 자동 활성화 시나리오

**마이크로서비스 아키텍처 설계**:
```bash
# "마이크로서비스 설계" 키워드 감지 → 자동 활성화
→ --persona-architect + --seq + --ultrathink
→ MCP: Sequential(주요) + Context7(패턴)
```

**PWA 구현**:
```bash  
# "PWA", "오프라인" 키워드 감지 → 자동 활성화
→ --persona-frontend + --magic + --c7
→ MCP: Magic(주요) + Context7(문서) + Playwright(테스트)
```

**보안 강화**:
```bash
# "보안", "취약점" 키워드 감지 → 자동 활성화  
→ --persona-security + --validate + --think-hard
→ MCP: Sequential(분석) + Context7(패턴)
```

#### Wave 오케스트레이션 활용

**복잡한 시스템 개선** (자동 Wave 모드):
```bash
# 복잡도 >0.8 + 파일 >20 + 작업 유형 >2 감지
→ --wave-mode auto --systematic-waves
→ 1단계: Analyzer (현상 분석)
→ 2단계: Architect (설계)
→ 3단계: 전문 에이전트들 (구현)
→ 4단계: QA (검증)
→ 5단계: Performance (최적화)
```

**대규모 작업 위임**:
```bash
# 파일 >50개 또는 디렉토리 >7개 감지
→ --delegate auto --concurrency 5
→ Task 에이전트가 병렬 처리 조정
```

### 실제 사용 예시

#### 1. 프로젝트 초기 설정
```bash
/load @portfolio-manager --wave-mode auto
# 자동 활성화: Architect + Security + 전체 시스템 분석
```

#### 2. Next.js PWA 구현  
```bash
/implement "PWA 오프라인 모드" --persona-frontend
# MCP: Magic(컴포넌트) + Context7(PWA 문서) + Playwright(테스트)
```

#### 3. FastAPI 마이크로서비스 개발
```bash
/build "인증 서비스" --persona-backend --persona-security  
# MCP: Context7(FastAPI 문서) + Sequential(아키텍처)
```

#### 4. Kubernetes 배포
```bash
/deploy "k8s 환경" --persona-devops --validate
# MCP: Docker(컨테이너) + Context7(K8s 문서)
```

#### 5. 포괄적 시스템 분석
```bash
/analyze --comprehensive --delegate auto
# Wave 모드: 모든 전문 에이전트 + Task 위임 + 체계적 분석
```

### 개발 워크플로우 통합

1. **계획 수립**: Architect + Sequential → 시스템 설계
2. **구현**: Frontend/Backend 페르소나 + 각 MCP 서버 연동
3. **테스트**: QA + Playwright → E2E 테스트 자동화  
4. **배포**: DevOps + Docker MCP → 컨테이너화 및 K8s 배포
5. **문서화**: Scribe + Notion MCP → 자동 문서 생성/동기화
6. **유지보수**: Memory MCP → 컨텍스트 보존 및 지속적 학습

## 🚀 바로 사용할 수 있는 액션 템플릿

### 프로젝트 시작 템플릿

```bash
# 1. 프로젝트 초기 분석 및 설정
/load @portfolio-manager --wave-mode auto --persona-architect
# → 전체 시스템 이해, 아키텍처 분석, 개발 계획 수립

# 2. Phase별 구현 시작
/implement "Phase 1 MVP: 프로젝트 CRUD" --persona-backend --validate
# → FastAPI 또는 Next.js API Routes 구현

# 3. 프론트엔드 UI 구현  
/build "좌측 탭 기반 노트 시스템" --persona-frontend --magic
# → React 컴포넌트, shadcn/ui, Tailwind 구현

# 4. 데이터베이스 스키마 설계
/design "PostgreSQL 스키마" --persona-backend --think
# → ERD, 마이그레이션, 인덱스 설계
```

### 기능별 구현 템플릿

#### 인증 시스템
```bash
/implement "NextAuth.js 소셜 로그인" --persona-security --validate
# → Google/GitHub OAuth, JWT, 세션 관리
```

#### PWA 기능
```bash
/implement "Service Worker 오프라인 모드" --persona-frontend --play
# → PWA 매니페스트, 캐싱 전략, IndexedDB
```

#### 검색 기능
```bash
/build "PostgreSQL 전문 검색" --persona-backend --think
# → GIN 인덱스, tsvector, 검색 최적화
```

#### API 문서화
```bash
/document "REST API 스펙" --persona-scribe=ko --c7
# → OpenAPI 스펙, 자동 문서 생성
```

### 문제 해결 템플릿

```bash
# 성능 문제 분석
/analyze "응답 속도 저하" --persona-performance --play --think-hard
# → 병목 지점 식별, 최적화 방안 제시

# 보안 취약점 점검
/troubleshoot "보안 검토" --persona-security --validate --ultrathink
# → OWASP 체크리스트, 취약점 스캔

# 코드 품질 개선
/improve --quality --persona-refactorer --loop
# → 코드 리팩토링, 기술 부채 해결
```

### Wave 오케스트레이션 템플릿

```bash
# 대규모 시스템 개선
/improve "전체 시스템 최적화" --wave-mode systematic --delegate auto
# → 1단계: 분석 → 2단계: 설계 → 3단계: 구현 → 4단계: 검증

# 포괄적 코드 검토
/analyze --comprehensive --wave-mode progressive --concurrency 5
# → 멀티 에이전트 병렬 분석, 점진적 개선
```

## 🤖 AI 협업을 자동화 시스템 수준으로 끌어올리기

### 1. 컨텍스트 자동 보존 전략

```bash
# 매 세션마다 컨텍스트 로드
/load @portfolio-manager --memory
# → Memory MCP가 이전 작업 내용, 아키텍처 결정, 코딩 스타일 기억

# 주요 의사결정 자동 기록
/document "아키텍처 결정 기록" --persona-scribe=ko --notion
# → ADR(Architecture Decision Record) 자동 생성 및 Notion 동기화
```

### 2. 품질 게이트 자동화

```bash
# 코드 작성 시 자동 검증 체인
/implement [기능명] --validate --persona-qa --loop
# → 구현 → 테스트 → 리팩토링 → 문서화 자동 사이클

# 배포 전 자동 체크리스트
/test --comprehensive --persona-qa --play
# → 단위/통합/E2E 테스트 + 성능 + 보안 검증
```

### 3. 학습 피드백 루프 구축

```yaml
자동_학습_사이클:
  1. 구현: "MCP 서버 활용해서 최신 패턴으로 구현"
  2. 검증: "QA 페르소나로 코드 품질 자동 검토"
  3. 문서화: "Notion MCP로 학습 내용 자동 정리"
  4. 피드백: "Memory MCP로 개선점 다음 세션에 반영"
```

### 4. 전문가 시뮬레이션 환경

```bash
# 코드 리뷰 시뮬레이션
/analyze "코드 리뷰" --persona-senior --persona-security --persona-performance
# → 시니어 개발자 관점의 다각도 검토

# 아키텍처 리뷰 위원회 시뮬레이션
/design "시스템 아키텍처" --wave-mode systematic
# → 아키텍트 + 보안 전문가 + 성능 전문가 협업
```

### 5. 자동화된 워크플로우 패턴

```yaml
일일_개발_루틴:
  morning:
    - "/load @portfolio-manager --memory"  # 컨텍스트 복원
    - "오늘 할 일 우선순위 정리"
  
  development:
    - "/implement [기능] --validate --loop"  # 품질 보장 구현
    - 자동 테스트 + 문서화
  
  evening:
    - "/document '오늘 학습 내용' --notion"  # 학습 정리
    - "/analyze '개선점' --memory"  # 피드백 저장

주간_회고_자동화:
  - "/analyze '이번 주 성과' --persona-mentor --notion"
  - "다음 주 개선 계획 수립 및 기록"
  - "기술 학습 로드맵 업데이트"
```

### 6. 지능형 에러 예방 시스템

```bash
# 잠재적 문제 사전 감지
/analyze "잠재적 기술 부채" --persona-architect --think-hard
# → 현재 구조에서 발생할 수 있는 문제점 미리 식별

# 보안 취약점 사전 점검
/troubleshoot "보안 체크" --persona-security --validate --schedule=weekly
# → 정기적 보안 점검 루틴 구축
```

### 7. 성과 측정 및 개선

```yaml
ai_협업_kpi:
  개발_속도: "기능당 구현 시간 50% 단축"
  코드_품질: "버그 발생률 70% 감소"
  학습_효율: "신기술 습득 시간 60% 단축"
  문서_완성도: "API 문서 자동화 90% 달성"

측정_방법:
  - Memory MCP로 개발 시간 자동 추적
  - QA 페르소나로 품질 지표 자동 측정
  - Notion MCP로 학습 진도 시각화
```

## 현실적 체크리스트 (Phase 1 우선)

### 🎯 MVP 필수 기능 (2-3개월)
- [ ] 도메인 확정 및 스키마 1차안 (Project/Site/Note/Auth/Deployment)
- [ ] 인증 서비스(NextAuth.js) MVP: 회원가입/로그인, 세션 관리
- [ ] 매니저 웹(좌측 내비·탭) MVP: 프로젝트 목록, 노트(학습/변경/조사)
- [ ] 포트폴리오 API: 프로젝트/사이트 CRUD, 배포 메타
- [ ] 기본 검색: PostgreSQL 전문검색으로 시작
- [ ] 반응형 UI 구현 (모바일/태블릿/데스크톱)
- [ ] 배포 환경 구성 (Vercel + Supabase)

### 🚀 점진적 확장 (필요에 의해서만)
- [ ] (Phase 2) PWA 및 고급 검색 구현
- [ ] (Phase 3) Notion API 통합
- [ ] (Phase 4) 마이크로서비스 및 Kafka 도입

### 🤖 AI 협업 자동화 체크리스트
- [ ] Memory MCP로 프로젝트 컨텍스트 보존 설정
- [ ] 기능별 구현 템플릿 활용 (위의 액션 템플릿 참고)
- [ ] 품질 게이트 자동화 (--validate --loop 패턴)
- [ ] Notion MCP로 문서 자동 동기화
- [ ] 정기적 회고 및 개선 루틴 구축