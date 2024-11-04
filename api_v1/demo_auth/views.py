import secrets
import uuid
from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials


router = APIRouter(prefix="/demo-auth", tags=["Demo Auth"])

security = HTTPBasic()


# -------------- 1 ------------------------------------
@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }


usernames_to_password = {
    "admin1": "admin1",
    "tom": "pass",
}

# 2 ----------- get_auth_user_username (Basic Auth)-----------------------


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    unauthed = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},  # правило хорошего тона
    )
    correct_password = usernames_to_password.get(credentials.username)
    if correct_password is None:
        raise unauthed

    # сравнение рекомендуется импользовать через `secrets`
    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),  # текущий пароль
        correct_password.encode("utf-8"),  # корректный пароль
    ):
        raise unauthed

    return credentials.username


@router.get("/basic-auth-username/")  # после проверки
def demo_basic_auth_username(auth_username: str = Depends(get_auth_user_username)):
    return {
        "message": f"Привет, {auth_username}!",
        "username": auth_username,
    }


# 3 -------(Token Auth)------- "/some-http-header-auth/" (новый помощник)------------------
# помощник будет доставать из заголовков инфомацию об аутентификации пользователя
# и возвращать ему `username`, если пользователь  аутетифицирован
# по  идее, username храниться в БД, но пока используем словарь

static_auth_token_to_username = {
    "da47c0801184f657ac2220b50df635e3": "admin1",
    "f48f85edbd9b2813c82c07b59b8615b3": "tom",
}


def get_username_by_static_auth_token(
    static_token: str = Header(alias="x-secret-auth-token"),
) -> str:
    if username := static_auth_token_to_username.get(static_token):
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )


@router.get("/some-http-header-auth/")  # после проверки
def demo_auth_some_http_header(
    auth_username: str = Depends(get_username_by_static_auth_token),
):
    return {
        "message": f"Привет, {auth_username}!",
        "username": auth_username,
    }


# 4 -----Cookie Auth)------- cookies ------------------------------
COOKIES: dict[str, dict[str, Any]] = {}  # временное хранилище наших cookies
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
) -> dict:  # для демонстрации
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )
    return COOKIES[session_id]


@router.post("/login-cookie/")  # после проверки
def demo_auth_login_set_cookies(
    response: Response,
    # auth_username: str = Depends(get_auth_user_username),  # взято из 2-го примера
    username: str = Depends(
        get_username_by_static_auth_token
    ),  # взято из 3-го примера (токен)
):
    session_id = generate_session_id()
    COOKIES[session_id] = {
        "username": username,
        "login_at": int(time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "Ok"}


@router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
):  # получить здесь информацию по пользователю
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}!",
        "username": username,  # оставил
        **user_session_data,
    }


@router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
):  # logout
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }
