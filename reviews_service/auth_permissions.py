import jwt
import time
from flask import jsonify, request
from functools import wraps
import pyotp  # For MFA
from services import get_db_connection

SECRET_KEY = "5ecRet_K3Y"  # Replace with a secure key

# Fetch user from database
def get_user_by_id(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

# Generate JWT token
def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": time.time() + 3600  # Token expires in 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Verify JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# MFA Enforcement
def mfa_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid token"}), 401

        user = get_user_by_id(payload["user_id"])
        if user and user["mfa_enabled"]:
            mfa_code = request.headers.get("X-MFA-Code")
            totp = pyotp.TOTP(user["mfa_secret"])
            if not mfa_code or not totp.verify(mfa_code):
                return jsonify({"error": "MFA required"}), 403

        return func(*args, **kwargs)
    return wrapper

# RBAC Enforcement
def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Unauthorized"}), 401

            payload = verify_token(token)
            if not payload or payload["role"] != role:
                return jsonify({"error": "Forbidden"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
