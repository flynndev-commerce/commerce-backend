# Scaffold API Skill

## 설명 (Description)
FastAPI 라우터와 관련 설정을 생성하여 외부에서 접근 가능한 API 엔드포인트를 구축하는 스킬입니다.

## 입력 (Inputs)
- **domain_name**: 도메인 이름
- **endpoints**: 생성할 엔드포인트 목록 (Method, Path)

## 출력 (Outputs)

1. `app/core/route_names.py` (수정)
    - 새로운 `RouteName` 상수 추가 (StrEnum)

2. `app/infrastructure/api/v1/{snake_case_name}.py`
    - `APIRouter` 생성 (prefix, tags 설정)
    - `Use Case` 주입 (`Depends(Provide[...])`)
    - 응답 모델 `BaseResponse[T]` 사용

3. `app/infrastructure/api/v1/__init__.py` (수정)
    - 메인 라우터에 `include_router` 추가

4. `app/containers.py` (수정)
    - `wiring_config`에 모듈 경로 추가

## 예시 프롬프트 (Example Prompt)
> "Coupon API 라우터를 만들어줘. 발급(POST), 조회(GET) 기능이 있어."
