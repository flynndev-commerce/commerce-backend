# Gemini 프로젝트 컨텍스트

이 문서는 Gemini와 다른 개발자들이 프로젝트를 더 잘 이해할 수 있도록 프로젝트 설정 및 규칙에 대한 컨텍스트를 제공합니다.

## 프로젝트 개요

이 프로젝트는 간단한 커머스 서비스를 만들어 보는 토이 프로젝트입니다. 사용자(User)와 상품(Product) 도메인 기능을 구현하고 있습니다.

## 프로젝트 설정

-   **Python 버전 관리**: 이 프로젝트는 `asdf`를 사용하여 Python 버전을 관리합니다. 특정 버전은 `.tool-versions` 파일에 정의되어 있습니다. (`3.13.7`)
-   **의존성 관리**: 의존성은 `Poetry`로 관리됩니다. 의존성 목록은 `pyproject.toml` 파일에 있습니다. (`greenlet` 라이브러리 추가됨)
-   **소스 코드**: 주요 애플리케이션 코드는 `app` 디렉토리 내에 DDD(도메인 주도 설계)와 헥사고날 아키텍처를 따라 구성됩니다.
    -   `app/domain`: 애플리케이션의 핵심 비즈니스 로직과 규칙을 포함하며, 다른 계층에 대한 의존성이 없는 순수한 도메인 모델, 서비스, 포트(인터페이스)를 정의합니다. (예: `User`, `Product` 도메인 모델 및 관련 리포지토리 인터페이스)
    -   `app/application`: 애플리케이션의 사용 사례(Use Cases)를 구현합니다. `domain` 계층의 포트를 사용하여 비즈니스 로직을 오케스트레이션하고, `infrastructure` 계층의 구현에 의존하지 않습니다. API 요청/응답을 위한 DTO(데이터 전송 객체)도 이 계층에서 정의하며, 유즈케이스 클래스명은 `UserUseCase`, `ProductUseCase`와 같이 명명합니다.
    -   `app/infrastructure`: 외부 세계와의 통신을 담당하는 어댑터들을 포함합니다. 예를 들어, FastAPI를 사용한 웹 API(Driving Adapter), SQLModel을 사용한 데이터베이스 연동(Driven Adapter) 등이 이 계층에 속합니다. `domain`에 정의된 포트의 구체적인 구현을 제공합니다.
    -   `app/core`: 로깅, 설정, 의존성 주입 컨테이너 등 프로젝트 전반에 걸쳐 사용되는 핵심 유틸리티 및 기반 코드를 포함합니다.
-   **주요 라이브러리**:
    -   웹 프레임워크: `FastAPI`
    -   데이터베이스 ORM: `SQLModel` (비동기 지원)
    -   비동기 SQLite 드라이버: `aiosqlite`
    -   데이터 검증: `Pydantic` (`email-validator` 포함)
    -   의존성 주입: `dependency-injector`
    -   설정 관리: `pydantic-settings`
    -   비밀번호 해싱: `bcrypt`
    -   비동기 코드 실행: `greenlet` (SQLAlchemy async와의 호환성)

## 개발 규칙

### 언어 및 스타일

-   **모든 코드, 주석, 독스트링, 커밋 메시지, 문서 등 프로젝트의 모든 텍스트는 한글로 작성하는 것을 원칙으로 합니다.**

### 커밋 스타일

