# Private Assistant Web UI

A comprehensive web interface for managing the Private Assistant ecosystem, built with FastAPI and React.

## Quick Start

### Launch Development Environment

**The devcontainer includes:**
- PostgreSQL (port 5432)
- Mosquitto MQTT Broker (ports 1883, 9001)
- MinIO Object Storage (ports 9000, 9001)

### Initial Setup

```bash
# Install backend dependencies
cd backend
uv sync

# Create database migrations
uv run alembic revision --autogenerate -m "Add picture display tables"

# Apply migrations
uv run alembic upgrade head

# Verify setup
uv run pytest

# Start backend server
uv run fastapi dev app/main.py
```

### Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **PostgreSQL**: localhost:5432 (postgres/changethis)
- **MQTT Broker**: localhost:1883

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, MQTT, MinIO clients
│   │   ├── models.py       # User/Item models
│   │   ├── models_commons.py   # Commons re-exports
│   │   ├── models_picture.py   # Picture display models
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

## Features

### Implemented ✅
- Backend foundation with SQLModel and FastAPI
- MQTT client for device registry updates
- MinIO client for image storage
- Commons model integration
- Devcontainer with PostgreSQL, MQTT, MinIO

### In Progress ⏳
- Device management API (CRUD with MQTT notifications)
- Picture display API (upload, manage, schedule)
- Monitoring API (skills and commands)
- React frontend pages

### Planned 📋
- OAuth integration (generic OIDC)
- Advanced scheduling system
- Bulk operations
- Kubernetes deployment manifests

## Development

### Backend Development

```bash
cd backend

# Run tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage report

# Type checking
uv run mypy app/

# Linting & formatting
uv run ruff check --fix .
uv run ruff format .
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Create .env file from template (first time only)
cp .env.example .env
# Edit .env and set VITE_API_URL (required) and optional OAuth settings

# Start dev server (automatically generates runtime config from .env)
npm run dev

# Generate API client (after backend changes)
npm run generate-client

# Run E2E tests
npm run test:e2e
```

**Runtime Configuration:**
- The frontend uses a runtime configuration system (not build-time)
- In development: `npm run dev` generates `public/config.js` from your `.env` file
- In production: The container generates `/config.js` from environment variables at startup
- This allows the same Docker image to be deployed to different environments

**Required Configuration:**
- `VITE_API_URL` - Backend API endpoint (e.g., `http://localhost:8000`)

**Optional OAuth Configuration:**
- `VITE_OAUTH_AUTHORITY` - OAuth/OIDC provider authority URL
- `VITE_OAUTH_CLIENT_ID` - OAuth client ID
- Both must be set together or OAuth will be disabled

### Database Management

```bash
cd backend

# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Database Seeding

Populate the database with test data using the seed script:

```bash
cd backend

# Seed the database (idempotent - safe to run multiple times)
uv run python -m scripts.seed.seed_database

# Clear existing data and reseed
uv run python -m scripts.seed.seed_database --clean

# Preview what would be seeded without making changes
uv run python -m scripts.seed.seed_database --dry-run
```

The seed script creates:
- 8 rooms (bedroom, living room, kitchen, etc.)
- 10 device types (light, switch, thermostat, etc.)
- 7 skills (climate, switch, scene, etc.)
- ~120 devices with fictional MQTT configurations
- 3 sample images for picture displays
- Picture display client device mappings

All seeded data uses fictional values (e.g., `fictional2mqtt/...` topics) to avoid exposing real device information.

## Environment Variables

### Backend Environment Variables

Key environment variables (see `backend/.env` for full list):

```bash
# Database
POSTGRES_SERVER=postgres  # or localhost
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

# MQTT
MQTT_BROKER_HOST=mosquitto  # or localhost
MQTT_BROKER_PORT=1883

# MinIO
MINIO_ENDPOINT=minio:9000  # or localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=assistant-images

# OAuth (optional)
DISABLE_OAUTH=true  # Set to false in production
```

### Frontend Environment Variables

Configuration variables (see `frontend/.env.example` for template):

```bash
# Backend API URL (REQUIRED)
VITE_API_URL=http://localhost:8000

# OAuth Configuration (OPTIONAL - both must be set together)
VITE_OAUTH_AUTHORITY=https://your-oauth-provider.com
VITE_OAUTH_CLIENT_ID=your-client-id
VITE_OAUTH_REDIRECT_URI=http://localhost:5173/oauth-callback
VITE_OAUTH_SCOPE=openid email profile
```

**Note:** In production (Docker/Kubernetes), frontend configuration is injected at runtime via environment variables, not baked into the image. See `frontend/Containerfile` for details.

## Architecture

### Database Integration
- Uses **private-assistant-commons-py** for shared models (Device, Room, DeviceType, Skill)
- Commons tables are external - managed by commons package migrations
- Web-UI owns: picture_display_image, picture_display_client_device tables

### MQTT Integration
- **Publish-only** client (no subscriptions)
- Publishes device updates to `assistant/device_registry/update`
- Skills listen for updates and reload configuration

### Storage
- **MinIO** for image storage (S3-compatible)
- Generates presigned URLs for frontend access
- Automatic bucket creation on startup
