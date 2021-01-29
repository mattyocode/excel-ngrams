"""Base pytest fixtures."""
from _pytest.config import Config


def pytest_configure(config: Config) -> None:
    """Marks end to end tests."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
