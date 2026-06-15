from pydantic import BaseModel, Field, EmailStr
from typing import List


class Activity(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int = Field(..., ge=0)
    participants: List[EmailStr] = []


class ActivityInDB(Activity):
    _id: str | None = None
