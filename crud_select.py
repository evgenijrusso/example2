#  Временный файл для запросов по пользователю.
import asyncio
from click.testing import Result
from mako.testing.helpers import result_lines
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from core.models import db_helper, Post, Profile, User


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user: ", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)  # 1-й вариант
    user: User | None = result.scalars().one_or_none()  # 1-й вариант
    # user = await session.scalar(stmt)                 # 2-й вариант
    print("found username: ", username, " ", user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profile(session: AsyncSession):
    stmt = (
        select(User).options(joinedload(User.profile)).order_by(User.id)
    )  # нужны доп. параметры (joinedload) для объединения User.profile
    # result: Result = await session.execute(stmt)      1-й вариант
    # users = result.scalars()
    users = await session.scalars(stmt)  # 2-й вариант
    for user in users:
        print("User: ", user)
        print("User_profile: ", user.profile.first_name, user.profile.last_name)


async def create_posts(
    session: AsyncSession,
    user_id: int,
    *posts_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in posts_titles]
    session.add_all(posts)
    await session.commit()
    print("post:", posts)
    return posts


#  4 варианта в Readme.md
async def get_users_with_posts(session: AsyncSession):
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    users = await session.scalars(stmt)

    # type: User #  1-й вариант, добавить уникальность users.unique():, 2-й вариант - users:
    for user in users:
        print("**" * 10)
        print("User: ", user)
        for post in user.posts:  # type: User.posts
            print("User_posts: ", post.title, " ", post.body)


# от поста к пользователю (автору постов)
async def get_posts_with_author(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)
    for post in posts:
        print("post: ", post)
        print("author:", post.user)
        print("**" * 10)


async def get_users_with_posts_and_profiles(session: AsyncSession):
    stmt = (
        select(User)
        .options(
            joinedload(User.profile),
            selectinload(User.posts),
        )
        .order_by(User.id)
    )
    users = await session.scalars(stmt)

    for user in users:  # type: User
        print("**" * 10)
        print(
            user, user.profile and user.profile.first_name
        )  # Если только `user.profile.first_name`, то ошибка
        for post in user.posts:
            print("-", post)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .join(Profile.user)  # фильтрация для user
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .where(User.username == "John")
        .order_by(Profile.id)
    )
    profiles = await session.scalars(stmt)
    for profile in profiles:
        print("profile: ", profile.first_name, profile.user)
        print("profile user posts: ", profile.user.posts)


# Второе видео
async def main_relations(session: AsyncSession):
    await main_relations(session)
    await create_user(session=session, username="John")
    await create_user(session=session, username="Sam")
    await create_user(session=session, username="Alice")
    user_john = await get_user_by_username(session=session, username="John")
    user_sam = await get_user_by_username(session=session, username="Sam")
    await create_user_profile(
        session=session,
        user_id=user_john.id,
        first_name="Johnny",
        last_name="Forst",
    )
    await create_user_profile(
        session=session,
        user_id=user_sam.id,
        first_name="Sammy",
        last_name="Sloy",
    )
    await show_users_with_profile(
        session=session
    )  # отдельно проверяем и потом комментируем
    await create_posts(
        session,
        user_john.id,
        "SQLA 2.0",
        "SQLA Joins",
        "SQLA To",
    )
    await create_posts(
        session,
        user_sam.id,
        "Fast API",
        "Fast intro",
    )
    await get_users_with_posts(session=session)
    await get_posts_with_author(session=session)
    await get_users_with_posts_and_profiles(session=session)
    await get_profiles_with_users_and_users_with_posts(session=session)


async def demo_m2m(session: AsyncSession): ...


async def main():
    async with db_helper.session_factory() as session:
        await main_relations(session)


if __name__ == "__main__":
    asyncio.run(main())
