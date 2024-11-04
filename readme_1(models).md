#  Замечания
Продолжение проекта `example1`. Не понравилось повторение питоновких пакетов при их создании (В терминале 
запускал команду `poetry new example1`, потом находим его в каталоге и открываем в `pycharm`).
Решил продолжить здесь.


- Запуск проекта:
##  Установка
- poetry add fastapi[all]   
- poetry add pydantic[email]
- poetry add sqlalchemy, psycopg, asyncpg, pymysql (p.s. sqlalchemy не установилось сразу)
- poetry show --tree (проверка зависимостей)
- poetry add black --group dev (p.s. пока поставил через `settings` в Pycharm)
- poetry add aiosqlite
- poetry add alembic
- 
## Добавил (изменил номер порта) в main.py
```
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, log_level="info", reload=True)
```

## Создание базы данных (Product)
Сначало запустил создание БД. Файл БД выл создан, но в терминале создание таблице не прошло.
Потом вспомнил, что в файле `core.models.__init__py` был добавлен код:
```
# Объекты для экспорта (могут пригодится)
__all__ = (
    'Base',
    'Product',
    'DatabaseHelper',
    'db_helper',
)

from .database import Base
from .product import Product
from .db_helper import db_helper, DatabaseHelper
```
и это помогло, появилась таблица в БД. Решил перепроверить, удалил таблицу в БД  и закомментировал 
эти объекты(__all__ = ..). Запустил код в `main.py` и в терминале снова появилась таблица 'Product' в БД.
Так что не совсем понятно, почему ранее таблица не создавалась ?!

## Config.py
```
db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}\db_example2.sqlite3"
``` 
Так и не разобрался до конца, как правильно добавлять  в строку `port` и слеш '\' перед названием БД.
Менял и так '\' и так '/' - разницу не увидел. При этом таблица создавалась, но в браузере модель "Product" не 
отображается.

## Проблемы с обновлением браузера, порт 8002, main.py.
Пользовался этим решением: `uvicorn.run("main:app", host="127.0.0.1", port=8002, log_level="info", reload=True)`
Но обновления не проходило. В терминале проверял `Id` нужного мне процесса на порту 8002. Этот `id` процесса получал 
из команды `netstat -ano|findstr 8002` и затем искал `Id` в диспетчере задач. Однако `Id` в диспетчере не совпадало 
со значением от `netstat` (так и не понял причину). В диспетчере нашел `python.exe` и удалил все это процессы. `
В main.py` немного изменил строку запуска: `reload=True` -> `reload=False`. И после этого в браузере отобразился 'Product'.

## db_helper
```
async def session_dependency(self) -> AsyncSession:
    async with self.session_factory() as session:   # заменил get_scoped_session() на session_factory
        yield session
        await session.close()    # заменил remove на close
```
Пришлось заменил `get_scoped_session()` на `session_factory`, иначе была ошибка
Затем была добавлено еще одна новая функция
```
    async def scoped_session_dependency(self) -> AsyncSession:  # новое решение
        session = self.get_scoped_session()
        yield session
        await session.close()
```
и потом ее следовало заменить в `views.py` на предыдущую:
- `Depends(db_helper.session_dependency)  -> Depends(db_helper.scoped_session_dependency))`
## Работа с alembic (миграции)
Выбор варианта: async - `Generic single-database configuration with an async dbapi`
- `alembic init alembic` (простой вариант)
- `alembic init -t async alembic` (варианта для асинхронного движка)
- `alembic revision -m "create account table"`  
Можно использования автомиграцию. В  файле `.env.py` укажем, откуда брать информацию в существующих таблицах. 
И нам достаточно указать в файле `.env.py`
```.env.ini
# target_metadata = None   -- эту строку комментируем
from core.models import Base -- добавляем импорт Base
from core.config import settings  --  добавляем импорт settings (чтобы скорректировать путь к БД)
target_metadata = Base.metadata 
# далее переопределяем `sqlalchemy.url` (из alembic.ini - sqlalchemy.url = driver://user:pass@localhost/dbname)
```
## Создаем автомиграцию
- `alembic revision --autogenerate -m "Create products table"`
Учитывая то, что у нас модель уже сформирована, `alembic` сравнивает модель и БД и видит, что в данном случае нет изменений.
Т.е. эту миграцию можно удалить.
Далее, для проверки, удаляем базу данных. И потом снова запускаем миграцию. В миграции уже формируется снова модель "Продукт".
P.s. Пока миграцию еще не реализовали (не задействовали), ее можно удалить. В БД ее еще нет.

