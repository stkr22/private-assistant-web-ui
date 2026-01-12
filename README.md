# Private Assistant Web UI

A comprehensive web interface for managing the Private Assistant ecosystem, built with FastAPI and React.

## Quick Start

### Prerequisites

Open this project in a devcontainer (VS Code or GitHub Codespaces). The devcontainer provides:
- PostgreSQL (port 5432)
- Mosquitto MQTT Broker (port 1883)
- MinIO Object Storage (ports 9000, 9001)

### Initial Setup

```bash
# 1. Backend setup
cd backend
uv sync

# 2. Create database tables and seed with test data
uv run alembic upgrade head
uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from private_assistant_commons.database.models import GlobalDevice, Room, DeviceType, Skill
from app.models import User
from app.core.config import get_settings
async def create():
    engine = create_async_engine(str(get_settings().SQLALCHEMY_DATABASE_URI))
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()
asyncio.run(create())
"
uv run python -m scripts.seed.seed_database

# 3. Start backend (in one terminal)
uv run fastapi dev app/main.py

# 4. Frontend setup (in another terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Default Credentials

- **Web UI**: http://localhost:5173
  - Email: `admin@example.com`
  - Password: `changethis`
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, MQTT, MinIO clients
│   │   ├── models.py       # SQLModel definitions
│   │   └── alembic/        # Database migrations
│   └── pyproject.toml
├── frontend/               # React frontend
│   ├── src/
│   │   ├── routes/        # TanStack Router pages
│   │   ├── components/    # React components
│   │   └── client/        # Auto-generated API client
│   └── package.json
├── .devcontainer/         # Dev environment configuration
```

## Development

### Backend

```bash
cd backend

# Start server
uv run fastapi dev app/main.py

# Run tests
uv run pytest

# Type checking
uv run mypy app/

# Linting & formatting
uv run ruff check --fix .
uv run ruff format .
```

### Frontend

```bash
cd frontend

# Start dev server
npm run dev

# Generate API client (after backend OpenAPI changes)
npm run generate-client

# Run E2E tests
npm run test:e2e
```

### Database

```bash
cd backend

# Apply migrations
uv run alembic upgrade head

# Create new migration (after model changes)
uv run alembic revision --autogenerate -m "Description"

# Rollback one migration
uv run alembic downgrade -1

# Reseed database
uv run python -m scripts.seed.seed_database --clean
```

The seed script creates test data: 8 rooms, 10 device types, 7 skills, ~120 devices, 3 images, and device display states. All data uses fictional values (e.g., `fictional2mqtt/...` topics).

## Environment Variables

Environment variables are pre-configured in the devcontainer. For reference:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | postgres | Database host |
| `POSTGRES_PORT` | 5432 | Database port |
| `POSTGRES_DB` | app | Database name |
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | changethis | Database password |
| `MQTT_HOST` | mosquitto | MQTT broker host |
| `MQTT_PORT` | 1883 | MQTT broker port |
| `MINIO_ENDPOINT` | minio:9000 | MinIO endpoint |
| `MINIO_ACCESS_KEY` | minioadmin | MinIO access key |
| `MINIO_SECRET_KEY` | minioadmin | MinIO secret key |
| `FIRST_SUPERUSER` | admin@example.com | Initial admin email |
| `FIRST_SUPERUSER_PASSWORD` | changethis | Initial admin password |

Frontend configuration (`frontend/.env`):
- `VITE_API_URL` - Backend API endpoint (required, e.g., `http://localhost:8000`)
- `VITE_OAUTH_AUTHORITY` - OAuth provider URL (optional)
- `VITE_OAUTH_CLIENT_ID` - OAuth client ID (optional)

## Architecture

### Database

- **Commons tables** (`rooms`, `device_types`, `skills`, `global_devices`) - Shared models from `private-assistant-commons-py`. In development, created via `SQLModel.metadata.create_all()`.
- **App tables** (`user`, `images`, `device_display_states`, `immich_sync_jobs`) - Managed by Alembic migrations.

### MQTT

Publish-only client that sends device updates to `assistant/device_registry/update`. Skills subscribe to this topic to reload configuration.

### Storage

MinIO (S3-compatible) for image storage with presigned URLs for frontend access.
