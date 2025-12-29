"""Test service definitions."""

from gr8pc import BaseService, ServiceModes
from gr8pc.exceptions import RunTimeServerError, SendEmpty
from grpc import StatusCode

from .models import (
    BytesRequest,
    BytesResponse,
    ComplexRequest,
    ComplexResponse,
    EchoRequest,
    EchoResponse,
    EmptyRequest,
    EmptyResponse,
)


class ExampleService(BaseService):
    """Example service with various method types."""

    name = 'ExampleService'

    async def echo(self, request: EchoRequest) -> EchoResponse:
        """Simple echo method."""
        return EchoResponse(text=request.text * request.count, count=request.count)

    async def complex(self, request: ComplexRequest) -> ComplexResponse:
        """Complex method with various field types."""
        return ComplexResponse(
            string_field=request.string_field.upper(),
            int_field=request.int_field * 2,
            bool_field=not request.bool_field,
            float_field=request.float_field * 1.5,
            optional_field=request.optional_field,
            list_field=request.list_field + ['extra'],
            dict_field={**request.dict_field, 'extra': 999},
            nested=request.nested,
            uuid_field=request.uuid_field,
            processed=True,
        )

    async def empty(self, request: EmptyRequest) -> EmptyResponse:
        """Method with empty request/response."""
        return EmptyResponse()

    async def raise_error(self, request: EchoRequest) -> EchoResponse:
        """Method that raises an error."""
        if request.text == 'runtime_error':
            raise RunTimeServerError(status_code=StatusCode.INTERNAL, details='Intentional error')
        elif request.text == 'send_empty':
            raise SendEmpty('Empty response requested')
        else:
            raise ValueError('Invalid input')

    async def bytes_method(self, request: BytesRequest) -> BytesResponse:
        """Method handling bytes data."""
        return BytesResponse(data=request.data, size=len(request.data))


class ExampleBytesService(BaseService):
    """Example service using BYTES mode."""

    name = 'ExampleBytesService'
    mode = ServiceModes.BYTES

    async def process_bytes(self, request: BytesRequest) -> BytesResponse:
        """Process bytes in BYTES mode."""
        return BytesResponse(
            data=request.data[::-1],  # Reverse bytes
            size=len(request.data),
        )
