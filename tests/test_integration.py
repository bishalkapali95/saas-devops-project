"""
Integration Tests for Flask Password-Reset API
----------------------------------------------
DevOps Context:
Integration tests verify that HTTP endpoints, request parsing,
response formatting, status codes, and business logic coordinate properly
through the web framework.
These tests simulate real client HTTP requests using Flask's test client.
"""

import pytest
from app import create_app
from app.password_reset import reset_service


@pytest.fixture
def client():
    """Creates a Flask test client with an isolated in-memory
    test environment."""
    app = create_app({"TESTING": True})
    reset_service.clear_store()
    with app.test_client() as test_client:
        yield test_client
    reset_service.clear_store()


def test_health_check_endpoint(client):
    """
    Test GET /health
    Expectation: HTTP 200 with JSON payload {"status": "healthy"}
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data == {"status": "healthy"}


def test_password_reset_success(client):
    """
    Test POST /password-reset with valid email
    Expectation: HTTP 200 with generated token and expiry metadata
    """
    payload = {"email": "student@example.com"}
    response = client.post("/password-reset", json=payload)

    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "success"
    assert "token" in data
    assert len(data["token"]) > 20
    assert data["expires_in_minutes"] == 15


def test_password_reset_missing_email(client):
    """
    Test POST /password-reset with missing email key
    Expectation: HTTP 400 Bad Request
    """
    response = client.post("/password-reset", json={})

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "error"
    assert "Missing 'email' field" in data["message"]


def test_password_reset_empty_email(client):
    """
    Test POST /password-reset with empty or whitespace email
    Expectation: HTTP 400 Bad Request
    """
    response = client.post("/password-reset", json={"email": "   "})

    assert response.status_code == 400
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "error"
    assert "Email field cannot be empty" in data["message"]


def test_password_reset_validate_success(client):
    """
    Test POST /password-reset/validate with a valid token
    Expectation: HTTP 200 with {"valid": true}
    """
    # 1. Request a token first
    req_response = client.post(
        "/password-reset", json={"email": "student@example.com"}
    )
    assert req_response.status_code == 200
    token = req_response.get_json()["token"]

    # 2. Validate the generated token
    val_response = client.post(
        "/password-reset/validate", json={"token": token}
    )

    assert val_response.status_code == 200
    assert val_response.is_json
    data = val_response.get_json()
    assert data["status"] == "success"
    assert data["valid"] is True
    assert data["message"] == "Token is valid."


def test_password_reset_validate_invalid_token(client):
    """
    Test POST /password-reset/validate with an unknown token
    Expectation: HTTP 400 with {"valid": false}
    """
    val_response = client.post(
        "/password-reset/validate", json={"token": "invalid-token-xyz"}
    )

    assert val_response.status_code == 400
    assert val_response.is_json
    data = val_response.get_json()
    assert data["status"] == "error"
    assert data["valid"] is False
    assert (
        "not found" in data["message"].lower()
        or "invalid" in data["message"].lower()
    )


def test_password_reset_validate_missing_token_field(client):
    """
    Test POST /password-reset/validate with missing token key
    Expectation: HTTP 400 Bad Request
    """
    val_response = client.post("/password-reset/validate", json={})

    assert val_response.status_code == 400
    assert val_response.is_json
    data = val_response.get_json()
    assert data["status"] == "error"
    assert data["valid"] is False
    assert "Missing 'token' field" in data["message"]


def test_end_to_end_password_reset_flow(client):
    """
    End-to-End Integration Scenario:
    1. Service health is confirmed.
    2. User requests a password-reset token.
    3. User validates the token.
    4. Malicious user tries a fake token and gets rejected.
    """
    # Step 1: Health check
    health_res = client.get("/health")
    assert health_res.status_code == 200

    # Step 2: Request token
    reset_res = client.post(
        "/password-reset", json={"email": "alice@saas-devops.local"}
    )
    assert reset_res.status_code == 200
    token = reset_res.get_json()["token"]

    # Step 3: Validate legitimate token
    valid_res = client.post(
        "/password-reset/validate", json={"token": token}
    )
    assert valid_res.status_code == 200
    assert valid_res.get_json()["valid"] is True

    # Step 4: Validate unauthorized token
    tampered_res = client.post(
        "/password-reset/validate", json={"token": token + "-tampered"}
    )
    assert tampered_res.status_code == 400
    assert tampered_res.get_json()["valid"] is False
