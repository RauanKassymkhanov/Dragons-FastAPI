from app.config import get_settings
from app.core.consumer.consumer import sqs_consumer
from app.daily_reporter.report_sender import upload_to_s3
from app.daily_reporter.service import DailyReportService


async def process_daily_report_message(message: dict, service: DailyReportService) -> None:
    daily_report = await service.get_daily_report()
    await upload_to_s3(daily_report.model_dump())


async def consume_daily_report_trigger() -> None:
    settings = get_settings()
    queue_url = settings.TRIGGER_SQS_QUEUE_URL
    await sqs_consumer(queue_url, DailyReportService, process_daily_report_message)
