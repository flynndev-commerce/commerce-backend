# Hexagonal Architecture & DDD

이 프로젝트의 아키텍처 원칙과 계층 구조 정의입니다.

## 🏗️ Layered Structure

```
app/
├── domain/        # [순수] 비즈니스 로직, 엔티티, 포트 (외부 의존성 0%)
│   ├── model/     # 엔티티 (Pydantic Only)
│   └── ports/     # 리포지토리 인터페이스 (ABC)
├── application/   # [조율] 애플리케이션 서비스
│   ├── use_cases/ # 비즈니스 흐름 구현
│   └── dto/       # 데이터 전송 객체
├── infrastructure/# [구현] 외부 어댑터
│   ├── api/       # Web Adapter (FastAPI)
│   └── persistence/# DB Adapter (SQLModel)
└── core/          # [공통] 설정, 유틸리티, DI
```

## 🚫 Dependency Rules (Strict)

1.  **단방향 의존성**: `Infrastructure` -> `Application` -> `Domain`
    - Domain 계층은 다른 어떤 계층도 import 해서는 안 됩니다.
    - Application 계층은 Domain 계층만 import 할 수 있습니다.
2.  **Domain Purity**:
    - `app/domain` 내부 파일에서는 `sqlalchemy`, `fastapi`, `sqlmodel` 등의 인프라 라이브러리를 임포트하면 안 됩니다.
    - 오직 Python 표준 라이브러리와 `pydantic`만 허용됩니다.
3.  **Ports & Adapters**:
    - Application 계층은 `app/domain/ports`에 정의된 인터페이스(Port)에만 의존해야 합니다.
    - 실제 구현체(Adapter)는 `app/infrastructure`에 위치하며, 런타임에 DI 컨테이너에 의해 주입됩니다.

## 💾 Persistence Pattern
- **Mapping**: 도메인 모델(`app/domain/model`)과 영속성 엔티티(`app/infrastructure/persistence/models`)는 분리되어야 합니다.
- **Conversion**: 리포지토리 구현체에서 `to_domain()` / `from_domain()` 메서드를 통해 변환을 수행합니다.

## 🧪 Testing Strategy (Pyramid)
이 프로젝트는 **엄격한 테스트 피라미드** 전략을 따릅니다.
**Unit Test(Pure/UseCase)**에서는 **절대로 DB에 연결하거나 Mock을 남용해서는 안 됩니다.**

### 1. Pure Domain Tests (Unit) - `tests/unit/domain/`
- **대상**: `app/domain/model` 내의 엔티티 및 VO.
- **원칙**:
    - **No DB**: 데이터베이스 연결 금지.
    - **No Mock**: `unittest.mock` 사용 지양. 순수 객체 생성만 허용.
- **목표**: 비즈니스 불변식(Invariant)과 도메인 로직 검증.
- **속도**: 매우 빠름 (<1ms).

### 2. Use Case Tests (Unit with Fakes) - `tests/unit/application/`
- **대상**: `app/application/use_cases`.
- **원칙**:
    - **Fake Repository 필수**: `unittest.mock` 대신 `tests/fakes/`의 In-Memory Repository를 사용해야 합니다.
    - **No DB**: 데이터베이스 연결 금지.
- **목표**: 애플리케이션 흐름 제어, 예외 처리, 포트 호출 검증.

### 3. Integration Tests - `tests/integration/`
- **대상**: `app/infrastructure` (Repository, API Endpoint).
- **원칙**:
    - 실제 DB(SQLite/PostgreSQL) 연결 허용.
    - `TestClient`를 사용한 E2E 테스트.
- **목표**: SQL 쿼리 정확성, 외부 어댑터 연동 검증.
