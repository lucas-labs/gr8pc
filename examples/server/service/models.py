from datetime import datetime
from uuid import UUID, uuid4

from gr8pc import Message
from pydantic import Field

from .enums import Names


class PingRequest(Message):
    id: UUID = Field(default_factory=uuid4)


class PingResponse(Message):
    id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)


class ComplexModel(Message):
    name: Names


class ComplexRequest(Message):
    id: UUID
    model: ComplexModel


class ComplexResponse(Message):
    id: UUID
    model: ComplexModel
