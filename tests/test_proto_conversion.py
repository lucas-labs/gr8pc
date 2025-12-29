"""Tests for proto-pydantic conversion."""

from datetime import datetime
from uuid import uuid4

import pytest
from gr8pc.enums import ServiceModes
from gr8pc.method import MethodGRPC
from gr8pc.models import Method
from gr8pc.proto.enums import ProtoBufTypes
from gr8pc.proto.parser import parse_field_type, parse_type

from tests.test_services import (
    ComplexNestedModel,
    ComplexRequest,
    EchoRequest,
)


class TestTypeParser:
    """Test type parsing for proto generation."""

    def test_basic_type_mapping(self):
        """Test basic Python to Proto type mapping."""
        assert parse_type('test', int, int) == ProtoBufTypes.INT64
        assert parse_type('test', float, float) == ProtoBufTypes.DOUBLE
        assert parse_type('test', bool, bool) == ProtoBufTypes.BOOL
        assert parse_type('test', str, str) == ProtoBufTypes.STRING
        assert parse_type('test', bytes, bytes) == ProtoBufTypes.BYTES

    def test_special_type_mapping(self):
        """Test special type conversions."""
        from datetime import date, datetime, time
        from uuid import UUID

        assert parse_type('test', UUID, UUID) == ProtoBufTypes.STRING
        assert parse_type('test', datetime, datetime) == ProtoBufTypes.STRING
        assert parse_type('test', date, date) == ProtoBufTypes.STRING
        assert parse_type('test', time, time) == ProtoBufTypes.STRING

    def test_dict_type_mapping(self):
        """Test dict/map type mapping."""
        assert parse_type('test', dict, dict) == ProtoBufTypes.MAP

    def test_model_type_parsing(self):
        """Test Pydantic model type parsing."""
        result = parse_type('test', ComplexNestedModel, ComplexNestedModel)
        assert result == 'ComplexNestedModel'

    def test_field_type_parsing(self):
        """Test complete field type parsing."""
        result = parse_field_type('test_field', str)
        assert result['name'] == 'test_field'
        assert result['type'] == ProtoBufTypes.STRING

        result = parse_field_type('int_field', int)
        assert result['name'] == 'int_field'
        assert result['type'] == ProtoBufTypes.INT64


class TestProtoConversion:
    """Test proto-pydantic conversion methods."""

    @pytest.fixture
    def mock_method(self):
        """Create a mock method for testing."""
        from functools import partial

        async def dummy_func(self, request: EchoRequest) -> EchoRequest:
            return request

        class MockSelf:
            pass

        method = Method(
            mode=ServiceModes.DEFAULT,
            target=partial(dummy_func, MockSelf()),
            request=EchoRequest,
            response=EchoRequest,
            validation_request=EchoRequest,
            validation_response=EchoRequest,
            additional_messages={},
        )
        return method

    def test_pydantic_message_creation(self):
        """Test creating Pydantic messages."""
        msg = EchoRequest(text='hello', count=5)
        assert msg.text == 'hello'
        assert msg.count == 5

    def test_pydantic_message_dump(self):
        """Test dumping Pydantic messages."""
        msg = EchoRequest(text='hello', count=5)
        dump = msg.model_dump()

        assert dump['text'] == 'hello'
        assert dump['count'] == 5

    def test_pydantic_json_dump(self):
        """Test JSON serialization of messages."""
        msg = EchoRequest(text='test', count=3)
        json_data = msg.model_dump_json()

        assert 'test' in json_data
        assert '3' in json_data

    def test_pydantic_json_load(self):
        """Test JSON deserialization of messages."""
        json_data = '{"text": "test", "count": 3}'
        msg = EchoRequest.model_validate_json(json_data)

        assert msg.text == 'test'
        assert msg.count == 3


