from uuid import uuid4
from sqlalchemy import insert
from app.base_service import BaseService
from app.stream_consumer.schemas import EventCreate
from app.models.events import EventModel


class EventService(BaseService):
    async def create_event(self, new_event: EventCreate) -> EventModel:
        new_event_id = str(uuid4())

        query = insert(EventModel).values(id=new_event_id, event_name=new_event.event_name).returning(EventModel)

        result = await self._session.execute(query)

        created_event = result.scalar_one()

        return created_event
