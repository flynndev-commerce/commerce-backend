from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.application.dto.cart_dto import CartItemCreate, CartItemUpdate, CartRead
from app.application.dto.response import BaseResponse
from app.application.use_cases.cart_use_case import CartUseCase
from app.containers import Container
from app.core.route_names import RouteName
from app.core.security import get_current_user
from app.domain.model.user import User

router = APIRouter(prefix="/carts", tags=["carts"])


@router.get(
    "/me",
    response_model=BaseResponse[CartRead],
    name=RouteName.CARTS_GET_MY_CART,
    summary="내 장바구니 조회",
)
@inject
async def get_my_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    cart_use_case: Annotated[CartUseCase, Depends(Provide[Container.cart_use_case])],
) -> BaseResponse[CartRead]:
    """
    현재 로그인한 사용자의 장바구니를 조회합니다.
    """
    # User.id is Optional[int], but authenticated user must have an ID.
    if current_user.id is None:
        raise ValueError("User ID is missing")

    cart = await cart_use_case.get_cart(user_id=current_user.id)
    return BaseResponse(result=cart)


@router.post(
    "/items",
    response_model=BaseResponse[CartRead],
    name=RouteName.CARTS_ADD_ITEM,
    summary="장바구니에 상품 추가",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_item_to_cart(
    item_in: CartItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    cart_use_case: Annotated[CartUseCase, Depends(Provide[Container.cart_use_case])],
) -> BaseResponse[CartRead]:
    """
    장바구니에 상품을 추가합니다. 이미 존재하는 상품이면 수량을 증가시킵니다.
    """
    if current_user.id is None:
        raise ValueError("User ID is missing")

    cart = await cart_use_case.add_to_cart(user_id=current_user.id, item_create=item_in)
    return BaseResponse(result=cart)


@router.patch(
    "/items/{product_id}",
    response_model=BaseResponse[CartRead],
    name=RouteName.CARTS_UPDATE_ITEM,
    summary="장바구니 상품 수량 변경",
)
@inject
async def update_cart_item(
    product_id: int,
    item_in: CartItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    cart_use_case: Annotated[CartUseCase, Depends(Provide[Container.cart_use_case])],
) -> BaseResponse[CartRead]:
    """
    장바구니에 담긴 상품의 수량을 변경합니다.
    """
    if current_user.id is None:
        raise ValueError("User ID is missing")

    cart = await cart_use_case.update_item_quantity(
        user_id=current_user.id, product_id=product_id, item_update=item_in
    )
    return BaseResponse(result=cart)


@router.delete(
    "/items/{product_id}",
    response_model=BaseResponse[CartRead],
    name=RouteName.CARTS_REMOVE_ITEM,
    summary="장바구니 상품 삭제",
)
@inject
async def remove_cart_item(
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    cart_use_case: Annotated[CartUseCase, Depends(Provide[Container.cart_use_case])],
) -> BaseResponse[CartRead]:
    """
    장바구니에서 특정 상품을 삭제합니다.
    """
    if current_user.id is None:
        raise ValueError("User ID is missing")

    cart = await cart_use_case.remove_item(user_id=current_user.id, product_id=product_id)
    return BaseResponse(result=cart)
