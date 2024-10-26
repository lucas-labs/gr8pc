from abc import abstractmethod
from typing import Any, Union

from grpc.aio import ServicerContext

from .models import Message, Target


class BaseMiddleware:
    def __init__(self, target: Union['BaseMiddleware', Target]):
        self.target: Union['BaseMiddleware', Target] = target

    def get_kwargs(self, request: Message, context: ServicerContext) -> dict[str, Any]:
        if isinstance(self.target, BaseMiddleware):
            return {'request': request, 'context': context}
        kwargs: dict[str, Any] = {}
        if 'request' in self.target.func.__annotations__:
            kwargs['request'] = request
        if 'context' in self.target.func.__annotations__:
            kwargs['context'] = context
        return kwargs

    async def call_target(self, request: Message, context: ServicerContext) -> Message:
        return await self.target(**self.get_kwargs(request=request, context=context))

    @abstractmethod
    async def __call__(
        self: 'BaseMiddleware', request: Message, context: ServicerContext
    ) -> Message:
        return await self.call_target(request=request, context=context)
