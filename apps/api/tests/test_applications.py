from tests.conftest import register_and_login


def test_application_crud_and_dashboard(client):
    headers = register_and_login(client)
    created = client.post("/applications", headers=headers, json={"company": "Example Labs", "position": "Junior Python Developer", "status": "SAVED"})
    assert created.status_code == 201, created.text
    application_id = created.json()["id"]
    assert client.get("/applications", headers=headers).json()[0]["company"] == "Example Labs"
    changed = client.patch(f"/applications/{application_id}", headers=headers, json={"status": "APPLIED"})
    assert changed.status_code == 200
    assert changed.json()["status"] == "APPLIED"
    stats = client.get("/dashboard/stats", headers=headers).json()
    assert stats["total"] == 1 and stats["applied"] == 1
    assert client.delete(f"/applications/{application_id}", headers=headers).status_code == 204


def test_user_cannot_access_another_users_application(client):
    owner_headers = register_and_login(client, "owner@example.com")
    intruder_headers = register_and_login(client, "intruder@example.com")
    created = client.post("/applications", headers=owner_headers, json={"company": "Private Co", "position": "Engineer"})
    application_id = created.json()["id"]
    assert client.get(f"/applications/{application_id}", headers=intruder_headers).status_code == 404
    assert client.patch(f"/applications/{application_id}", headers=intruder_headers, json={"status": "OFFER"}).status_code == 404
    assert client.delete(f"/applications/{application_id}", headers=intruder_headers).status_code == 404


def test_protected_endpoints_require_auth(client):
    assert client.get("/applications").status_code == 401
    assert client.get("/dashboard/stats").status_code == 401


def test_required_application_fields_cannot_be_set_to_null(client):
    headers = register_and_login(client)
    created = client.post("/applications", headers=headers, json={"company": "Example Labs", "position": "Engineer"})
    application_id = created.json()["id"]
    response = client.patch(f"/applications/{application_id}", headers=headers, json={"company": None})
    assert response.status_code == 422
