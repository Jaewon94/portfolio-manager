# Portfolio Manager Backend Tests

이 디렉토리는 Portfolio Manager 백엔드의 테스트 코드를 포함합니다. 테스트는 유형별로 체계적으로 구성되어 있습니다.

## 📁 테스트 구조

```
tests/
├── conftest.py              # 공통 fixtures 및 설정
├── pytest.ini              # pytest 설정 (루트에 위치)
├── README.md               # 이 파일
│
├── unit/                   # 단위 테스트
│   ├── test_models.py      # SQLAlchemy 모델 테스트
│   └── test_schemas.py     # Pydantic 스키마 테스트
│
├── integration/            # 통합 테스트
│   └── test_media_service.py  # 미디어 서비스 통합 테스트
│
├── api/                    # API 테스트
│   ├── test_auth_endpoints.py     # 인증 API 테스트
│   ├── test_media_endpoints.py    # 미디어 API 테스트
│   └── test_project_endpoints.py  # 프로젝트 API 테스트
│
└── e2e/                    # E2E 테스트
    └── test_complete_workflows.py # 전체 워크플로우 테스트
```

## 🧪 테스트 유형별 설명

### Unit Tests (단위 테스트)

- **목적**: 개별 함수/클래스의 로직 검증
- **특징**: 빠른 실행, 외부 의존성 없음 (Mock 사용)
- **실행 시간**: 매우 빠름 (< 1초)
- **실행 명령**: `pytest tests/unit/ -m unit`

**예시**:

- 모델 생성/검증 테스트
- 스키마 직렬화/역직렬화 테스트
- 유틸리티 함수 테스트

### Integration Tests (통합 테스트)

- **목적**: 여러 컴포넌트 간의 상호작용 검증
- **특징**: 실제 DB 사용, 서비스 간 연동 테스트
- **실행 시간**: 보통 (1-10초)
- **실행 명령**: `pytest tests/integration/ -m integration`

**예시**:

- 서비스 레이어와 데이터베이스 연동
- 파일 시스템과의 상호작용
- 외부 API 연동 (Mock 또는 Test API 사용)

### API Tests (API 테스트)

- **목적**: HTTP 엔드포인트 검증
- **특징**: FastAPI TestClient 사용, HTTP 요청/응답 검증
- **실행 시간**: 보통 (1-5초)
- **실행 명령**: `pytest tests/api/ -m api`

**예시**:

- REST API 엔드포인트 테스트
- 인증/권한 검증
- 요청/응답 형식 검증

### E2E Tests (종단간 테스트)

- **목적**: 전체 워크플로우 검증
- **특징**: 실제 사용자 시나리오 시뮬레이션
- **실행 시간**: 느림 (10초 이상)
- **실행 명령**: `pytest tests/e2e/ -m e2e`

**예시**:

- 사용자 로그인 → 프로젝트 생성 → 미디어 업로드 → 공개
- 협업 워크플로우
- 에러 복구 시나리오

## 🚀 테스트 실행 방법

### 전체 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 유형만 실행
pytest -m unit          # 단위 테스트만
pytest -m integration   # 통합 테스트만
pytest -m api          # API 테스트만
pytest -m e2e          # E2E 테스트만

# 느린 테스트 제외
pytest -m "not slow"

# 특정 기능 테스트만
pytest -m auth         # 인증 관련 테스트만
pytest -m media        # 미디어 관련 테스트만
pytest -m project      # 프로젝트 관련 테스트만
```

### 개발 중 권장 실행 순서

```bash
# 1. 빠른 단위 테스트로 기본 로직 검증
pytest tests/unit/ -v

# 2. 통합 테스트로 컴포넌트 연동 확인
pytest tests/integration/ -v

# 3. API 테스트로 엔드포인트 검증
pytest tests/api/ -v

# 4. 최종적으로 E2E 테스트 (시간이 있을 때)
pytest tests/e2e/ -v
```

### 특정 파일/테스트 실행

```bash
# 특정 파일 실행
pytest tests/unit/test_models.py -v

