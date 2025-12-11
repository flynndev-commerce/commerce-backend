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

# Commerce Backend - Copilot Instructions

## 언어 및 문서화

**모든 코드, 주석, 독스트링, 커밋 메시지는 한글로 작성합니다.** 이는 이 프로젝트의 핵심 규칙입니다.

## 아키텍처 개요

이 프로젝트는 **DDD(도메인 주도 설계) 기반 헥사고날 아키텍처**를 따르는 FastAPI 기반 커머스 서비스입니다.

### 주요 계층 구조

```
app/
├── domain/        # 순수 도메인 모델, 도메인 서비스, 포트(인터페이스)
├── application/   # 애플리케이션 유즈케이스(Use Cases), DTO
├── infrastructure/# 어댑터 (API, 영속성), 영속성 모델
├── core/         # 설정, DB, 보안, 예외 처리 등 공통 유틸리티
└── main.py       # 애플리케이션 진입점 및 구성 루트
```

-   **`app/domain`**: 핵심 비즈니스 로직과 규칙을 담는 계층입니다. `model` (도메인 모델)과 `ports` (리포지토리 인터페이스 등) 하위 디렉토리를 가집니다. 외부 기술에 대한 의존성이 없습니다.
-   **`app/application`**: 애플리케이션의 유즈케이스(Use Case)를 구현하는 계층입니다. `dto` (API 요청/응답 DTO)와 `use_cases` (애플리케이션 서비스) 하위 디렉토리를 가집니다. `domain` 계층의 포트를 사용하여 비즈니스 로직을 오케스트레이션합니다.
-   **`app/infrastructure`**: 외부 세계와의 통신을 담당하는 어댑터들을 포함합니다. `api` (FastAPI 라우터), `persistence` (SQLModel 기반 DB 구현체) 하위 디렉토리를 가집니다. `domain` 계층에 정의된 포트의 구체적인 구현을 제공합니다.
-   **`app/core`**: 로깅, 설정, 의존성 주입 컨테이너(`app/containers.py`), 예외 처리 등 프로젝트 전반에 걸쳐 사용되는 핵심 유틸리티 및 기반 코드를 포함합니다.

### 의존성 주입 (DI)

**dependency-injector**를 사용한 DI 컨테이너(`app/containers.py`)가 모든 의존성을 관리합니다. 새 엔드포인트나 유즈케이스/리포지토리 추가 시 `Container.wiring_config.modules`에 관련 모듈 경로를 등록하고, 컨테이너에 프로바이더를 정의하세요.

## 핵심 규칙

### 모델링

-   **Domain Model (`app/domain/model/`)**: 순수한 비즈니스 도메인을 표현하며, 데이터베이스나 외부 기술에 대한 의존성이 없습니다. (예: `User`, `Product`)
    ```python
    class User(BaseModel):
        id: int | None = Field(default=None, ...)
        email: EmailStr = Field(...)
    ```
-   **Persistence Model (`app/infrastructure/persistence/model/`)**: DB 테이블과 1:1 매핑, 클래스명에 `Entity` 접미사 (예: `UserEntity`, `ProductEntity`). `SQLModel` 상속.
    ```python
    class UserEntity(SQLModel, table=True):
        __tablename__: ClassVar[str] = "user"  # 소문자 단수형
        id: Annotated[int | None, Field(primary_key=True, title="고유 ID", ...)]
    ```
-   **DTO (`app/application/dto/`)**: API 요청/응답을 위한 데이터 전송 객체, `CamelCaseBaseModel` 상속으로 카멜케이스 자동 변환.
    ```python
    class UserCreate(CamelCaseBaseModel):
        full_name: Annotated[str, Field(title="전체 이름", ...)]
    ```
-   **필드 선언**: 항상 `Annotated`와 `Field` 사용, `title`/`description` 한글 명시
    ```python
    # ✅ 올바른 예시
    email: Annotated[str, Field(unique=True, title="이메일", description="...")]
    is_active: Annotated[bool, Field(title="활성 상태", ...)] = True

    # ❌ 잘못된 예시
    is_active: bool = Field(default=True)  # Annotated 누락
    ```

### API 규칙

-   **엔드포인트 경로**: 후행 슬래시(`/`) 없음 (예: `router.post("")`)
-   **라우트 이름**: `app/core/route_names.py`의 `RouteName` StrEnum 사용
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
-   **응답 포맷**: 모든 API는 `BaseResponse[T]` 래핑 (`app/application/dto/response.py`)
-   **예외 처리**: `HTTPException` 발생 시 전역 핸들러(`app/core/exception_handlers.py`)가 자동 처리
-   **의존성 주입**: `Annotated[UseCase, Depends(Provide[Container.use_case])]` 패턴 (예: `Annotated[UserUseCase, Depends(Provide[Container.user_use_case])]`)
-   **API 문서 요약 (Summary)**: 각 API 엔드포인트의 `APIRouter` 데코레이터에 `summary` 파라미터를 사용하여 간결하고 명확한 한글 요약 설명을 추가합니다.

### 코드 스타일

