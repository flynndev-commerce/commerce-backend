# 간단한 커머스 서비스 (Simple Commerce Service)

이것은 간단한 커머스 서비스를 만들어보는 토이 프로젝트입니다.

## 기술 스택

-   **언어**: Python 3.13.7
-   **프레임워크**: FastAPI
-   **데이터베이스 ORM**: SQLModel (비동기 지원)
-   **비동기 SQLite 드라이버**: aiosqlite
-   **데이터 검증**: Pydantic, email-validator
-   **의존성 주입**: dependency-injector
-   **설정**: pydantic-settings
-   **비밀번호 해싱**: bcrypt
-   **테스트**: Pytest
-   **정적 분석**: Ruff, Mypy, Black
-   **버전 관리**: asdf
-   **의존성 관리**: Poetry

## 시작하기

### 요구사항

-   [asdf](https://asdf-vm.com/)
-   [Poetry](https://python-poetry.org/)

### 설치 및 실행

1.  **저장소 클론**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Python 버전 설치**:
    `.tool-versions` 파일에 명시된 Python 버전을 설치합니다.
    ```bash
    asdf install
    ```

3.  **의존성 설치**:
    Poetry를 사용하여 프로젝트 의존성을 설치합니다.
    ```bash
    poetry install
    ```

4.  **서버 실행**:
    FastAPI 개발 서버를 실행합니다.
    ```bash
    poetry run uvicorn app.main:app --reload
    ```
    서버는 `http://127.0.0.1:8000`에서 실행됩니다.

## API

모든 API 요청 및 응답 필드는 카멜케이스(camelCase)를 사용합니다.

### 사용자 (Users)

-   **사용자 생성**
    -   `POST /api/v1/users/`
    -   새로운 사용자를 생성합니다.
        - **요청 본문**:
            ```json
            {
              "email": "user@example.com",
              "password": "string",
              "fullName": "string"
            }
            ```
        -   **예시 (`curl`)**:
            ```bash
            curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
            -H "Content-Type: application/json" \
            -d '{"email": "test@example.com", "password": "password123", "fullName": "Test User"}'
            ```

## 개발

### 설정

-   애플리케이션 설정은 `pydantic-settings`를 통해 관리됩니다.
-   프로젝트 루트에 `.env` 파일을 생성하여 설정을 재정의할 수 있습니다. (`.env.example` 파일 참고)

### 코드 스타일 및 품질 검사

모든 코드는 다음 명령을 실행하여 검사를 통과해야 합니다.

-   **전체 검사 실행**:
    ```bash
    poetry run ruff check app && poetry run black --check app && poetry run mypy -p app
    ```
-   **자동 수정**:
    ```bash
    poetry run ruff check app --fix && poetry run black app
    ```

### 테스트

프로젝트의 단위 테스트를 실행하려면 다음 명령어를 사용하세요.

```bash
poetry run pytest
```
