#  Временный файл для запросов по пользователю.
import asyncio
from itertools import product, count

from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from core.models import (
    db_helper,
    Post,
    Profile,
    User,
    Order,
    Product,
    OrderProductAssociation,
)


async def create_order(
    session: AsyncSession,
    promocode: str | None = None,
) -> Order:
    order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: int,
) -> Product:
    product_new = Product(
        name=name,
        description=description,
        price=price,
    )
    session.add(product_new)
    await session.commit()
    return product_new


async def create_orders_and_products(session: AsyncSession):
    order_one = await create_order(session)
    order_promo = await create_order(session, promocode="promo")

    mouse = await create_product(
        session,
        name="Mouse",
        description="Great gaming mouse",
        price=123,
    )
    keyboard = await create_product(
        session,
        name="Mouse",
        description="Great gaming keyboard",
        price=149,
    )
    display = await create_product(
        session,
        name="Display",
        description="Office display",
        price=299,
    )
    order_one = await session.scalar(
        select(Order)
        .where(Order.id == order_one.id)
        .options(
            selectinload(Order.products),
        ),
    )
    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order_one.products = [mouse, keyboard]
    order_promo.products = [keyboard, display]

    await session.commit()


async def get_order_with_products(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)
    return list(orders)


async def demo_get_order_with_products_through_secondary(session: AsyncSession):
    orders = await get_order_with_products(session)
    for order in orders:
        print("**" * 10)
        print("Order:", order.id, order.promocode, " ", order.create_at)
        for product in order.products:  # type: Product
            print(
                "products: ",
                product.id,
                product.name,
                product.description,
                product.price,
            )


async def get_order_with_products_assoc(session: AsyncSession):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)
    return list(orders)


async def demo_get_order_with_products_with_assoc(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)
    for order in orders:
        print("Order -> all", order.id, order.promocode, order.create_at, "product:")
        for (
            order_products_details
        ) in order.products_details:  # type OrderProductAssociation
            print(
                "-",
                order_products_details.product.id,
                order_products_details.product.name,
                order_products_details.product.price,
                "qty:",
                order_products_details.count,
            )


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_order_with_products_assoc(session)
    gift_product = await create_product(
        session,
        name="Gift",
        description="Gift for you",
        price=0,
    )
    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                count=1,
                unit_price=0,
                product=gift_product,
            )
        )
    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session)
    # await demo_get_order_with_products_through_secondary(session)
    await demo_get_order_with_products_with_assoc(session)  # получение информации
    # await create_gift_product_for_existing_orders(session)  № создание gift_product


async def main():
    async with db_helper.session_factory() as session:
        await demo_m2m(session)


if __name__ == "__main__":
    asyncio.run(main())
