from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from app.config import get_settings


async def get_sqs_client() -> AioBaseClient:
    session = AioSession()
    settings = get_settings()
    async with session.create_client(
        "sqs",
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    ) as client:
        yield client
