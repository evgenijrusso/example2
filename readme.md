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