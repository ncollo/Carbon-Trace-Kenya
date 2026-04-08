from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from api.auth import decode_jwt, get_current_user
from config import settings


def test_decode_valid_jwt():
    payload = {"sub": "user-1"}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    assert decode_jwt(token) == payload


def test_decode_expired_jwt():
    payload = {"sub": "user-1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    with pytest.raises(HTTPException) as exc:
        decode_jwt(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Token expired"


def test_decode_invalid_jwt():
    payload = {"sub": "user-1"}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    with pytest.raises(HTTPException) as exc:
        decode_jwt(token + "tamper")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"


def test_get_current_user_missing_header():
    with pytest.raises(HTTPException) as exc:
        get_current_user(authorization=None)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Missing Authorization header"


def test_get_current_user_malformed_header():
    with pytest.raises(HTTPException) as exc:
        get_current_user(authorization="onlyonetoken")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Malformed Authorization header"


def test_get_current_user_wrong_scheme():
    with pytest.raises(HTTPException) as exc:
        get_current_user(authorization="Basic abc")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Unsupported auth scheme"


def test_get_current_user_valid_bearer():
    payload = {"sub": "user-1"}
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    assert get_current_user(authorization=f"Bearer {token}") == payload
