from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from app.application.dto.order_dto import OrderCreate, OrderRead
from app.application.dto.response import BaseResponse
from app.application.dto.user_dto import UserRead
from app.application.use_cases.order_use_case import OrderUseCase
from app.containers import Container
from app.core.route_names import RouteName
from app.core.security import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    summary="주문 생성",
    response_model=BaseResponse[OrderRead],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.ORDERS_CREATE,
)
@inject
async def create_order(
    order_create: OrderCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    order_use_case: Annotated[OrderUseCase, Depends(Provide[Container.order_use_case])],
) -> BaseResponse[OrderRead]:
    created_order = await order_use_case.create_order(
        user_id=current_user.id,
        order_create=order_create,
    )
    return BaseResponse(result=created_order)


@router.get(
    "",
    summary="내 주문 목록 조회",
    response_model=BaseResponse[list[OrderRead]],
    name=RouteName.ORDERS_LIST,
)
@inject
async def list_orders(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    order_use_case: Annotated[OrderUseCase, Depends(Provide[Container.order_use_case])],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> BaseResponse[list[OrderRead]]:
    orders = await order_use_case.list_orders(
        user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return BaseResponse(result=orders)


@router.get(
    "/{order_id}",
    summary="주문 상세 조회",
    response_model=BaseResponse[OrderRead],
    name=RouteName.ORDERS_GET,
)
@inject
async def get_order(
    order_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    order_use_case: Annotated[OrderUseCase, Depends(Provide[Container.order_use_case])],
) -> BaseResponse[OrderRead]:
    order = await order_use_case.get_order(
        user_id=current_user.id,
        order_id=order_id,
    )
    return BaseResponse(result=order)


@router.post(
    "/{order_id}/cancel",
    summary="주문 취소",
    response_model=BaseResponse[OrderRead],
    name=RouteName.ORDERS_CANCEL,
)
@inject
async def cancel_order(
    order_id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    order_use_case: Annotated[OrderUseCase, Depends(Provide[Container.order_use_case])],
) -> BaseResponse[OrderRead]:
    cancelled_order = await order_use_case.cancel_order(
        user_id=current_user.id,
        order_id=order_id,
    )
    return BaseResponse(result=cancelled_order)
