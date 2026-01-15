# Create UseCase Skill

## 설명 (Description)
비즈니스 로직을 처리하는 유즈케이스(Use Case)와 관련 DTO를 생성하고, DI 컨테이너에 등록하는 스킬입니다.

## 입력 (Inputs)
- **domain_name**: 대상 도메인 이름
- **action**: 수행할 동작 (예: `IssueCoupon`, `CancelOrder`)

## 출력 (Outputs)

1. `app/application/dto/{snake_case_name}_dto.py`
    - 요청(Request)/응답(Response) DTO 생성
    - `CamelCaseBaseModel` 상속
    - 유효성 검사 로직 포함

2. `app/application/use_cases/{snake_case_name}_use_case.py`
    - `I{Domain}Repository` 주입 (생성자 주입)
    - `@transactional` 데코레이터 고려 (필요 시)
    - 비즈니스 로직 흐름 구현

3. `app/containers.py` (수정)
    - `use_cases` 프로바이더에 신규 유즈케이스 등록
    - `Factory` 패턴 사용

## 예시 프롬프트 (Example Prompt)
> "Coupon 발급(Issue) 기능을 위한 유즈케이스를 만들어줘."
