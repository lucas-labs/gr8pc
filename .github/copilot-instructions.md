# Copilot Instructions for gr8pc

## Project Overview

**gr8pc** is a high-level gRPC framework wrapper for Python 3.11+. It provides async-first abstractions over gRPC, combining Pydantic for validation with protocol buffers for serialization. The project is split into two packages:
- **gr8pc**: Core async gRPC server/client framework with Pydantic-based message validation
- **gr8gen**: CLI tool for generating `.proto` files from Python service definitions (uses Jinja templating)

## Architecture & Key Patterns

### Service Definition Pattern
Services inherit from `BaseService` and use async method handlers that accept Pydantic `Message` models:
- Methods are auto-discovered by the metaclass `BaseServiceMeta` 
- Each method's signature is introspected to extract request/response types
- Support two modes: `ServiceModes.DEFAULT` (standard) and `ServiceModes.BYTES` (for binary data)
- Example: [examples/server/service/main.py](examples/server/service/main.py#L5-L11)

### Message & Field System
- `Message` base class: Pydantic `BaseModel` with proto-aware field analysis
- `Field` class introspects Pydantic fields to determine proto types (int64, string, bool, bytes, map, nested messages, repeated fields)
- Type parsing logic: [packages/gr8pc/src/gr8pc/proto/parser.py](packages/gr8pc/src/gr8pc/proto/parser.py) - maps Python types to ProtoBuf types (UUID→string, datetime→string, dict→map, List[T]→repeated)
- Nested messages automatically discovered via `get_additional_messages()` - no manual registration needed

### Proto File Generation Workflow
1. **Development-time**: Define Python service class with Pydantic Message types
2. **Run gr8gen**: `gr8gen --output proto/ -s myapp.service.MyService` generates `.proto` file
3. **Runtime**: `BaseService.init_protos_and_services()` loads compiled proto descriptors using `grpc.protos_and_services()`
4. **Key constraint**: Proto files must exist on disk; runtime generation is explicitly disabled

### Server Architecture
- `GrpcServer`: Async gRPC server wrapper ([packages/gr8pc/src/gr8pc/server/base.py](packages/gr8pc/src/gr8pc/server/base.py))
  - Accepts middleware stack and lifecycle hooks (`on_startup`, `on_shutdown`)
  - Supports multiple services via `add_service()`
  - Uses `ServerInterceptor` for unified error handling
- `ServerInterceptor`: Async middleware ([packages/gr8pc/src/gr8pc/interceptor.py](packages/gr8pc/src/gr8pc/interceptor.py))
  - Catches custom exceptions (`GrpcException`, `SendEmpty`, `RunTimeServerError`, `ValidationError`)
  - Maps to gRPC status codes and details
  - Optional access logging in background asyncio tasks

### Middleware System
- Base: `BaseMiddleware` - chain pattern with `call_target()`
- Custom middleware: inspect method annotations to optionally inject `request` and `context` parameters
- Middleware wrapping: each middleware can wrap another middleware or the final handler
- Applied per-service: set via service metaclass

### Proto-Pydantic Conversion
- **proto→pydantic**: `MethodGRPC.proto_to_pydantic()` - recursively converts ProtoBuf messages to Pydantic models
- **pydantic→proto**: `MethodGRPC.pydantic_to_proto()` - recursively converts Pydantic to ProtoBuf, with optional exclusions (e.g., BYTES fields)
- Handles repeated fields, nested messages, and type coercion

### Error Handling
Custom exceptions mapped to gRPC status codes:
- `GrpcException`: Explicit gRPC errors with `status_code` and `details`
- `SendEmpty`: Aborts with ABORTED status
- `RunTimeServerError`: Custom status code; INTERNAL→"Internal Server Error" sanitization
- `ValidationError` (Pydantic): Returns INVALID_ARGUMENT with error JSON

## Development Workflow

### Project Structure
- **Monorepo** via `uv` workspace: `packages/gr8pc` and `packages/gr8gen` are independent projects
- **Root** `pyproject.toml`: aggregates both; dev dependencies (ruff) shared
- **Python 3.11+** required; Pydantic <3, grpcio>=1.67.1, grpc-interceptor>=0.15.4

### Key Commands
```bash
# Install workspace (both packages)
uv sync

# Generate proto files from service definitions
uv run -p gr8gen gr8gen --output ./examples/server/proto --svcs examples.server.service.main.ExampleService

# Run example server
cd examples/server
python server.py

# Linting
uv run ruff check packages/

# Format
uv run ruff format packages/
```

### Status Code Mapping
- Always return/raise with gRPC `StatusCode` intent (e.g., INVALID_ARGUMENT for bad input)
- Framework sanitizes INTERNAL errors to hide implementation details