## alembic.ini
Для форматирования кода миграции, в `alembic.ini` `использует black`
Было:
```
# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME
```
Стало:
```
# format using "black" - use the console_scripts runner, against the "black" entrypoint
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 89 REVISION_SCRIPT_FILENAME
```
Для изменения БД используется команда `alembic upgrade head`
Для отката текущей миграции используется команда: `alembic downgrade -1`
Рекомендуется сначало коммитет изменения в проекте, а только потом файл миграции

Теперь можно отказаться от кода `....db_helper.engine.begin()`
```
async def lifespan(app: FastAPI):
   # async with db_helper.engine.begin() as conn:
   #     await conn.run_sync(Base.metadata.create_all)  # `create_all`  без скобок ()
    yield
```
## Далее
Создаем новую модель `User` в `core` (пока только поле `username`) и создаем новую миграцию
- `alembic revision --autogenerate -m "Create users table"` (проверить миграция)
- `alembic upgrade head` - выполняем миграцию

Создаем еще одну модель `Post` (поля - title, body).
И в этом моделе создаем внешний ключ `users.id` для связи моделей User->Post (one to many)
`user_id = Mapped[int] = mapped_column(ForeignKey("users.id"))` 
p.s. "user_id" - формируется 'user' в нижнем регистре +(s) и через подчеркивание `id`
Затем создаем новую миграцию:
- `alembic revision --autogenerate -m "Create posts table"` (проверить миграция)
- `alembic upgrade head` - выполняем миграцию 'Post', , появилась таблица в БД.

Создаем новую модель `Profile`, которая будет связана с моделью `User` через связь `one to one` 
Там есть повторяющая запись типа `user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)`
Чтобы не было повторений, создаем новый класс Mixin (файл `mixins.py`, перевод - примесь)
И в конце дополняем класс "User" строкой   `profile: Mapped["Profile"] = relationship(back_populates="user")`  

Создал миграцию `alembic revision --autogenerate -m "Create profile table"` - не пригодилось, изменений в моделях нет.
Добавил "Profile" `в __init__.py (core.models)`
Снова создал миграцию `alembic revision --autogenerate -m "Create profile table"`.
Теперь миграция создалась для модели `Profile`
Далее, `alembic upgrade head` - выполняем миграцию на `Profile`, появилась таблица в БД.  

## История миграция
- `alembic history`
- `alembic current` 
- `alembic downgrade -2` #  пример, возрат на 2 миграции (post, profile) 
- `alembic downgrade base` 
Проверка: 
выполним `alembic downgrade -2` (в БД удалены миграции post, profile)
вернем эти миграции `alembic upgrade head` - вернулись удаленные миграции.

- Можно удалить все `alembic downgrade base` - удалил все миграции
`alembic upgrade head` - восстановил все миграции

## def get_users_with_posts():  -- несколько вариантов
```py 
# 1-вариант
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User

async def get_users_with_posts1(session: AsyncSession):
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    users = await session.scalars(stmt)           # 1-й вариант
    
    for user in users.unique():
        print("**" * 10)
        print("User: ", user)
        for post in user.posts:  # type: User.posts
            print("User_posts: ", post.title, " ", post.body)

# 2-вариант
async def get_users_with_posts2(session: AsyncSession):
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    result: Result = await session.execute(stmt)  # 2-й вариант
    users = result.unique().scalars()  # 2-й вариант

    for user in users:
        print("**" * 10)
        print("User: ", user)
        for post in user.posts:  # type: User.posts
            print("User_posts: ", post.title, " ", post.body)

# 3-вариант
async def get_users_with_posts3(session: AsyncSession):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    result: Result = await session.execute(stmt)  # 3-й вариант
    users = result.scalars()  # 3-й вариант

    for user in users:
        print("**" * 10)
        print("User: ", user)
        for post in user.posts:  # type: User.posts
            print("User_posts: ", post.title, " ", post.body)

# 4-вариант
async def get_users_with_posts4(session: AsyncSession):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    users = await session.scalars(stmt)

    # ... далее то же самое
```