-   이 프로젝트는 커밋 메시지에 대해 [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 명세를 따릅니다.
-   **커밋 타입 지정 시 `feat`, `fix`, `refactor`의 의미를 명확히 구분하여 사용해야 합니다.** 특히, 단순 코드 리팩토링이나 내부 구조 개선은 `refactor`, 사용자에게 영향을 주는 버그 수정은 `fix`, 새로운 기능 추가는 `feat`으로 지정하는 것에 주의합니다. (사용자 피드백 2025-10-08)

### 모델링 규칙

-   **헥사고날 아키텍처 기반 모델링 규칙**:
    -   **계층별 모델 분리**:
        -   `app/domain/model`: 순수한 비즈니스 도메인을 표현하는 핵심 모델입니다. 데이터베이스나 외부 기술에 대한 어떠한 의존성도 갖지 않아야 합니다. 비즈니스 로직은 이 모델 내에 메서드로 포함됩니다.
        -   `app/application/dto`: 애플리케이션 유즈케이스(Use Case)의 입력 및 출력을 위한 데이터 전송 객체(DTO)를 정의합니다. Pydantic의 `BaseModel`을 상속하여 데이터 유효성 검사를 수행하며 API의 Request/Response 스키마로 사용됩니다.
        -   `app/infrastructure/persistence/model`: 데이터베이스 테이블 구조와 매핑되는 영속성 모델을 정의합니다. `SQLModel`을 상속받으며, 테이블 이름, 컬럼 정보 등 데이터베이스에 특화된 설정을 포함합니다.
-   **DB 모델 명명 규칙**:
    -   `app/infrastructure/persistence/model`의 데이터베이스 테이블 모델 클래스는 `Entity` 접미사를 사용합니다. (예: `UserEntity`, `ProductEntity`)
    -   클래스 내부에서 `__tablename__` 속성을 명시하여, 실제 데이터베이스 테이블 이름은 소문자 단수형을 유지합니다. (예: `__tablename__: ClassVar[str] = "user"`)
-   **필드 선언 스타일**:
    -   모든 모델의 필드는 `typing.Annotated`를 사용하여 타입과 메타데이터(`Field`)를 명확하게 분리합니다. (예: `email: Annotated[str, Field(...)]`)
    -   기본값이 있는 필드의 경우, `Field` 내부에 `default=` 키워드 인자를 사용하지 않고, 필드 선언 끝에 직접 기본값을 할당합니다. (예: `field_name: Annotated[str, Field(title="...")] = "기본값"`)
    -   모든 필드에는 `title`과 `description`을 한글로 명시하여 가독성과 문서화를 향상시킵니다.
-   **데이터 검증**:
    -   사용자 입력값에 대한 검증(이메일 형식, 비밀번호 길이 등)은 `app/application/dto` 레이어에서 `Pydantic`의 기능을 사용하여 처리합니다.
-   **API 필드 명명 규칙 (카멜케이스)**:
    -   모든 API 요청(Request) 및 응답(Response) DTO 필드는 카멜케이스(camelCase)를 사용합니다. 이를 위해 `pydantic.BaseModel`을 상속받는 기본 DTO 모델에 `model_config`를 통해 자동 변환을 처리합니다. 도메인 및 영속성 모델은 스네이크 케이스(snake_case)를 유지합니다.

### API 스타일 규칙

-   **엔드포인트 경로**: 모든 API 엔드포인트 경로는 후행 슬래시(`/`)로 끝나지 않도록 작성합니다. (예: `router.post("")`)
-   **API 문서 요약 (Summary)**: 각 API 엔드포인트의 `APIRouter` 데코레이터에 `summary` 파라미터를 사용하여 간결하고 명확한 한글 요약 설명을 추가합니다. 이는 OpenAPI(Swagger UI) 문서의 가독성을 크게 향상시킵니다.

### API 예외 처리

-   **전역 예외 처리**: 모든 API 엔드포인트의 예외 처리는 `app/main.py`에 정의된 전역 예외 핸들러를 통해 `BaseResponse` 포맷으로 통일하여 반환합니다.
-   `HTTPException`과 일반 `Exception`을 구분하여 처리하며, `mypy` 호환성을 위해 `typing.cast`를 사용할 수 있습니다.

### 코드 스타일 및 품질

-   **Linter**: `ruff`
-   **Formatter**: `black`
-   **Type Checker**: `mypy` (`strict` 모드 활성화)
    -   **`py.typed` 파일**: MyPy가 패키지를 타입 힌트가 있는 것으로 인식하도록 각 파이썬 패키지 디렉토리(`app/domain`, `app/application` 등)에 비어있는 `py.typed` 파일을 포함합니다.
-   **Pre-commit**: 커밋 시 자동으로 Linter와 Formatter를 실행합니다.
    -   설치 명령어: `poetry run pre-commit install`
-   **Line Length**: 120자

모든 코드는 다음 명령을 실행하여 검사를 통과해야 합니다:
```bash
poetry run ruff check app && poetry run black --check app && poetry run mypy -p app
```

#### 세부 코드 스타일 규칙

항상 다음 규칙을 준수하여 코드를 작성하고 검토해야 합니다.

-   **`mypy: no-untyped-def`**: 모든 함수의 인자와 반환 값에는 반드시 타입 힌트를 명시해야 합니다. (`strict = true` 설정으로 강제됩니다.)
-   **`ruff: B008`**: FastAPI 의존성 주입 시에는 `Annotated` 타입을 사용하여 이 규칙을 준수합니다. (예: `Annotated[UserUseCase, Depends(...)]`)
-   **`ruff: UP035`**: 클래스 자신을 타입 힌트로 사용할 때는 `typing_extensions.Self`를 사용합니다.
-   **`ruff: UP045`**: `typing.List` 대신 내장 타입 `list`를 사용합니다.
-   **`ruff: UP007`**: `typing.Optional[X]` 대신 `X | None` 문법을 사용합니다. (Python 3.10+)
-   **`PEP 695`**: 제네릭 타입 선언 시 `class MyClass[T]:`와 같은 새로운 문법을 사용합니다. (Python 3.12+)
-   **`W292`**: 모든 파일의 끝에는 개행 문자가 있어야 합니다.

### 설정 관리

-   애플리케이션 설정은 `pydantic-settings`를 통해 관리됩니다.
-   설정 파일은 `app/core/config.py`에 위치하며, 모든 속성명은 소문자로 작성합니다.
-   프로젝트 루트의 `.env` 파일을 통해 설정을 재정의할 수 있습니다.

## 실행 방법

-   **애플리케이션 실행**:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
