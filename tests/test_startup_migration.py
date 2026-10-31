from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_app_runs_migrations_on_startup():
    with patch("app.main.command.upgrade") as mock_upgrade:
        with TestClient(app):
            pass

    mock_upgrade.assert_called_once()
