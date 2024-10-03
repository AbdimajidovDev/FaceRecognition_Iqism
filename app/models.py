from datetime import datetime
from .database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, BLOB
# from fastapi import UploadFile


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String, unique=True, index=True)
    role = Column(String)
    image = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    def __repr__(self):
        return f'User {self.first_name} {self.last_name}'