# 특정 클래스 실행
pytest tests/api/test_auth_endpoints.py::TestAuthEndpoints -v

# 특정 메서드 실행
pytest tests/api/test_auth_endpoints.py::TestAuthEndpoints::test_github_oauth_login_url -v
```

## 🛠️ 테스트 환경 설정

### 필수 환경 변수

테스트 실행 전에 다음 환경 변수들이 설정되어 있어야 합니다:

```bash
# .env.test 파일에 설정
ENVIRONMENT=test
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost/portfolio_manager_test
SECRET_KEY=test-secret-key
GITHUB_CLIENT_ID=test-client-id
GITHUB_CLIENT_SECRET=test-client-secret
```

### 테스트 데이터베이스 설정

```bash
# PostgreSQL 테스트 데이터베이스 생성
createdb portfolio_manager_test

# 또는 Docker 사용
docker run -d \\
  --name portfolio-test-db \\
  -e POSTGRES_DB=portfolio_manager_test \\
  -e POSTGRES_USER=test \\
  -e POSTGRES_PASSWORD=test \\
  -p 5433:5432 \\
  postgres:15
```

## 📊 테스트 커버리지

테스트 커버리지를 확인하려면:

```bash
# 커버리지와 함께 테스트 실행
pytest --cov=app --cov-report=html --cov-report=term-missing

# HTML 리포트 확인
open htmlcov/index.html
```

목표 커버리지:

- **Unit Tests**: 95% 이상
- **Integration Tests**: 80% 이상
- **API Tests**: 90% 이상
- **전체**: 85% 이상

## 🔧 테스트 작성 가이드라인

### 1. 네이밍 컨벤션

```python
# 파일명: test_[모듈명].py
# 클래스명: Test[기능명]
# 메서드명: test_[기능]_[상황]

class TestUserModel:
    def test_create_user_success(self):
        pass

    def test_create_user_invalid_email(self):
        pass
```

### 2. 테스트 구조 (AAA 패턴)

```python
def test_example():
    # Arrange (준비)
    user_data = {"email": "test@example.com"}

    # Act (실행)
    user = create_user(user_data)

    # Assert (검증)
    assert user.email == "test@example.com"
```

### 3. Fixtures 활용

```python
# conftest.py에 정의된 fixtures 활용
def test_with_fixtures(test_db, test_user, authenticated_client):
    # test_db: 테스트 데이터베이스 세션
    # test_user: 테스트용 사용자
    # authenticated_client: 인증된 HTTP 클라이언트
    pass
```

### 4. 마커 사용

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_function():
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_slow_integration():
    pass
```

## 🐛 테스트 디버깅

### 로그 출력

```bash
# 상세한 출력
pytest -v -s

# 로그 레벨 설정
pytest --log-cli-level=DEBUG
```

### 실패한 테스트만 재실행

```bash
# 마지막 실패한 테스트만
pytest --lf

# 실패한 테스트부터 다시 시작
pytest --ff
```

### 특정 에러 타입만 중단

```bash
# 첫 번째 실패에서 중단
pytest -x

# N번 실패 후 중단
pytest --maxfail=3
```

## 📝 테스트 추가 시 체크리스트

새로운 테스트를 추가할 때 확인사항:

- [ ] 적절한 테스트 유형 선택 (unit/integration/api/e2e)
- [ ] 적절한 마커 추가 (`@pytest.mark.unit` 등)
- [ ] 필요한 fixtures 사용
- [ ] AAA 패턴 준수
- [ ] 에러 케이스 포함
- [ ] 의미있는 테스트명 사용
- [ ] 테스트 독립성 보장 (다른 테스트에 영향 없음)

## 🔍 CI/CD 통합

GitHub Actions에서 테스트 실행:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          # 빠른 테스트부터 실행
          pytest tests/unit/ -v
          pytest tests/integration/ -v  
          pytest tests/api/ -v
          # E2E는 선택적으로
          pytest tests/e2e/ -v -m "not slow"
```

## 📚 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI 테스팅](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy 테스팅](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Pydantic 테스팅](https://docs.pydantic.dev/latest/usage/validation_decorator/#testing)
