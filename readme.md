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
