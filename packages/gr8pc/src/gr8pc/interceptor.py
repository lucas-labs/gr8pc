import asyncio
import logging
import re

from google.protobuf.message import Message
from grpc import StatusCode
from grpc.aio import ServicerContext
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor
from pydantic import ValidationError

from .exceptions import RunTimeServerError, SendEmpty
from .method import ServerMethodGRPC

logger = logging.getLogger(__name__)


class ServerInterceptor(AsyncServerInterceptor):
    def __init__(self: 'ServerInterceptor', access_log: bool = False) -> None:
        self.access_log = access_log

    async def intercept(
        self: 'ServerInterceptor',
        route: ServerMethodGRPC,
        message: Message,
        context: ServicerContext,
        method_name: str,
    ) -> Message | None:
        response: Message | None = None

        try:
            response = await route(message=message, context=context)
            return response
        except GrpcException as grpc_exc:
            context.set_code(grpc_exc.status_code)
            context.set_details(grpc_exc.details)
        except SendEmpty as exc:
            context.set_code(StatusCode.ABORTED)
            context.set_details(exc.text)
        except RunTimeServerError as exc:
            logger.error(exc)
            context.set_code(exc.status_code)
            context.set_details(
                'Internal Server Error' if exc.status_code == StatusCode.INTERNAL else exc.details
            )
        except ValidationError as exc:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(exc.json())
        except Exception as exc:
            logger.exception(exc)
            context.set_code(StatusCode.INTERNAL)
            context.set_details('Internal Server Error')
        finally:
            if self.access_log:
                # log the request in a separate asyncio task
                asyncio.create_task(
                    access_log_task(
                        context=context,
                        route=route,
                        method_name=method_name,
                        response=response or None,
                    )
                )


async def access_log_task(
    context: ServicerContext, route: ServerMethodGRPC, method_name: str, response: Message | None
) -> None:
    code = context.code() or StatusCode.OK
    det = context.details()

    if code is not StatusCode.OK:
        msg = f'{context.peer()} - {route.__qualname__} {{{method_name}}} | {code} | {det}'
    else:
        msg = f'{context.peer()} - {route.__qualname__} {{{method_name}}} | {StatusCode.OK} |'
        resp = re.sub(r'\n+$', '', f'{response or ""}')
        resp = re.sub(r'(?m)^', '  | ', resp)
        msg = f'{msg}\n{resp}'

    logger.debug(f'{msg}')
