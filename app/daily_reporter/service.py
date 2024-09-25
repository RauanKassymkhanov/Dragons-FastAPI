from sqlalchemy import select
from app.base_service import BaseService
from app.daily_reporter.schemas import DailyReportModel
from app.models.events import EventModel


class DailyReportService(BaseService):
    async def get_daily_report(self) -> DailyReportModel:
        query = select(EventModel)
        result = await self._session.execute(query)
        events = result.scalars().all()

        report = DailyReportModel()

        for event in events:
            if event.event_name == "INSERT":
                report.Insert += 1
            elif event.event_name == "REMOVE":
                report.Remove += 1
            elif event.event_name == "MODIFY":
                report.Modify += 1

        return report
