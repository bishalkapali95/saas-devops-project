"""
Password Reset Domain Service
-----------------------------
This module handles generating, storing, and validating password-reset tokens.

DevOps & Architecture Note:
- For this Level 5 assessment demonstration, tokens are stored in-memory
  in a dictionary.
- In a production SaaS application, tokens would be stored in a
  persistent database (e.g., PostgreSQL or Redis with TTL), and sent via a
  transactional email provider (e.g., AWS SES or SendGrid) rather than
  returned directly in the API response.
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Tuple


class PasswordResetService:
    def __init__(self) -> None:
        # In-memory dictionary acting as our mock database table
        # Structure: { token_string: {"email": str, "expires_at": datetime} }
        self._tokens: Dict[str, Dict[str, object]] = {}

    def generate_token(self, email: str, expiry_minutes: int = 15) -> str:
        """
        Generates a cryptographically secure random token and records its
        expiration.

        :param email: Target user's email address
        :param expiry_minutes: Validity window in minutes (default 15 minutes)
        :return: Random secure token string
        """
        if not email or not isinstance(email, str) or not email.strip():
            raise ValueError("A valid, non-empty email address is required.")

        # Cryptographically secure random URL-safe token
        # (32 bytes / 43 characters)
        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=expiry_minutes
        )

        self._tokens[token] = {
            "email": email.strip(),
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
        }

        return token

    def validate_token(self, token: str) -> Tuple[bool, str]:
        """
        Validates whether a given token exists and has not expired.

        :param token: The token string to validate
        :return: Tuple of (is_valid: bool, reason_message: str)
        """
        if not token or not isinstance(token, str) or not token.strip():
            return False, "Token is missing or empty."

        token_data = self._tokens.get(token.strip())

        if not token_data:
            return False, "Token not found or invalid."

        expires_at = token_data.get("expires_at")
        if not isinstance(expires_at, datetime):
            return False, "Malformed token record."

        # Check if the token has expired compared to current UTC time
        current_time = datetime.now(timezone.utc)
        if current_time > expires_at:
            return False, "Token has expired."

        return True, "Token is valid."

    def clear_store(self) -> None:
        """Clears all stored tokens. Useful for test isolation."""
        self._tokens.clear()


# Global service instance for the application
reset_service = PasswordResetService()
