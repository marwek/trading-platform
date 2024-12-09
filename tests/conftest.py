import os

import pytest
from fastapi.testclient import TestClient

from server.main import app, order_repository

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="function")
def client():
    # Setup: Create a new TestClient instance
    with TestClient(app=app, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(autouse=True)
def clear_repository():
    """
    Automatically clean the repository before each test.
    """
    # Before test: Clear the repository
    order_repository._orders.clear()

    yield