-   **타입 힌트**: 모든 함수에 인자/반환값 타입 명시 (mypy strict 모드)
-   **모던 문법**: `X | None` (not `Optional[X]`), `list` (not `List`), PEP 695 제네릭
-   **Self 참조**: `typing_extensions.Self` 사용
-   **Line length**: 120자

### 커밋 메시지

[Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 준수:

-   `feat`: 새 기능 (사용자 영향)
-   `fix`: 버그 수정 (사용자 영향)
-   `refactor`: 내부 구조 개선 (사용자 무영향)
-   `docs`: 문서 변경

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
poetry run ruff check app && poetry run black --check app && poetry run mypy -p app && poetry run mypy tests
```

자동 수정:

```bash
poetry run ruff check app --fix && poetry run black app
```

### 새 도메인/엔드포인트 추가 체크리스트

새로운 도메인 엔티티와 관련 API를 추가할 때 다음 단계를 따릅니다.

1.  **도메인 모델 정의**: `app/domain/model/{domain_name}.py`에 순수 도메인 모델 생성. (예: `Product`)
2.  **리포지토리 포트 정의**: `app/domain/ports/{domain_name}_repository.py`에 `I{DomainName}Repository` 인터페이스 생성.
3.  **영속성 엔티티 정의**: `app/infrastructure/persistence/models/{domain_name}_entity.py`에 `SQLModel` 기반 `*Entity` 모델 생성. (`__tablename__` 명시)
4.  **DTO 정의**: `app/application/dto/{domain_name}_dto.py`에 `CamelCaseBaseModel` 상속받는 `*Create`, `*Read`, `*Update` DTO 생성.
5.  **리포지토리 구현**: `app/infrastructure/persistence/{domain_name}_repository.py`에 `SQL{DomainName}Repository` 구현체 생성.
6.  **유즈케이스 구현**: `app/application/use_cases/{domain_name}_use_case.py`에 `ProductUseCase`와 같은 애플리케이션 유즈케이스 클래스 구현.
7.  **라우트 이름 추가**: `app/core/route_names.py`의 `RouteName` StrEnum에 관련 라우트 이름 추가.
8.  **API 라우터 구현**: `app/infrastructure/api/v1/{domain_name}s.py`에 `APIRouter`를 사용하여 엔드포인트 구현. (`@inject` 데코레이터, `name=RouteName.*` 설정, `summary` 추가)
9.  **DI 컨테이너 업데이트**: `app/containers.py`에 리포지토리 및 유즈케이스 프로바이더 등록 및 API 모듈 wiring 추가.
10. **메인 라우터에 포함**: `app/infrastructure/api/v1/__init__.py`에 새로운 라우터 포함.
11. **코드 검사 및 테스트**: 모든 검사(ruff, black, mypy) 통과 확인 및 관련 단위/통합 테스트 작성.

## 설정 관리

-   모든 설정은 `app/core/config.py`의 `Settings` 클래스에 소문자 속성으로 정의
-   `.env` 파일로 재정의 가능 (pydantic-settings 사용)
-   `get_settings()` 함수로 싱글톤 접근

## 테스트 작성 규칙

### 테스트 구조

-   **테스트 파일**: `tests/v1/test_*.py` (API 버전별로 구분)
-   **Fixture**: `tests/conftest.py`에 공통 fixture 정의
-   **테스트 클래스**: 기능별로 그룹화 (예: `TestUserCreate`, `TestUserLogin`, `TestProductCreate`)

### 테스트 베스트 프랙티스

1.  **URL은 RouteName 사용**:
    ```python
    # ✅ 올바른 예시
    url = test_app.url_path_for(RouteName.USERS_CREATE_USER)
    
    # ❌ 잘못된 예시
    url = "/api/v1/users"  # 하드코딩 금지
    ```

2.  **응답은 Pydantic 모델로 검증**:
    ```python
    # ✅ 올바른 예시
    response_model = BaseResponse[UserRead].model_validate(response.json())
    assert response_model.code == "OK"
    assert response_model.result.email == "test@example.com"
    
    # ❌ 잘못된 예시
    data = response.json()
    assert data["code"] == "OK"  # dict 직접 접근
    ```

3.  **테스트 데이터는 상수화**:
    ```python
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "password123"
    TEST_USER_FULL_NAME = "Test User"
    ```

4.  **헬퍼 함수로 중복 제거**:
    ```python
    def create_test_user(test_app: FastAPI, client: TestClient) -> UserRead:
        """테스트용 사용자 생성 (idempotent)"""
        # 이미 존재하면 조회, 없으면 생성
    ```

5.  **Status Code는 starlette.status 상수 사용**:
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

-   **비동기 SQLite**: `aiosqlite` 드라이버 사용, 모든 DB 작업은 `async/await`
-   **DB 초기화**: `app.main.py`의 `lifespan` 컨텍스트에서 자동 테이블 생성
-   **JWT 인증**: `app/core/security.py`에 토큰 생성/검증 유틸리티 있음
-   **테스트 DB**: 각 테스트마다 인메모리 SQLite 사용, 테스트 간 격리 보장


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
