import os

os.environ["DATABASE_URL"] = "sqlite:///./test-jobpilot.db"
os.environ["JWT_SECRET"] = "test-only-secret-that-is-long-enough"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Application, User  # noqa: F401


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def register_and_login(client, email="lucas@example.com"):
    response = client.post("/auth/register", json={"email": email, "password": "Correct-Horse-Battery-42"})
    assert response.status_code == 201, response.text
    login = client.post("/auth/login", json={"email": email, "password": "Correct-Horse-Battery-42"})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture()
def authenticated_client(client):
    from tests.conftest import register_and_login
    client.headers.update(register_and_login(client))
    return client
