"""
Flask Application Factory and API Endpoints
-------------------------------------------
This module initialises the Flask application and defines the HTTP endpoints
for health checking and the SaaS password-reset workflow.
"""

from flask import Flask, jsonify, request
from app.password_reset import reset_service


def create_app(test_config: dict = None) -> Flask:
    """
    Application Factory: Creates and configures an instance of the Flask app.

    Using an application factory is a standard DevOps & 12-factor pattern:
    it enables easy testing with isolated configurations and facilitates
    running across multiple environments (dev, test, prod).
    """
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health Check Endpoint:
        Used by container orchestrators, load balancers, and monitoring tools
        to verify that the service is running and responsive.
        """
        return jsonify({"status": "healthy"}), 200

    @app.route("/password-reset", methods=["POST"])
    def request_password_reset():
        """
        Initiate Password Reset Endpoint:
        Accepts a JSON payload with an 'email' field and generates a
        time-limited token.

        Example JSON payload:
        { "email": "student@example.com" }
        """
        data = request.get_json(silent=True)
        if not data or "email" not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'email' field in request body."
            }), 400

        email = data.get("email")
        if not isinstance(email, str) or not email.strip():
            return jsonify({
                "status": "error",
                "message": "Email field cannot be empty."
            }), 400

        try:
            token = reset_service.generate_token(
                email=email.strip(), expiry_minutes=15
            )
            return jsonify({
                "status": "success",
                "message": "Password reset token generated.",
                "token": token,
                "expires_in_minutes": 15
            }), 200
        except ValueError as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

    @app.route("/password-reset/validate", methods=["POST"])
    def validate_password_reset():
        """
        Validate Password Reset Token Endpoint:
        Accepts a JSON payload with a 'token' field and checks
        validity / expiry.

        Example JSON payload:
        { "token": "abc123xyz..." }
        """
        data = request.get_json(silent=True)
        if not data or "token" not in data:
            return jsonify({
                "status": "error",
                "valid": False,
                "message": "Missing 'token' field in request body."
            }), 400

        token = data.get("token")
        if not isinstance(token, str) or not token.strip():
            return jsonify({
                "status": "error",
                "valid": False,
                "message": "Token field cannot be empty."
            }), 400

        is_valid, reason = reset_service.validate_token(token.strip())

        if is_valid:
            return jsonify({
                "status": "success",
                "valid": True,
                "message": reason
            }), 200
        else:
            return jsonify({
                "status": "error",
                "valid": False,
                "message": reason
            }), 400

    return app


# Default app instance for simple local execution via `flask run`
# or WSGI servers
app = create_app()

if __name__ == "__main__":
    # Runs the development server on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
