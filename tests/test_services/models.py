"""Test service models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from gr8pc import Message
from pydantic import Field


class EchoRequest(Message):
    """Simple echo request."""

    text: str
    count: int = 1


class EchoResponse(Message):
    """Simple echo response."""

    text: str
    count: int


class ComplexNestedModel(Message):
    """Nested model for testing."""

    name: str
    value: int
    timestamp: datetime


class ComplexRequest(Message):
    """Complex request with various types."""

    string_field: str
    int_field: int
    bool_field: bool
    float_field: float
    optional_field: Optional[str] = None
    list_field: list[str] = Field(default_factory=list)
    dict_field: dict[str, int] = Field(default_factory=dict)
    nested: ComplexNestedModel
    uuid_field: UUID


class ComplexResponse(Message):
    """Complex response mirroring request."""

    string_field: str
    int_field: int
    bool_field: bool
    float_field: float
    optional_field: Optional[str] = None
    list_field: list[str]
    dict_field: dict[str, int]
    nested: ComplexNestedModel
    uuid_field: UUID
    processed: bool = True


class EmptyRequest(Message):
    """Empty request for testing."""

    pass


class EmptyResponse(Message):
    """Empty response for testing."""

    pass


class BytesRequest(Message):
    """Request with bytes data."""

    data: bytes
    metadata: str


class BytesResponse(Message):
    """Response with bytes data."""

    data: bytes
    size: int
