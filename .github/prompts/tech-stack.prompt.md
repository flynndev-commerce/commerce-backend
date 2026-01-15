# Tech Stack & Environment

이 프로젝트의 기술 스택 및 환경 설정 정보입니다.

## 🛠️ Core Stack
- **Language**: Python 3.13+
- **Web Framework**: FastAPI (0.128.0+)
- **ORM**: SQLModel (SQLAlchemy 2.0 Core 기반)
    - **Session**: `sqlmodel.ext.asyncio.session.AsyncSession` 사용 (비동기 필수)
- **Database**:
    - **Production**: PostgreSQL 16+
    - **Test/Dev**: SQLite (aiosqlite)
- **DI Framework**: `dependency-injector`

## 🧪 Testing & Quality
- **Test Runner**: Pytest (v8.0+)
    - `pytest-asyncio`
    - `httpx` (TestClient)
- **Linter/Formatter**: Ruff
- **Type Checker**: Mypy (Strict Mode)
- **Pre-commit**: `.pre-commit-config.yaml` configured

## 📦 Package Management
- **Tool**: Poetry
- **File**: `pyproject.toml`
