import json
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from app.config import get_settings
from app.consumer.schemas import EventCreate
from app.consumer.service import EventService
from app.consumer.signal_handler import SignalHandler
from app.database import get_db_session


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


async def consume_sqs_messages() -> None:
    signal_handler = SignalHandler()

    async for sqs_client in get_sqs_client():
        settings = get_settings()
        queue_url = settings.SQS_QUEUE_URL

        while not signal_handler.received_signal():
            response = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=10)

            messages = response.get("Messages", [])

            if not messages:
                continue

            async for db_session in get_db_session():
                event_service = EventService(session=db_session)
                for message in messages:
                    message_body = json.loads(message["Body"])
                    new_event = EventCreate(event_name=message_body["eventName"])
                    await event_service.create_event(new_event=new_event)
                    await sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
