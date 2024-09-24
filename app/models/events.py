import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_name: Mapped[str]
