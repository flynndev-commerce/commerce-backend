# Gemini 프로젝트 컨텍스트

이 문서는 Gemini와 다른 개발자들이 프로젝트를 더 잘 이해할 수 있도록 프로젝트 설정 및 규칙에 대한 컨텍스트를 제공합니다.

## 프로젝트 개요

이 프로젝트는 간단한 커머스 서비스를 만들어 보는 토이 프로젝트입니다.

## 프로젝트 설정

-   **Python 버전 관리**: 이 프로젝트는 `asdf`를 사용하여 Python 버전을 관리합니다. 특정 버전은 `.tool-versions` 파일에 정의되어 있습니다. (`3.13.7`)
-   **의존성 관리**: 의존성은 `Poetry`로 관리됩니다. 의존성 목록은 `pyproject.toml` 파일에 있습니다.
-   **소스 코드**: 주요 애플리케이션 코드는 `app` 디렉토리 내에 레이어드 아키텍처를 따라 구성됩니다.

## 개발 규칙

### 커밋 스타일

이 프로젝트는 커밋 메시지에 대해 [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 명세를 따릅니다.

### 코드 스타일 및 품질

-   **Linter**: `ruff`
-   **Formatter**: `black`
-   **Type Checker**: `mypy`
-   **Line Length**: 120자

모든 코드는 다음 명령을 실행하여 검사를 통과해야 합니다:
```bash
poetry run ruff check app && poetry run black --check app && poetry run mypy -p app
```

### 설정 관리

-   애플리케이션 설정은 `pydantic-settings`를 통해 관리됩니다.
-   설정 파일은 `app/core/config.py`에 위치합니다.
-   프로젝트 루트의 `.env` 파일을 통해 설정을 재정의할 수 있습니다.

## 실행 방법

-   **애플리케이션 실행**:
    ```bash
    poetry run uvicorn app.main:app --reload
    ```

## 언어 및 스타일

-   모든 응답, 문서, 주석은 한글로 작성합니다.
