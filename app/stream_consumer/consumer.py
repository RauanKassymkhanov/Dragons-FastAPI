import json
from app.config import get_settings
from app.core.consumer.consumer import sqs_consumer
from app.stream_consumer.schemas import EventCreate
from app.stream_consumer.service import EventService


async def process_stream_message(message: dict, service: EventService) -> None:
    message_body = json.loads(message["Body"])
    new_event = EventCreate(event_name=message_body["eventName"])
    await service.create_event(new_event=new_event)


async def consume_stream_messages() -> None:
    settings = get_settings()
    queue_url = settings.SQS_QUEUE_URL
    await sqs_consumer(queue_url, EventService, process_stream_message)
