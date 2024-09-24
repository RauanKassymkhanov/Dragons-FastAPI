from unittest.mock import patch, AsyncMock
from app.core.consumer.consumer import SignalHandler
from app.daily_reporter.consumer import consume_daily_report_trigger
from app.tests.conftest import sqs_mock
from app.tests.factory_schemas import DailyReportModelFactory


@patch("app.daily_reporter.consumer.upload_to_s3")
@patch("app.core.consumer.consumer.get_db_session")
@patch("app.daily_reporter.consumer.DailyReportService")
@patch("aiobotocore.session.AioSession.create_client")
@patch("app.daily_reporter.consumer.get_settings")
@patch.object(SignalHandler, "received_signal")
async def test_consume_daily_report_trigger(
    mock_received_signal,
    mock_get_settings,
    mock_create_client,
    mock_daily_report_service,
    mock_get_db_session,
    mock_upload_to_s3,
):
    mock_db_session = AsyncMock()

    async def mock_db_session_generator():
        yield mock_db_session

    mock_get_db_session.return_value = mock_db_session_generator()
    report = DailyReportModelFactory.build()
    mock_daily_report_service_instance = mock_daily_report_service.return_value
    mock_daily_report_service_instance.get_daily_report = AsyncMock(return_value=report)

    mock_sqs_client = AsyncMock()
    mock_create_client.return_value.__aenter__.return_value = mock_sqs_client

    async with sqs_mock() as (queue_url, created_message_ids, mock_message):
        mock_get_settings.return_value.TRIGGER_SQS_QUEUE_URL = queue_url

        mock_sqs_client.receive_message = AsyncMock(
            return_value={
                "Messages": [
                    {
                        "ReceiptHandle": mock_message.receiptHandle,
                    }
                ]
            }
        )

        mock_received_signal.side_effect = [False, True]

        await consume_daily_report_trigger()

        mock_daily_report_service_instance.get_daily_report.assert_called_once()

        mock_upload_to_s3.assert_called_once_with(report.model_dump())

        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl=queue_url, ReceiptHandle=mock_message.receiptHandle
        )