class TestComplexTypeConversion:
    """Test conversion of complex types."""

    def test_nested_model_creation(self):
        """Test creating nested models."""
        nested = ComplexNestedModel(name='test', value=42, timestamp=datetime.now())

        assert nested.name == 'test'
        assert nested.value == 42
        assert isinstance(nested.timestamp, datetime)

    def test_complex_request_with_nested(self):
        """Test complex request with nested models."""
        nested = ComplexNestedModel(name='nested', value=100, timestamp=datetime.now())

        test_uuid = uuid4()

        request = ComplexRequest(
            string_field='test',
            int_field=10,
            bool_field=True,
            float_field=3.14,
            optional_field='optional',
            list_field=['a', 'b'],
            dict_field={'k1': 1, 'k2': 2},
            nested=nested,
            uuid_field=test_uuid,
        )

        assert request.nested.name == 'nested'
        assert request.uuid_field == test_uuid
        assert request.list_field == ['a', 'b']
        assert request.dict_field == {'k1': 1, 'k2': 2}

    def test_optional_field_handling(self):
        """Test handling of optional fields."""
        nested = ComplexNestedModel(name='test', value=1, timestamp=datetime.now())

        # With optional field
        msg1 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            optional_field='present',
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg1.optional_field == 'present'

        # Without optional field (None)
        msg2 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            optional_field=None,
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg2.optional_field is None

    def test_list_field_handling(self):
        """Test handling of list fields."""
        nested = ComplexNestedModel(name='test', value=1, timestamp=datetime.now())

        # Empty list
        msg1 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            list_field=[],
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg1.list_field == []

        # List with items
        msg2 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            list_field=['a', 'b', 'c'],
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg2.list_field == ['a', 'b', 'c']
        assert len(msg2.list_field) == 3

    def test_dict_field_handling(self):
        """Test handling of dict/map fields."""
        nested = ComplexNestedModel(name='test', value=1, timestamp=datetime.now())

        # Empty dict
        msg1 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            dict_field={},
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg1.dict_field == {}

        # Dict with items
        msg2 = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            dict_field={'key1': 10, 'key2': 20},
            nested=nested,
            uuid_field=uuid4(),
        )
        assert msg2.dict_field == {'key1': 10, 'key2': 20}
        assert msg2.dict_field['key1'] == 10


class TestUUIDConversion:
    """Test UUID field conversion."""

    def test_uuid_field_storage(self):
        """Test that UUID fields are stored correctly."""
        nested = ComplexNestedModel(name='test', value=1, timestamp=datetime.now())

        test_uuid = uuid4()
        msg = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            nested=nested,
            uuid_field=test_uuid,
        )

        assert msg.uuid_field == test_uuid
        assert isinstance(msg.uuid_field, type(test_uuid))

    def test_uuid_json_serialization(self):
        """Test UUID serialization in JSON."""
        nested = ComplexNestedModel(name='test', value=1, timestamp=datetime.now())

        test_uuid = uuid4()
        msg = ComplexRequest(
            string_field='test',
            int_field=1,
            bool_field=True,
            float_field=1.0,
            nested=nested,
            uuid_field=test_uuid,
        )

        json_data = msg.model_dump_json()
        # UUID should be serialized as string
        assert str(test_uuid) in json_data


class TestDateTimeConversion:
    """Test datetime field conversion."""

    def test_datetime_field_storage(self):
        """Test that datetime fields are stored correctly."""
        now = datetime.now()
        nested = ComplexNestedModel(name='test', value=1, timestamp=now)

        assert nested.timestamp == now
        assert isinstance(nested.timestamp, datetime)

    def test_datetime_json_serialization(self):
        """Test datetime serialization."""
        now = datetime.now()
        nested = ComplexNestedModel(name='test', value=1, timestamp=now)

        json_data = nested.model_dump_json()
        # Datetime should be serialized as ISO format string
        assert isinstance(json_data, str)

        # Should be deserializable
        restored = ComplexNestedModel.model_validate_json(json_data)
        assert isinstance(restored.timestamp, datetime)


class TestBytesMode:
    """Test BYTES mode conversion."""

    def test_bytes_to_pydantic(self):
        """Test converting proto bytes to Pydantic."""

        # Create a simple proto message mock
        class MockProtoMessage:
            def __init__(self, data: bytes):
                self.bytes = data

        json_data = '{"text": "hello", "count": 5}'
        proto_msg = MockProtoMessage(json_data.encode())

        result = MethodGRPC.bytes_to_pydantic(proto_msg, EchoRequest)

        assert isinstance(result, EchoRequest)
        assert result.text == 'hello'
        assert result.count == 5

    def test_pydantic_to_bytes(self):
        """Test converting Pydantic to proto bytes."""
        msg = EchoRequest(text='test', count=3)

        # Create mock method with a mock protos module
        from functools import partial
        from types import ModuleType

        async def dummy_func(self, request: EchoRequest) -> EchoRequest:
            return request

        class MockSelf:
            pass

        class MockBytesMessage:
            def __init__(self, bytes: bytes):
                self.bytes = bytes

        # Create a mock module with BytesMessage
        mock_protos = ModuleType('mock_protos')
        mock_protos.BytesMessage = MockBytesMessage

        method = Method(
            mode=ServiceModes.DEFAULT,
            target=partial(dummy_func, MockSelf()),
            request=EchoRequest,
            response=EchoRequest,
            validation_request=EchoRequest,
            validation_response=EchoRequest,
            additional_messages={},
            protos=mock_protos,
        )

        result = MethodGRPC.pydantic_to_bytes(msg, method)

        assert hasattr(result, 'bytes')
        assert isinstance(result.bytes, bytes)

        # Should be valid JSON
        import json

        data = json.loads(result.bytes.decode())
        assert data['text'] == 'test'
        assert data['count'] == 3
