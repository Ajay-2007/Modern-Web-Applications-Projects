import datetime as dt
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Column, Table, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSON


from database.core import metadata
from database.utils import uuid_pk, created_at, PyUUID


notification = Table(
    "notification", metadata,
    uuid_pk(),
    created_at(index=True),
    Column("profile_id", PyUUID,
            ForeignKey("profile.id", ondelete="CASCADE"),
            nullable=False),
    Column("data", JSON, nulllable=False),
    Column("read", Boolean, server_default="false"),
    Column("visited", Boolean, server_default="false")
)


class NotificationData(BaseModel):
    event: str
    payload: Dict

class Notification(BaseModel):
    id: Optional[UUID]
    created_at: Optional[dt.datetime]
    profile_id: UUID
    data: NotificationData
    read: bool = False
    visited: bool = False
    