"""API package exposing FastAPI app and server creation."""

from src.api.server import app, create_app

__all__ = ["app", "create_app"]
