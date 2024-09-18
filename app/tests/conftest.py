import os
import pathlib
from asyncio import DefaultEventLoopPolicy
from contextlib import asynccontextmanager
from typing import AsyncIterable, Callable

import boto3
import pytest
from alembic.command import downgrade, upgrade
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.database import get_alembic_config, get_db_session
from moto import mock_aws

from app.tests.factory_schemas import SqsRecordModelFactory

TEST_HOST = "http://test"


def pytest_configure(config: pytest.Config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    os.environ["ENVIRONMENT"] = "test"
    if os.getenv("CI", False):
        os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@postgres:5432/dragons_test"
    else:
        os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5433/dragons_test"

    os.environ["AWS_REGION_NAME"] = "us-east-1"
    os.environ["SQS_QUEUE_URL"] = "-"
    os.environ["QUEUE_NAME"] = "-"
    os.environ["AWS_ACCESS_KEY"] = "-"
    os.environ["AWS_SECRET_KEY"] = "-"


def override_app_test_dependencies(app: FastAPI) -> None:
    test_engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
    test_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_session() -> AsyncSession:
        async with test_session_maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_session


@pytest.fixture(scope="session")
async def app() -> FastAPI:
    from app.main import create_app

    _app = create_app()
    override_app_test_dependencies(_app)

    yield _app


@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=TEST_HOST) as client:
        yield client


def override_dependency(app: FastAPI, dependency: Callable, override: Callable):
    """
    Overrides a dependency in the FastAPI app.

    :param app: The FastAPI app instance.
    :param dependency: The dependency to override.
    :param override: The override function or value.
    """
    app.dependency_overrides[dependency] = override


@pytest.fixture(scope="function")
async def session(app: FastAPI, _engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    override_dependency(app, get_db_session, lambda: session)

    try:
        yield session
    finally:
        await trans.rollback()
        await session.close()
        await connection.close()


@pytest.fixture(scope="session", autouse=True)
async def _engine() -> AsyncIterable[AsyncEngine]:
    settings = get_settings()
    alembic_config = get_alembic_config(settings.DATABASE_URL, script_location=find_migrations_script_location())

    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(lambda conn: downgrade(alembic_config, "base"))
        await connection.run_sync(lambda conn: upgrade(alembic_config, "head"))

    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(lambda conn: downgrade(alembic_config, "base"))
        await engine.dispose()


def find_migrations_script_location() -> str:
    """Help find script location if tests was run by debugger or any other way except writing 'pytest' in cli"""
    return os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent, "migrations")


@pytest.fixture(scope="session", params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param


@asynccontextmanager
async def sqs_mock():
    with mock_aws():
        sqs_client = boto3.client(
            "sqs",
            region_name="us-east-1",
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )

        mock_create_queue_response = sqs_client.create_queue(
            QueueName="dragon-test.fifo", Attributes={"FifoQueue": "true"}
        )
        queue_url = mock_create_queue_response["QueueUrl"]

        created_message_ids = []

        mock_message = SqsRecordModelFactory.build()

        yield queue_url, created_message_ids, mock_message
