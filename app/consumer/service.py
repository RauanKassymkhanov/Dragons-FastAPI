from uuid import uuid4
from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.consumer.schemas import EventCreate
from app.database import get_db_session
from app.models.events import EventModel


class EventService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    async def create_event(self, new_event: EventCreate) -> EventModel:
        new_event_id = str(uuid4())

        query = insert(EventModel).values(id=new_event_id, event_name=new_event.event_name).returning(EventModel)

        result = await self._session.execute(query)

        created_event = result.scalar_one()

        return created_event
