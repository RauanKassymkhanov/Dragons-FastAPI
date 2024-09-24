from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterable
from alembic.config import Config
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings


class Base(DeclarativeBase):
    pass


def get_alembic_config(database_url: PostgresDsn, script_location: str = "migrations") -> Config:
    alembic_config = Config()
    alembic_config.set_main_option("script_location", script_location)
    alembic_config.set_main_option(
        "sqlalchemy.url",
        database_url,
    )
    return alembic_config


@lru_cache
def async_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=True,
    )


@lru_cache
def async_session_factory() -> async_sessionmaker:
    return async_sessionmaker(
        bind=async_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


async def get_db_session() -> AsyncIterable[AsyncSession]:
    async with get_managed_session() as session:
        yield session


@asynccontextmanager
async def get_managed_session() -> AsyncSession:
    factory: async_sessionmaker = async_session_factory()
    session: AsyncSession = factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    else:
        await session.commit()
    finally:
        await session.close()
