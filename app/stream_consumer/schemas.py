from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    event_name: str

    model_config = ConfigDict(from_attributes=True)
