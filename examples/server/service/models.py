from datetime import datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from gr8pc import Message
from pydantic import Field

from .enums import Names


class PingRequest(Message):
    """A simple ping request model."""

    id: Optional[UUID] = Field(default_factory=uuid4)


class PingResponse(Message):
    """A simple ping response model."""

    id: Union[UUID, None]
    timestamp: datetime = Field(default_factory=datetime.now)


class ComplexModel(Message):
    """A complex nested model used in requests and responses."""

    name: Names


class ComplexRequest(Message):
    """A complex request model with optional nested message."""

    id: UUID | None
    model: ComplexModel | None


class ComplexResponse(Message):
    """A complex response model with nested messages."""

    id: UUID
    model: ComplexModel | None
    model2: Union[ComplexModel, None]
    model3: Optional[ComplexModel]
