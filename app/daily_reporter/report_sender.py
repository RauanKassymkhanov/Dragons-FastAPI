import json
from datetime import datetime
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from app.config import get_settings


async def get_s3_client() -> AioBaseClient:
    session = AioSession()
    settings = get_settings()

    async with session.create_client(
        "s3",
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    ) as client:
        yield client


async def upload_to_s3(event_data: dict) -> None:
    settings = get_settings()
    async for s3_client in get_s3_client():
        file_content = json.dumps(event_data)
        date = datetime.now().strftime("%Y-%m-%d")
        file_name = f"daily_report({date}).json"
        await s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME, Key=file_name, Body=file_content, ContentType="application/json"
        )
