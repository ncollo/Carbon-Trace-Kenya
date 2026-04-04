from fastapi import Depends, HTTPException, Header
from typing import Optional
import jwt
from config import settings


def decode_jwt(token: str) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
