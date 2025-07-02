from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)
    extension = Column(String(10), nullable=False)
    size = Column(Integer, nullable=False)
    path = Column(String(100), nullable=False)
    creation_date = Column(DateTime, default=func.now())
    update_date = Column(DateTime, default=func.now(), onupdate=func.now())
    comment = Column(String(200), nullable=True)

