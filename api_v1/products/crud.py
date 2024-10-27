"""
Создание Create, Read, Update, Delete
"""

from click import password_option
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.product import Product

from .schemas import ProductCreate, ProductUpdate, ProductUpdatePartial


async def get_products(session: AsyncSession) -> list[Product]:  # чтение неких товаров
    stmt = select(Product).order_by(Product.id)
    result: Result = await session.execute(stmt)  # execute - выполнить выражение
    products = result.scalars().all()
    return list(products)


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def create_product(session: AsyncSession, product_new: ProductCreate) -> Product:
    product = Product(
        **product_new.model_dump()
    )  # model_dump() - преобразование в словарь (распаковать)
    session.add(product)
    await session.commit()
    # await session.refresh(product)  # для возможного изменеия товара ?!
    return product


async def update_product(
    session: AsyncSession,
    product: Product,
    product_update: ProductUpdate | ProductUpdatePartial,
    partial: bool = False,
) -> Product:  # put
    for name, value in product_update.model_dump(exclude_unset=partial).items():
        setattr(product, name, value)
    await session.commit()
    return product


# async def update_product_partial(
#     session: AsyncSession,
#     product: Product,
#     product_update: ProductUpdatePartial,
# ) -> Product:  # patch
#     product_update.model_dump(exclude_unset=True)
#     for name, value in product_update.model_dump().items():
#         setattr(product, name, value)
#     await session.commit()
#     return product


async def delete_product(
    session: AsyncSession,
    product: Product,
) -> None:
    await session.delete(product)
    await session.commit()
