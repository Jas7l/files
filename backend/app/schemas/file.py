from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# For PATCH methods
class FileUpdate(BaseModel):
    name: Optional[str] = None
    path: Optional[str] = None
    comment: Optional[str] = None


# For response
class FileRead(BaseModel):
    id: int
    name: str
    extension: str
    size: int
    path: str
    creation_date: datetime
    update_date: datetime
    comment: Optional[str] = None

    # Input from SQLAlchemy-object
    class Config:
        from_attributes = True
