# Coding Conventions

이 프로젝트의 코드 작성 규칙 및 컨벤션입니다.

## 📝 Language & Naming
- **언어**: Python
- **네이밍**:
    - 변수/함수: `snake_case` (e.g., `user_id`, `get_product`)
    - 클래스: `PascalCase` (e.g., `UserUseCase`, `ProductEntity`)
    - 상수: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **문서화 (Documentation)**:
    - **모든 주석, Docstring, 커밋 메시지는 한국어로 작성합니다.**
    - 함수/클래스의 역할, 인자, 반환값을 명확히 설명하세요.

## 🛡️ Type Hinting (Must)
- **Strict Mode**: 모든 함수 시그니처에 타입 힌트를 필수적으로 작성해야 합니다.
- **Rules**:
    - `Optional[T]` 대신 `T | None` 사용 (Python 3.10+)
    - `List[T]`, `Dict[K, V]` 대신 `list[T]`, `dict[K, V]` 사용 (PEP 585)
    - 반환값이 없으면 `-> None` 명시

## 🏗️ Pydantic Usage
- **Version**: Pydantic V2
- **Config**: `model_config = ConfigDict(from_attributes=True)` (ORM Mode)
- **Field**: `Annotated[T, Field(..., title="...", description="...")]` 패턴 사용.
- **DTO**: `app/application/dto/base.py`의 `CamelCaseBaseModel` 상속 필수.

## ⚠️ Error Handling
- **Custom Exception**: `app/domain/exceptions.py`에 정의된 비즈니스 예외 사용.
- **No Try-Catch**: 비즈니스 로직(UseCase)에서는 예외를 잡지 않고 전파(Populate)합니다.
- **Global Handler**: `app/core/exception_handlers.py`에서 일괄 처리합니다.

## 🐙 Git Workflow & PR Policy
기능 구현 시 반드시 다음 워크플로우를 준수하세요.

### 1. Branching Strategy
- **Master Branch**: `main` (배포 가능한 안정 상태)
- **Feature Branch**: `feat/<issue-id>-<description>` (새로운 기능)
    - 예: `feat/user-login`, `feat/cart-add-item`
- **Fix Branch**: `fix/<issue-id>-<description>` (버그 수정)
- **Chore Branch**: `chore/<description>` (설정, 문서, 리팩토링)

### 2. Pull Request (PR) Requirements
PR 작성 시 다음 내용을 반드시 포함하여 **'왜(Why)'**를 설명해야 합니다. 단순한 변경 내역 나열은 지양합니다.

- **Objective (목적)**: 무엇을 왜 변경했는가?
- **Technical Decisions (기술적 의사결정)**:
    - 왜 이 라이브러리/구조를 선택했는가?
    - 고려했던 대안(Alternatives)은 무엇이며, 왜 선택하지 않았는가?
    - Trade-off 분석 (장점 vs 단점)
- **Tests**: 수행한 테스트 종류와 결과.
