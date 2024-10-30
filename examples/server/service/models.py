from datetime import datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from gr8pc import Message
from pydantic import Field

from .enums import Names


class PingRequest(Message):
    id: Optional[UUID] = Field(default_factory=uuid4)


class PingResponse(Message):
    id: Union[UUID, None]
    timestamp: datetime = Field(default_factory=datetime.now)


class ComplexModel(Message):
    name: Names


class ComplexRequest(Message):
    id: UUID | None
    model: ComplexModel | None


class ComplexResponse(Message):
    id: UUID
    model: ComplexModel | None
    model2: Union[ComplexModel, None]
    model3: Optional[ComplexModel]
