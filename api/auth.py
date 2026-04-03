from fastapi import Depends, HTTPException, Header
from typing import Optional


def decode_jwt(token: str) -> dict:
    # Placeholder: validate and decode JWT token
    # Replace with PyJWT or other library integration
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    # For now return a dummy user
    return {"sub": "user@example.com", "scopes": ["user"]}


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = authorization.split()
    except Exception:
        raise HTTPException(status_code=401, detail="Malformed Authorization header")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Unsupported auth scheme")
    return decode_jwt(token)
