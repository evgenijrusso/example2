from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from core.config import settings
from asyncio import current_task


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url, echo=echo  # можно иначе settings.db_url  # settings.db_echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):  # добавляем еще одного помощника для создания сессии
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,  # без ()
        )
        return session

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:  # заменил get_scoped_session() на session_factory
            yield session
            await session.close()  # заменил remove на close

    async def scoped_session_dependency(self) -> AsyncSession:  # новое решение
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)
