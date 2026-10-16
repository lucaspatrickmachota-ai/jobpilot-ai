from tests.conftest import register_and_login


def test_register_login_and_me(client):
    headers = register_and_login(client)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "lucas@example.com"
    assert "password_hash" not in response.json()


def test_duplicate_registration_returns_conflict(client):
    register_and_login(client)
    response = client.post("/auth/register", json={"email": "lucas@example.com", "password": "Correct-Horse-Battery-42"})
    assert response.status_code == 409


def test_invalid_login_is_rejected(client):
    client.post("/auth/register", json={"email": "lucas@example.com", "password": "Correct-Horse-Battery-42"})
    response = client.post("/auth/login", json={"email": "lucas@example.com", "password": "wrong-password"})
    assert response.status_code == 401
