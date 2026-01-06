from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from app.application.dto.product_dto import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.application.dto.response import BaseResponse
from app.application.use_cases.product_use_case import ProductUseCase
from app.containers import Container
from app.core.route_names import RouteName
from app.core.security import get_current_seller
from app.domain.model.seller import Seller

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    summary="신규 상품 생성",
    response_model=BaseResponse[ProductRead],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.PRODUCTS_CREATE,
)
@inject
async def create_product(
    product_create: ProductCreate,
    product_use_case: Annotated[ProductUseCase, Depends(Provide[Container.product_use_case])],
    seller: Annotated[Seller, Depends(get_current_seller)],
) -> BaseResponse[ProductRead]:
    assert seller.id is not None

    created_product = await product_use_case.create_product(seller_id=seller.id, product_create=product_create)
    return BaseResponse(result=created_product)


@router.get(
    "",
    summary="상품 목록 조회",
    response_model=BaseResponse[list[ProductRead]],
    name=RouteName.PRODUCTS_LIST,
)
@inject
async def list_products(
    product_use_case: Annotated[ProductUseCase, Depends(Provide[Container.product_use_case])],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    seller_id: Annotated[int | None, Query(title="판매자 ID 필터")] = None,
) -> BaseResponse[list[ProductRead]]:
    products = await product_use_case.list_products(offset=offset, limit=limit, seller_id=seller_id)
    return BaseResponse(result=list(products))


@router.get(
    "/{product_id}",
    summary="단일 상품 조회",
    response_model=BaseResponse[ProductRead],
    name=RouteName.PRODUCTS_GET,
)
@inject
async def get_product(
    product_id: int,
    product_use_case: Annotated[ProductUseCase, Depends(Provide[Container.product_use_case])],
) -> BaseResponse[ProductRead]:
    product = await product_use_case.get_product_by_id(product_id=product_id)
    return BaseResponse(result=product)


@router.patch(
    "/{product_id}",
    summary="상품 정보 수정",
    response_model=BaseResponse[ProductRead],
    name=RouteName.PRODUCTS_UPDATE,
)
@inject
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    product_use_case: Annotated[ProductUseCase, Depends(Provide[Container.product_use_case])],
    seller: Annotated[Seller, Depends(get_current_seller)],
) -> BaseResponse[ProductRead]:
    assert seller.id is not None

    updated_product = await product_use_case.update_product(
        seller_id=seller.id, product_id=product_id, product_update=product_update
    )
    return BaseResponse(result=updated_product)
