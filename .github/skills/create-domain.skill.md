# Create Domain Skill

## 설명 (Description)
새로운 도메인 모델과 리포지토리 포트(Interface)를 생성하는 스킬입니다.
이 스킬은 외부 의존성이 전혀 없는 **순수 도메인 계층** 코드를 생성합니다.

## 입력 (Inputs)
- **domain_name**: 도메인 이름 (예: `Coupons`, `Review`)
- **attributes**: 도메인 속성 목록 (선택 사항)

## 출력 (Outputs)
다음 두 파일이 생성되어야 합니다:

1. `app/domain/model/{snake_case_name}.py`
    - Pydantic `BaseModel` 상속
    - `ConfigDict(from_attributes=True)` 설정
    - 필드에 `Annotated`, `Field`, 한글 `title`/`description` 사용

2. `app/domain/ports/{snake_case_name}_repository.py`
    - `abc.ABC` 상속
    - `Async` 메서드 정의 (`save`, `get_by_id` 등 기본 메서드 포함)
    - `typing.Protocol` 대신 `abc.ABC` 사용 (프로젝트 컨벤션)

## 예시 프롬프트 (Example Prompt)
> "Coupon 도메인을 만들어줘. code, discount_amount, valid_until 필드가 필요해."
