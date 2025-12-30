"""Shared test fixtures for gr8pc tests."""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

import pytest
from gr8pc import GrpcServer
from grpc.aio import Channel, insecure_channel


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def proto_dir() -> Path:
    """Proto directory containing .proto files."""
    return Path('tests/proto')


@pytest.fixture
async def grpc_server(proto_dir: Path) -> AsyncGenerator[GrpcServer, None]:
    """Create and start a gRPC server for testing."""
    server = GrpcServer(port=50051, proto_dir=proto_dir)

    # Start server in background
    server.server.add_insecure_port(f'{server.host}:{server.port}')
    await server.server.start()

    yield server

    # Cleanup
    await server.server.stop(grace=0.5)


@pytest.fixture
async def grpc_channel() -> AsyncGenerator[Channel, None]:
    """Create a gRPC channel for client testing."""
    channel = insecure_channel('localhost:50051')
    yield channel
    await channel.close()
