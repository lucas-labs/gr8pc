"""Tests for server.run() - the main entry point of the library."""

import threading
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from gr8pc import GrpcServer
from grpc import RpcError, StatusCode

from tests.test_services import (
    ComplexNestedModel,
    ComplexRequest,
    EchoRequest,
    EchoResponse,
    ExampleService,
)


@pytest.fixture(scope='module')
def running_server(proto_dir: Path):
    """Start server using run() in a background thread - the real-world usage pattern."""
    server = GrpcServer(
        name='TestServer',
        port=50070,
        proto_dir=proto_dir,
        services=(ExampleService,),
        access_log=False,
    )

    # Start server in daemon thread (like production would)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    time.sleep(0.5)

    yield server

    # Stop server cleanly
    if server.loop and server.loop.is_running():
        server.loop.call_soon_threadsafe(server.loop.stop)
    time.sleep(0.2)


@pytest.mark.asyncio
async def test_run_server_echo(running_server: GrpcServer, proto_dir: Path):
    """Test that server.run() actually serves requests."""
    # Create client connecting to the running server
    client = ExampleService(port=running_server.port, proto_dir=proto_dir)

    # Make a request to the running server
    response = await client.echo(request=EchoRequest(text='hello', count=3))

    assert isinstance(response, EchoResponse)
    assert response.text == 'hellohellohello'
    assert response.count == 3


@pytest.mark.asyncio
async def test_run_server_complex_types(running_server: GrpcServer, proto_dir: Path):
    """Test complex types through the running server."""
    client = ExampleService(port=running_server.port, proto_dir=proto_dir)

    test_uuid = uuid4()
    nested = ComplexNestedModel(name='nested_test', value=123, timestamp=datetime.now())

    request = ComplexRequest(
        string_field='test_data',
        int_field=42,
        bool_field=True,
        float_field=3.14159,
        optional_field='present',
        list_field=['item1', 'item2'],
        dict_field={'key1': 100, 'key2': 200},
        nested=nested,
        uuid_field=test_uuid,
    )

    response = await client.complex(request=request)

    # Verify the service processed the request correctly
    assert response.string_field == 'TEST_DATA'
    assert response.int_field == 84
    assert response.bool_field is False
    assert response.dict_field == {'key1': 100, 'key2': 200, 'extra': 999}
    assert response.uuid_field == test_uuid


@pytest.mark.asyncio
async def test_error_handling(running_server: GrpcServer, proto_dir: Path):
    """Test that errors are properly handled and sanitized."""
    client = ExampleService(port=running_server.port, proto_dir=proto_dir)

    with pytest.raises(RpcError) as exc_info:
        await client.raise_error(request=EchoRequest(text='runtime_error', count=1))

    # INTERNAL errors should be sanitized
    assert exc_info.value.code() == StatusCode.INTERNAL
    assert exc_info.value.details() == 'Internal Server Error'
