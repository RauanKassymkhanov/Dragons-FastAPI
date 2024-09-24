from unittest.mock import patch, AsyncMock
from app.consumer.consumer import consume_sqs_messages
from app.consumer.schemas import EventCreate
from app.consumer.consumer import SignalHandler
from app.tests.conftest import sqs_mock


@patch("app.consumer.consumer.get_db_session")
@patch("app.consumer.consumer.EventService")
@patch("aiobotocore.session.AioSession.create_client")
@patch("app.consumer.consumer.get_settings")
@patch.object(SignalHandler, "received_signal")
async def test_consume_sqs_messages(
    mock_received_signal, mock_get_settings, mock_create_client, mock_event_service, mock_get_db_session
):
    mock_db_session = AsyncMock()

    async def mock_db_session_generator():
        yield mock_db_session

    mock_get_db_session.return_value = mock_db_session_generator()

    mock_event_service_instance = mock_event_service.return_value
    mock_event_service_instance.create_event = AsyncMock()

    mock_sqs_client = AsyncMock()
    mock_create_client.return_value.__aenter__.return_value = mock_sqs_client

    async with sqs_mock() as (queue_url, created_message_ids, mock_message):
        mock_get_settings.return_value.SQS_QUEUE_URL = queue_url

        mock_sqs_client.receive_message = AsyncMock(
            return_value={
                "Messages": [
                    {
                        "MessageId": mock_message.messageId,
                        "ReceiptHandle": mock_message.receiptHandle,
                        "Body": mock_message.body.model_dump_json(),
                    }
                ]
            }
        )
        mock_received_signal.side_effect = [False, True]
        await consume_sqs_messages()

        mock_event_service_instance.create_event.assert_called_once_with(
            new_event=EventCreate(event_name=mock_message.body.eventName)
        )
        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl=queue_url, ReceiptHandle=mock_message.receiptHandle
        )
