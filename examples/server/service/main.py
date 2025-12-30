from .base import BaseExampleService
from .models import ComplexRequest, ComplexResponse, PingRequest, PingResponse


class ExampleService(BaseExampleService):
    """Documentation of the entire ExampleService service."""

    async def ping(self: 'ExampleService', request: PingRequest) -> PingResponse:
        """Simple ping service that returns the same ID received in the request."""
        return PingResponse(id=request.id)

    async def complex(self: 'ExampleService', request: ComplexRequest) -> ComplexResponse:
        """Complex service demonstrating nested message handling."""
        rq = request.model_dump()

        return ComplexResponse(**rq, model2=request.model, model3=request.model)
