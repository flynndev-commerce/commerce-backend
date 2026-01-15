# Commerce Backend - Copilot Instructions

이 프로젝트는 **DDD 기반 헥사고날 아키텍처**를 따르는 커머스 서비스입니다.
엄격한 코드 품질과 아키텍처 원칙 준수를 위해, 다음 **Prompt Files**에 정의된 규칙을 반드시 따르세요.

## 📚 참조 문서 (Reference Prompts)

작업 컨텍스트에 따라 아래 프롬프트 파일의 내용을 준수해야 합니다.

- **기술 스택**: `.github/prompts/tech-stack.prompt.md`
- **코딩 컨벤션**: `.github/prompts/conventions.prompt.md`
- **아키텍처 원칙**: `.github/prompts/architecture.prompt.md`

## 🤖 에이전트 협업 (Agents)

복잡한 작업은 역할에 맞는 에이전트를 호출하여 수행하세요.

| 에이전트 | 역할 | 주요 책임 |
| :--- | :--- | :--- |
| **@tech-lead** | Tech Lead | 요구사항 분석, 기술 스펙 작성, 작업 위임 |
| **@domain-expert** | Domain Expert | [순수] 도메인 모델, 유즈케이스, DTO 구현 |
| **@data-engineer** | Data Engineer | DB(RDB/NoSQL), 메시징 인프라 구현 |
| **@api-dev**| API Developer | API, Event Consumer 구현 및 스펙 관리 |
| **@security-engineer**| Security | 인증/인가(OAuth), 암호화, 보안 정책 |
| **@devops-engineer** | DevOps/QA | 테스트(TDD), CI/CD, Docker 인프라 |

## 🚀 워크플로우 요약

1.  **언어**: 모든 코드의 주석, 문서, 커밋 메시지는 **한국어**로 작성합니다.
2.  **테스트**: 기능 구현 시 반드시 `tests/`에 테스트 코드를 포함해야 합니다. (FakeRepo 우선)
3.  **검증**: 코드 변경 후 `poetry run ruff check app` 및 `mypy` 통과 필수.
4.  **Git/PR**: 모든 작업은 Feature Branch에서 수행하며, PR 작성 시 **"Why"**가 포함된 기술적 의사결정 내용을 상세히 기술해야 합니다.
