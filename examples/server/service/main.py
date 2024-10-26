from .base import BaseExampleService
from .models import ComplexRequest, ComplexResponse, PingRequest, PingResponse


class ExampleService(BaseExampleService):
    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        return PingResponse(id=request.id)

    async def complex(self: 'ExampleService', request: ComplexRequest) -> ComplexResponse:
        return ComplexResponse(**request.model_dump())