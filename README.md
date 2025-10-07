# 간단한 커머스 서비스 (Simple Commerce Service)

이것은 간단한 커머스 서비스를 만들어보는 토이 프로젝트입니다.

## 기술 스택

-   **언어**: Python 3.13.7
-   **프레임워크**: FastAPI
-   **의존성 주입**: dependency-injector
-   **테스트**: Pytest
-   **정적 분석**: Ruff, Mypy, Black
-   **버전 관리**: asdf
-   **의존성 관리**: Poetry

## 시작하기

### 요구사항

-   [asdf](https://asdf-vm.com/)
-   [Poetry](https://python-poetry.org/)

### 설치

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
    poetry run uvicorn main:app --reload
    ```
    (참고: `main.py` 파일과 `app` 인스턴스를 생성해야 합니다.)

## 테스트

프로젝트의 테스트를 실행하려면 다음 명령어를 사용하세요.

```bash
poetry run pytest
```
