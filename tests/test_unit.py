"""
Unit Tests for PasswordResetService
-----------------------------------
DevOps Context:
Unit tests verify individual functions and domain logic in complete isolation
without spinning up web servers, databases, or external dependencies.
They execute in milliseconds and form the foundation of the Test Pyramid in CI.
"""

from datetime import datetime, timedelta, timezone
import pytest
from app.password_reset import PasswordResetService


@pytest.fixture
def reset_service():
    """Provides a fresh, isolated instance of PasswordResetService for
    each test."""
    service = PasswordResetService()
    service.clear_store()
    return service


def test_token_generation_success(reset_service):
    """Verify that generate_token produces a valid, non-empty string and
    stores it."""
    email = "student@example.com"
    token = reset_service.generate_token(email=email, expiry_minutes=15)

    assert isinstance(token, str)
    assert len(token) > 20
    assert token in reset_service._tokens
    assert reset_service._tokens[token]["email"] == email


def test_token_generation_unique(reset_service):
    """Verify that multiple generated tokens are unique."""
    token1 = reset_service.generate_token("user1@example.com")
    token2 = reset_service.generate_token("user2@example.com")

    assert token1 != token2


def test_token_generation_empty_email(reset_service):
    """Verify that token generation fails when given an empty or whitespace
    email."""
    with pytest.raises(ValueError, match="valid, non-empty email"):
        reset_service.generate_token("")

    with pytest.raises(ValueError, match="valid, non-empty email"):
        reset_service.generate_token("   ")


def test_validate_valid_token(reset_service):
    """Verify that a freshly generated token validates successfully."""
    email = "student@example.com"
    token = reset_service.generate_token(email, expiry_minutes=15)

    is_valid, message = reset_service.validate_token(token)

    assert is_valid is True
    assert message == "Token is valid."


def test_validate_invalid_token(reset_service):
    """Verify that a non-existent or manipulated token is rejected."""
    is_valid, message = reset_service.validate_token(
        "non-existent-token-12345"
    )

    assert is_valid is False
    assert "not found" in message.lower() or "invalid" in message.lower()


def test_validate_empty_token(reset_service):
    """Verify that empty or None tokens are rejected gracefully."""
    is_valid, message = reset_service.validate_token("")
    assert is_valid is False

    is_valid, message = reset_service.validate_token("   ")
    assert is_valid is False


def test_validate_expired_token(reset_service):
    """Verify that an expired token is detected and rejected."""
    token = "test-expired-token"
    # Manually store an already expired token
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    reset_service._tokens[token] = {
        "email": "student@example.com",
        "expires_at": past_time,
        "created_at": past_time - timedelta(minutes=15),
    }

    is_valid, message = reset_service.validate_token(token)

    assert is_valid is False
    assert "expired" in message.lower()


def test_clear_store(reset_service):
    """Verify that clear_store empties the in-memory dictionary."""
    reset_service.generate_token("user@example.com")
    assert len(reset_service._tokens) == 1

    reset_service.clear_store()
    assert len(reset_service._tokens) == 0