## Третье видео посвящено отношение много-ко-много
- В core.models создаем новый файл `order.py` (Заказ) и копируем пока данные из `product.py`  
```
class Order(Base):
    promocode: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now(timezone.utc),  # в оригинале - datetime.utcnow
    )
```
- создаем миграцию `alembic revision --autogenerate -m "Create orders table"`
- удалил миграцию для изменения поля `promocode`. Нужно `promocode: Mapped[str | None]`
- создаем новый файл `order_product_association` и в нес создаем класс `order_product_association_table`.
Это промежуточная таблица в формате `many-to-many`  и используется именно (старый метод)  в `core` (не в `ord`).
```python
from sqlalchemy import Table, Column, ForeignKey
from core.models.database import Base

order_product_association_table = Table(
    "order_product_association",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)
```
Эта таблица будет работать. Но для, чтобы потом не делать возможные миграции, эту таблицу можно изменить.
Добавим с нее дополнительно `id` с `primary_key`, а колонках "order_id" и "product_id" уберем.
```python
from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint
from  core.models.database import Base

order_product_association_table = Table(
    "order_product_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("order_id", ForeignKey("orders.id"), nullable=False),
    Column("product_id", ForeignKey("products.id"), nullable=False),
    UniqueConstraint("order_id", "product_id", name="idx_unique_order_product"),
)
```
Создаем миграцию `alembic revision --autogenerate -m "Create order product association table"`
Выполняем  миграцию `alembic upgrade head`

## Запросы по m2m (сделал в другом файле crud_m2m)
- создаем функцию `create_order`
- создаем функцию `create_product`
И создаем несколько товаров и заказов в `demo_m2m`
- После проверки функции `get_order_with_products`(`crud_m2m`), предложено изменить таблицу 
`order_product_association_table` (см. выше), добавляя класс для работы с алхимией.
```python
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.models.database import Base

class OrderProductAssociation(Base):
    __tablename__ = "order_product_association"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="idx_unique_order_product",
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
```
Изменение таблица "Product", "Order" и правим `__init__.py`
```python
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship
from core.models.database import Base

if TYPE_CHECKING:
    from core.models import Order

class Product(Base):
    # __tablename__ = "products" #  убрал название таблицы. Оно реализуется через `Base` (database)

    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    orders: Mapped[list[Order]] = relationship(
        secondary="order_product_association",
        back_populates="products",
    )
```
- Добавляем некоторые свойства в класс `OrderProductAssociation`. 
```
    count: Mapped[int] = mapped_column(ForeignKey("products.id"))
```
- Новые изменения. Временно отключаем в классах `Order` и `Product` соответственно поля `products` и `order`.
В функции `demo_m2m` убираем  код
``` 
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
 ```
- Возращаем обратно в классах `Order` и `Product` соответственно поля `products` и `order`.
- Судя по всему, можно использовать, например, в `Order` либо  поле `products`, либо поле `products_details`
- Снова отключаем в классах `Order` и `Product` соответственно поля `products` и `order`. В классе 
`OrderProductAssociation` добавляем поле `unit_price[int]` и 
- создаем миграцию `alembic revision --autogenerate -m "Add unit_price column to order product association table"`
Выполняем  миграцию `alembic upgrade head`
- Переопределяем функцию `get_order_with_products_with__assoc() -> get_order_with_products_assoc()`
P.s. Сложно. Так и не понял, клда использовать ассоциативную модель, а когда сквозную модель.


  
