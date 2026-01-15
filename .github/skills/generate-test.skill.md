# Generate Test Skill

## 설명 (Description)
작성된 코드에 대해 **테스트 피라미드 전략**에 맞는 테스트 코드를 생성하는 스킬입니다.
DB 연결 유무에 따라 **Pure Domain Test** 또는 **Use Case Test (with Fakes)** 를 생성합니다.

## 입력 (Inputs)
- **target_file**: 테스트 대상 파일 경로 (Domain Model 또는 UseCase)
- **test_type**: `domain` (순수) 또는 `usecase` (Fake 사용)

## 출력 (Outputs)

### Case 1: Pure Domain Test (Default for Entities)
- **Condition**: 입력 파일이 `domain/model`에 위치한 경우.
- **Path**: `tests/unit/domain/test_{name}.py`
- **Content**:
    - **No Mock**: `unittest.mock` import 금지.
    - 순수 객체 생성 → 메서드 호출 → 상태 검증 Flow.

### Case 2: Use Case Test (Default for UseCases)
- **Condition**: 입력 파일이 `application/use_cases`에 위치한 경우.
- **Path**: `tests/unit/application/test_{name}_use_case.py`
- **Dependency**:
    - `tests/fakes/repositories/fake_{name}_repository.py` 사용 (없으면 생성).
    - `pytest.fixture`를 통해 Fake Repository가 주입된 UseCase 인스턴스 제공.
- **Content**:
    - **No Mocking Repositories**: 리포지토리를 Mocking 하지 말고 반드시 Fake 객체를 사용하세요.
    - 비즈니스 로직 성공/실패 시나리오 검증.

## 예시 프롬프트 (Example Prompt)
> "Order 엔티티에 대한 순수 도메인 테스트를 만들어줘."
> "OrderUseCase에 대해 Fake Repository를 사용한 테스트를 만들어줘."
