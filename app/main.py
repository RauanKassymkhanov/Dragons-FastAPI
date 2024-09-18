import asyncio
from contextlib import asynccontextmanager
from alembic import command
from fastapi import FastAPI
from app.config import get_settings
from app.consumer.consumer import consume_sqs_messages
from app.database import get_alembic_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    alembic_cfg = get_alembic_config(settings.DATABASE_URL, "app/migrations")
    command.upgrade(alembic_cfg, "head")
    startup_event()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    return app


app = create_app()


def startup_event() -> None:
    asyncio.create_task(consume_sqs_messages())
