from pydantic import BaseModel, ConfigDict


class DailyReportModel(BaseModel):
    Insert: int = 0
    Remove: int = 0
    Modify: int = 0

    model_config = ConfigDict(from_attributes=True)
