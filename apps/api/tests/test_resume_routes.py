from fastapi.testclient import TestClient


def test_resume_requires_authentication(client: TestClient) -> None:
    response = client.get("/resume")
    assert response.status_code == 401


def test_resume_upload_rejects_non_pdf(authenticated_client: TestClient) -> None:
    response = authenticated_client.post("/resume", files={"file": ("resume.pdf", b"not a pdf", "application/pdf")})
    assert response.status_code == 415


def test_job_analyzer_requires_authentication(client: TestClient) -> None:
    response = client.post("/job-analyzer", json={"description": "A sufficiently long job description that contains at least thirty characters."})
    assert response.status_code == 401
