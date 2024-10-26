# activate loggers
import logging

from gr8pc import GrpcServer
from service.main import ExampleService

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    server: GrpcServer = GrpcServer(
        name='ExampleGrpc',
        services=(ExampleService,),
        access_log=True,
    )

    # or...
    # server.add_service(service=ExampleService)

    server.run()


if __name__ == '__main__':
    main()
