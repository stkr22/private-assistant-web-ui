"""Basic health check tests."""

import importlib.util
from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


def test_app_package_exists() -> None:
    """Verify app package can be found."""
    spec = importlib.util.find_spec("app")
    assert spec is not None


def test_app_api_package_exists() -> None:
    """Verify app.api package can be found."""
    spec = importlib.util.find_spec("app.api")
    assert spec is not None


def test_health_check_endpoint() -> None:
    """Verify health check endpoint returns correct response."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # Verify response structure and value
    assert "status" in data
    assert data["status"] == "ok"
