from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateUser(BaseModel):
    username: Optional[str]
    first_name:Optional[str] = Field(min_length=2, max_length=55)
    last_name: Optional[str] = Field(min_length=2, max_length=55)
    email: Optional[str]
    role: Optional[str] = 'user'

    class Config:
        orm_mode = True

