from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ProductCreate, Product, ProductUpdate, ProductUpdatePartial
from fastapi import APIRouter, status, Depends
from core.models import db_helper
from .dependencies import product_by_id
from . import crud

router = APIRouter(tags=["Products"])


@router.get("/", response_model=list[Product])
async def get_products(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_products(session=session)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_new: ProductCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),  # без ()
):
    return await crud.create_product(session=session, product_new=product_new)


@router.get("/{product_id}/", response_model=Product)
async def get_product(product: Product = Depends(product_by_id)):
    return product


# @router.get("/{product_id}/", response_model=Product)
# async def get_product(
#     product_id: int,
#     session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ):
#     product = await crud.get_product(product_id=product_id, session=session)
#     if product is not None:
#         return product
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Product {product_id} not found!",
#     )


@router.put("/{product_id}/", response_model=Product)
async def update_product(
    product_update: ProductUpdate,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_product(
        session=session,
        product=product,
        product_update=product_update,
    )


@router.patch(
    "/{product_id}/", response_model=Product
)  # обновляются только некоторые параметры
async def update_product(
    product_update: ProductUpdatePartial,
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_product(
        session=session,
        product=product,
        product_update=product_update,
        partial=True,
    )


@router.delete("/{product_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product: Product = Depends(product_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    await crud.delete_product(session=session, product=product)
