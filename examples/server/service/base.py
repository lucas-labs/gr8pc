from abc import abstractmethod

from gr8pc import BaseService

from .models import ComplexRequest, ComplexResponse, PingRequest, PingResponse


class BaseExampleService(BaseService):
    @abstractmethod
    async def ping(self: 'BaseExampleService', request: PingRequest) -> PingResponse: ...

    @abstractmethod
    async def complex(self: 'BaseExampleService', request: ComplexRequest) -> ComplexResponse: ...
