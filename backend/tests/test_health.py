"""Basic health check tests."""

import importlib.util


def test_app_package_exists() -> None:
    """Verify app package can be found."""
    spec = importlib.util.find_spec("app")
    assert spec is not None


def test_app_api_package_exists() -> None:
    """Verify app.api package can be found."""
    spec = importlib.util.find_spec("app.api")
    assert spec is not None
