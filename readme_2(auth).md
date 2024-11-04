## Аутентификация в FastAPI | Basic Auth, Cookie Auth, Заголовки, Токен | FastAPI Auth
##(файл api_v1/demo_auth/views.py)
---------------
Надо подключить HTTPBasic, HTTPBasicCredentials из `fastapi.security`. Можно посмотреть код `HTTPBasic` и там 
показана его реализация.

## Example
    ```python
    from typing import Annotated

    from fastapi import Depends, FastAPI
    from fastapi.security import HTTPBasic, HTTPBasicCredentials

    app = FastAPI()

    security = HTTPBasic()

    @app.get("/users/me")
    def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
        return {"username": credentials.username, "password": credentials.password}
    ```
    """
Теперь роутер надо подключить в нашем приложении. Переходим в __init__.py(api_v1) и подлючаем этот роутер.
Перевод: `credentials` - реквизиты для входа 
Переходим на Uvicorn running on http://127.0.0.1:8002/docs и видем, что есть появилась кнопка `Authorise`, где 
можно ввести имя и пароль. Кроме этого добавилась форма `Demo Auth` c кнопкой "Get".
Можно использовать ввод пользователя и пароля в адресной строке, типа:
`http://username:password@127.0.0.1:8002/api/v1/demo-auth/basic-auth/`
получаем 
{
    "message": "Hi!",
    "username": "username",
    "password": "password"
}
В `Network` браузера можно увидеть URL-адрес запроса: http://127.0.0.1:8002/api/v1/demo-auth/
Браузер запомнил вход и теперь даже если использовать `http://127.0.0.1:8002/api/v1/demo-auth/`, то все равно
показывает Код состояния: 200 OK
В заголовке `Accept` видем, параметр `authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=` (это Base64 - закодированная строка).
Ее можно раскодировать. В сети есть сайт: `base64decode.org`. Вставляешь код `dXNlcm5hbWU6cGFzc3dvcmQ=` 
и получаешь результат = `username:password`
Точно так же можно изменить пользователя и пароль, например: john:secret и так же авторизоваться.
`http://john:secret@127.0.0.1:8002/api/v1/demo-auth/basic-auth/`
Можно да же без пароля.
`http://john:@127.0.0.1:8002/api/v1/demo-auth/basic-auth/`

- Проверка по логину и паролю.
Создаем, как пример, словарь для пользователей
```python
usernames_to_password = {
    'admin1':'admin1',
    'tom': 'password',
}
```
# Работа с токеном.
```
from fastapi import Depends
@router.get("/some-http-header-auth/")  # после проверки
def demo_auth_some_http_header(auth_username: str = Depends(...)):
    return {
        "message": f"Привет, {auth_username}!",
        "username": auth_username,
    }
```
можно создать токен таким образом в терминале:
`python -c 'import secrets; print(secrets.token_hex())'`
получил, например, токен `da47c0801184f657ac2220b50df635e3f48f85edbd9b2813c82c07b59b8615b3`.
Если еще раз запустить создание другого токена, то код будет другой.   
Этот токен можно разделить на 2 "кусочка"  
```python
static_auth_token_to_username = {
    "admin1": "admin1",
    "tom": "pass",
}
```
и преобразовать `static_auth_token_to_username` на 2 части:
"admin1" -> "da47c0801184f657ac2220b50df635e3"
"tom" -> "f48f85edbd9b2813c82c07b59b8615b3" 
```python
static_auth_token_to_username = {
    "da47c0801184f657ac2220b50df635e3": "admin1",
    "f48f85edbd9b2813c82c07b59b8615b3": "pass",
}
```
URL-адрес запроса: http://127.0.0.1:8002/api/v1/demo-auth/some-http-header-auth/
Метод запроса: GET
Код состояния: 200 OK
Удаленный адрес: 127.0.0.1:8002
connection: keep-alive
x-secret-auth-token: da47c0801184f657ac2220b50df635e3

Работает. В заголовке запроса присутствует alias `x-secret-auth-token:da47c0801184f657ac2220b50df635e3` 

## Cookie (login with cookies)

- установка cookies
Этот словарь COOKIES: dict[str, dict[str, Any]] = {}  # временное хранилище наших cookies о пользователях,
которые выполнили вход. Нам нужно на ответ который получает пользователь, установить cookies. Для этого импортируем 
объект Response и мы можем либо создать экземпляр здесь:
```
response=Response() # и потом его вернуть
return response
```
или получим этот `response` в аргументах. В Этом случае далее выполняем `response.set_cookie()`. 
Здесь нужен ключ из словаря `COOKIES` 
Поэтому делаем: COOKIE_SESSION_ID_KEY = "web-app-session-id"  # любая строка

`response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)` - 
мы не хотим, чтобы у всех пользователей, выполняющие вход, был свой `session_id`.  Поэтому нам нужно 
отдельно случайно генерировать `session_id`.

Для этого, создаем новую функцию `def generate_session_id()`, которая возвращает просто строку
```
def generate_session_id() -> str:
    return uuid.uuid4().hex  # генерация случайных строк
```
И через эту фукцию будем генерировать новую Id сессии
`COOKIES[session_id] = {"username": auth_username, "login_at": int(time())}`  # id user
параметр "login_at" совсем необязательный, можно и без него. Главное, что он будет уникальным для разных пользователей.
И вот создали способ входа пользователя. А что нужно сделать, чтобы его прочитать. Что выполнили вход и получаем 
эту информацию (`COOKIES[session_id])

## JWT Auth в FastAPI | Выпуск и проверка токена | Пароль и шифрование через bcrypt