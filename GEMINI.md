# Gemini 프로젝트 컨텍스트

이 문서는 Gemini와 다른 개발자들이 프로젝트를 더 잘 이해할 수 있도록 프로젝트 설정 및 규칙에 대한 컨텍스트를 제공합니다.

## 프로젝트 개요

이 프로젝트는 간단한 커머스 서비스를 만들어 보는 토이 프로젝트입니다.

## 프로젝트 설정

-   **Python 버전 관리**: 이 프로젝트는 `asdf`를 사용하여 Python 버전을 관리합니다. 특정 버전은 `.tool-versions` 파일에 정의되어 있습니다. (`3.13.7`)
-   **의존성 관리**: 의존성은 `Poetry`로 관리됩니다. 의존성 목록은 `pyproject.toml` 파일에 있습니다.
-   **소스 코드**: 주요 애플리케이션 코드는 `app` 디렉토리 내에 `domain`, `repositories`, `services`, `api`, `schemas` 등의 계층형 아키텍처를 따라 구성됩니다.
-   **주요 라이브러리**:
    -   웹 프레임워크: `FastAPI`
    -   데이터베이스 ORM: `SQLModel`
    -   데이터 검증: `Pydantic` (`email-validator` 포함)
    -   의존성 주입: `dependency-injector`
    -   설정 관리: `pydantic-settings`
    -   비밀번호 해싱: `bcrypt`

## 개발 규칙

### 언어 및 스타일

-   **모든 코드, 주석, 독스트링, 커밋 메시지, 문서 등 프로젝트의 모든 텍스트는 한글로 작성하는 것을 원칙으로 합니다.**

### 커밋 스타일

-   이 프로젝트는 커밋 메시지에 대해 [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 명세를 따릅니다.
-   **커밋 타입 지정 시 `feat`, `fix`, `refactor`의 의미를 명확히 구분하여 사용해야 합니다.** 특히, 단순 코드 리팩토링이나 내부 구조 개선은 `refactor`, 사용자에게 영향을 주는 버그 수정은 `fix`, 새로운 기능 추가는 `feat`으로 지정하는 것에 주의합니다. (사용자 피드백 2025-10-08)

### 모델링 규칙

-   **Domain vs. Schema 분리**:
    -   `app/domain`: 데이터베이스 테이블 구조와 일대일로 매칭되는 핵심 모델을 정의합니다. 이 모델은 모든 필드를 명시적으로 포함하여, 해당 파일만으로 모델의 전체 구조를 파악할 수 있어야 합니다.
    -   `app/schemas`: API의 요청(Request) 및 응답(Response) 데이터 전송 객체(DTO)를 정의합니다. `pydantic.BaseModel`을 상속받아 데이터베이스 기술로부터 독립성을 유지합니다.
-   **DB 모델 명명 규칙**:
    -   `app/domain`의 데이터베이스 테이블 모델 클래스는 `Entity` 접미사를 사용합니다. (예: `UserEntity`)
    -   클래스 내부에서 `__tablename__` 속성을 명시하여, 실제 데이터베이스 테이블 이름은 소문자 단수형을 유지합니다. (예: `__tablename__: ClassVar[str] = "user"`)
-   **필드 선언 스타일**:
    -   모든 모델의 필드는 `typing.Annotated`를 사용하여 타입과 메타데이터(`Field`)를 명확하게 분리합니다. (예: `email: Annotated[str, Field(...)]`)
    -   모든 필드에는 `title`과 `description`을 한글로 명시하여 가독성과 문서화를 향상시킵니다.
-   **데이터 검증**:
    -   사용자 입력값에 대한 검증(이메일 형식, 비밀번호 길이 등)은 `app/schemas` 레이어에서 `Pydantic`의 기능을 사용하여 처리합니다.

### API 스타일 규칙

-   **엔드포인트 경로**: 모든 API 엔드포인트 경로는 후행 슬래시(`/`)로 끝나지 않도록 작성합니다. (예: `router.post("")`)

### 코드 스타일 및 품질

-   **Linter**: `ruff`
-   **Formatter**: `black`
-   **Type Checker**: `mypy` (`strict` 모드 활성화)
-   **Line Length**: 120자

모든 코드는 다음 명령을 실행하여 검사를 통과해야 합니다:
```bash
poetry run ruff check app && poetry run black --check app && poetry run mypy -p app
```

#### 세부 코드 스타일 규칙

항상 다음 규칙을 준수하여 코드를 작성하고 검토해야 합니다.

-   **`mypy: no-untyped-def`**: 모든 함수의 인자와 반환 값에는 반드시 타입 힌트를 명시해야 합니다. (`strict = true` 설정으로 강제됩니다.)
-   **`ruff: B008`**: FastAPI 의존성 주입 시에는 `Annotated` 타입을 사용하여 이 규칙을 준수합니다. (예: `Annotated[UserService, Depends(...)]`)
-   **`ruff: UP035`**: 클래스 자신을 타입 힌트로 사용할 때는 `typing_extensions.Self`를 사용합니다.
-   **`ruff: UP045`**: `typing.List` 대신 내장 타입 `list`를 사용합니다.
-   **`ruff: W292`**: 모든 파일의 끝에는 개행 문자가 있어야 합니다.

### 설정 관리

-   애플리케이션 설정은 `pydantic-settings`를 통해 관리됩니다.
-   설정 파일은 `app/core/config.py`에 위치하며, 모든 속성명은 소문자로 작성합니다.
-   프로젝트 루트의 `.env` 파일을 통해 설정을 재정의할 수 있습니다.

## 실행 방법

-   **애플리케이션 실행**:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
