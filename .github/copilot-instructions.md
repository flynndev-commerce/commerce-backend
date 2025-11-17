# Commerce Backend - Copilot Instructions

## 언어 및 문서화

**모든 코드, 주석, 독스트링, 커밋 메시지는 한글로 작성합니다.** 이는 이 프로젝트의 핵심 규칙입니다.

## 아키텍처 개요

이 프로젝트는 **계층형 아키텍처**를 따르는 FastAPI 기반 커머스 서비스입니다:

```
app/
├── domain/        # DB 테이블 모델 (SQLModel, Entity 접미사)
├── repositories/  # DB 접근 레이어
├── services/      # 비즈니스 로직
├── api/          # API 엔드포인트 (v1, v2 버전 관리)
├── schemas/      # API DTO (Pydantic, 카멜케이스)
└── core/         # 설정, DB, 보안, 예외 처리
```

**dependency-injector**를 사용한 DI 컨테이너(`app/containers.py`)가 모든 의존성을 관리합니다. 새 엔드포인트 추가 시 `Container.wiring_config.modules`에 모듈 경로를 등록하세요.

## 핵심 규칙

### 모델링

- **Domain (`app/domain/`)**: DB 테이블과 1:1 매핑, 클래스명에 `Entity` 접미사 (예: `UserEntity`)
  ```python
  class UserEntity(SQLModel, table=True):
      __tablename__: ClassVar[str] = "user"  # 소문자 단수형
      id: Annotated[int | None, Field(primary_key=True, title="고유 ID", ...)]
  ```
- **Schemas (`app/schemas/`)**: API DTO, `CamelCaseBaseModel` 상속으로 카멜케이스 자동 변환

  ```python
  class UserCreate(CamelCaseBaseModel):
      full_name: Annotated[str, Field(title="전체 이름", ...)]
  ```

- **필드 선언**: 항상 `Annotated`와 `Field` 사용, `title`/`description` 한글 명시

  ```python
  # ✅ 올바른 예시
  email: Annotated[str, Field(unique=True, title="이메일", description="...")]
  is_active: Annotated[bool, Field(title="활성 상태", ...)] = True

  # ❌ 잘못된 예시
  is_active: bool = Field(default=True)  # Annotated 누락
  ```

### API 규칙

- **엔드포인트 경로**: 후행 슬래시(`/`) 없음 (예: `router.post("")`)
- **라우트 이름**: `app/core/route_names.py`의 `RouteName` StrEnum 사용
  ```python
  # RouteName 정의
  class RouteName(StrEnum):
      USERS_CREATE_USER = "users:create-user"
      USERS_LOGIN = "users:login"
  
  # 라우터에서 사용
  @router.post("", name=RouteName.USERS_CREATE_USER)
  
  # 테스트에서 사용
  url = test_app.url_path_for(RouteName.USERS_CREATE_USER)
  ```
- **응답 포맷**: 모든 API는 `BaseResponse[T]` 래핑 (`app/schemas/response.py`)
- **예외 처리**: `HTTPException` 발생 시 전역 핸들러(`app/core/exception_handlers.py`)가 자동 처리
- **의존성 주입**: `Annotated[Service, Depends(Provide[Container.service])]` 패턴

### 코드 스타일

- **타입 힌트**: 모든 함수에 인자/반환값 타입 명시 (mypy strict 모드)
- **모던 문법**: `X | None` (not `Optional[X]`), `list` (not `List`), PEP 695 제네릭
- **Self 참조**: `typing_extensions.Self` 사용
- **Line length**: 120자

### 커밋 메시지

[Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 준수:

- `feat`: 새 기능 (사용자 영향)
- `fix`: 버그 수정 (사용자 영향)
- `refactor`: 내부 구조 개선 (사용자 무영향)

## 필수 워크플로우

### 개발 환경

```bash
# Python 버전 설치 (asdf 사용)
asdf install

# 의존성 설치
poetry install

# 서버 실행
poetry run uvicorn app.main:app --reload
```

### 코드 검사

**반드시 모든 변경사항은 다음 검사를 통과해야 합니다:**

```bash
poetry run ruff check app && poetry run black --check app && poetry run mypy -p app
```

자동 수정:

```bash
poetry run ruff check app --fix && poetry run black app
```

### 새 엔드포인트 추가 체크리스트

1. `app/domain/`에 `*Entity` 모델 생성 (`__tablename__` 명시)
2. `app/schemas/`에 DTO 생성 (`CamelCaseBaseModel` 상속)
3. `app/repositories/`에 DB 접근 레이어 구현
4. `app/services/`에 비즈니스 로직 구현
5. `app/core/route_names.py`에 라우트 이름 추가 (StrEnum)
6. `app/api/v1/`에 라우터 구현 (`@inject` 데코레이터, `name=RouteName.*` 설정)
7. `app/containers.py`에 서비스/리포지토리 등록 및 wiring 추가
8. 코드 검사 통과 확인

## 설정 관리

- 모든 설정은 `app/core/config.py`의 `Settings` 클래스에 소문자 속성으로 정의
- `.env` 파일로 재정의 가능 (pydantic-settings 사용)
- `get_settings()` 함수로 싱글톤 접근

## 테스트 작성 규칙

### 테스트 구조

- **테스트 파일**: `tests/v1/test_*.py` (API 버전별로 구분)
- **Fixture**: `tests/conftest.py`에 공통 fixture 정의
- **테스트 클래스**: 기능별로 그룹화 (예: `TestUserCreate`, `TestUserLogin`)

### 테스트 베스트 프랙티스

1. **URL은 RouteName 사용**:
   ```python
   # ✅ 올바른 예시
   url = test_app.url_path_for(RouteName.USERS_CREATE_USER)
   
   # ❌ 잘못된 예시
   url = "/api/v1/users"  # 하드코딩 금지
   ```

2. **응답은 Pydantic 모델로 검증**:
   ```python
   # ✅ 올바른 예시
   response_model = BaseResponse[UserRead].model_validate(response.json())
   assert response_model.code == "OK"
   assert response_model.result.email == "test@example.com"
   
   # ❌ 잘못된 예시
   data = response.json()
   assert data["code"] == "OK"  # dict 직접 접근
   ```

3. **테스트 데이터는 상수화**:
   ```python
   TEST_USER_EMAIL = "test@example.com"
   TEST_USER_PASSWORD = "password123"
   TEST_USER_FULL_NAME = "Test User"
   ```

4. **헬퍼 함수로 중복 제거**:
   ```python
   def create_test_user(test_app: FastAPI, client: TestClient) -> UserRead:
       """테스트용 사용자 생성 (idempotent)"""
       # 이미 존재하면 조회, 없으면 생성
   ```

5. **Status Code는 starlette.status 상수 사용**:
   ```python
   assert response.status_code == status.HTTP_201_CREATED
   assert response.status_code == status.HTTP_400_BAD_REQUEST
   ```

### 테스트 실행

```bash
# 전체 테스트
poetry run pytest tests/ -v

# 특정 파일
poetry run pytest tests/v1/test_users.py -v

# 특정 테스트
poetry run pytest tests/v1/test_users.py::TestUserCreate::test_create_user_success -v
```

## 특이사항

- **비동기 SQLite**: `aiosqlite` 드라이버 사용, 모든 DB 작업은 `async/await`
- **DB 초기화**: `app.main.py`의 `lifespan` 컨텍스트에서 자동 테이블 생성
- **JWT 인증**: `app/core/security.py`에 토큰 생성/검증 유틸리티 있음
- **테스트 DB**: 각 테스트마다 인메모리 SQLite 사용, 테스트 간 격리 보장
