from typing import Callable
from app.base_service import BaseService
from app.core.consumer.client import get_sqs_client
from app.core.consumer.signal_handler import SignalHandler
from app.database import get_db_session


async def sqs_consumer(queue_url: str, service_cls: type[BaseService], message_processor: Callable) -> None:
    signal_handler = SignalHandler()

    async for sqs_client in get_sqs_client():
        while not signal_handler.received_signal():
            response = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=10)

            messages = response.get("Messages", [])

            if not messages:
                continue

            async for db_session in get_db_session():
                service = service_cls(session=db_session)
                for message in messages:
                    await message_processor(message, service)
                    await sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
