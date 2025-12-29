from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName

# 테스트 데이터 상수
TEST_PRODUCT_NAME = "테스트 상품"
TEST_PRODUCT_DESCRIPTION = "테스트 상품 설명입니다."
TEST_PRODUCT_PRICE = 10000.0
TEST_PRODUCT_STOCK = 100
TEST_PRODUCT_INVALID_PRICE = -1000.0
TEST_PRODUCT_INVALID_STOCK = -1


def create_test_product(test_app: FastAPI, client: TestClient) -> ProductRead:
    """테스트용 상품을 생성하고 ProductRead 모델을 반환하는 헬퍼 함수"""
    response = client.post(
        test_app.url_path_for(RouteName.PRODUCTS_CREATE),
        json={
            "name": TEST_PRODUCT_NAME,
            "description": TEST_PRODUCT_DESCRIPTION,
            "price": TEST_PRODUCT_PRICE,
            "stock": TEST_PRODUCT_STOCK,
        },
    )
    response_model = BaseResponse[ProductRead].model_validate(response.json())
    return response_model.result


class TestProductCreate:
    """상품 생성 테스트"""

    def test_create_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 생성 성공 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            json={
                "name": TEST_PRODUCT_NAME,
                "description": TEST_PRODUCT_DESCRIPTION,
                "price": TEST_PRODUCT_PRICE,
                "stock": TEST_PRODUCT_STOCK,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.name == TEST_PRODUCT_NAME
        assert response_model.result.description == TEST_PRODUCT_DESCRIPTION
        assert response_model.result.price == TEST_PRODUCT_PRICE
        assert response_model.result.stock == TEST_PRODUCT_STOCK
        assert response_model.result.id is not None

    def test_create_product_invalid_price(self, test_app: FastAPI, client: TestClient) -> None:
        """유효하지 않은 가격으로 상품 생성 실패 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            json={
                "name": TEST_PRODUCT_NAME,
                "price": TEST_PRODUCT_INVALID_PRICE,  # 잘못된 가격
                "stock": TEST_PRODUCT_STOCK,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_invalid_stock(self, test_app: FastAPI, client: TestClient) -> None:
        """유효하지 않은 재고로 상품 생성 실패 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            json={
                "name": TEST_PRODUCT_NAME,
                "price": TEST_PRODUCT_PRICE,
                "stock": TEST_PRODUCT_INVALID_STOCK,  # 잘못된 재고
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProductList:
    """상품 목록 조회 테스트"""

    def test_list_products_empty(self, test_app: FastAPI, client: TestClient) -> None:
        """빈 상품 목록 조회 테스트"""
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert response_model.code == "OK"
        assert len(response_model.result) == 0

    def test_list_products_with_data(self, test_app: FastAPI, client: TestClient) -> None:
        """데이터가 있는 상품 목록 조회 테스트"""
        # 상품 2개 생성
        create_test_product(test_app, client)
        client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            json={
                "name": "두 번째 상품",
                "price": 20000,
                "stock": 50,
            },
        )

        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert len(response_model.result) == 2

    def test_list_products_pagination(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 목록 페이징 테스트"""
        # 상품 15개 생성
        for i in range(15):
            client.post(
                test_app.url_path_for(RouteName.PRODUCTS_CREATE),
                json={
                    "name": f"상품 {i}",
                    "price": 1000 * (i + 1),
                    "stock": 10,
                },
            )

        # 기본 페이지 (limit=10)
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert len(response_model.result) == 10

        # 두 번째 페이지 (offset=10, limit=10)
        response = client.get(
            test_app.url_path_for(RouteName.PRODUCTS_LIST),
            params={"offset": 10, "limit": 10},
        )
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert len(response_model.result) == 5


class TestProductGet:
    """단일 상품 조회 테스트"""

    def test_get_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """단일 상품 조회 성공 테스트"""
        created_product = create_test_product(test_app, client)

        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_GET, product_id=created_product.id))

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.result.id == created_product.id
        assert response_model.result.name == created_product.name

    def test_get_product_not_found(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 상품 조회 실패 테스트"""
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_GET, product_id=99999))

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductUpdate:
    """상품 정보 수정 테스트"""

    def test_update_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 정보 수정 성공 테스트"""
        created_product = create_test_product(test_app, client)
        new_name = "수정된 상품명"
        new_price = 50000.0

        response = client.patch(
            test_app.url_path_for(RouteName.PRODUCTS_UPDATE, product_id=created_product.id),
            json={
                "name": new_name,
                "price": new_price,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.result.name == new_name
        assert response_model.result.price == new_price
        # 변경하지 않은 필드는 그대로 유지되어야 함
        assert response_model.result.stock == created_product.stock
        assert response_model.result.description == created_product.description

    def test_update_product_not_found(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 상품 수정 실패 테스트"""
        response = client.patch(
            test_app.url_path_for(RouteName.PRODUCTS_UPDATE, product_id=99999),
            json={"name": "새 이름"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
