"""
Authentication endpoints for Carbon Trace Kenya.
Handles user login, token generation, and JWT validation.
"""
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
import jwt
from datetime import datetime, timezone
import hashlib
import os

from db.session import SessionLocal
from db.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    company_id: Optional[int] = None
    role: str = "user"
    
    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)  # Will be validated in signup endpoint
    company_name: str = Field(..., min_length=2, max_length=255)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using SHA256 (in production, use bcrypt)."""
    salt = os.getenv("PASSWORD_SALT", "default-salt-change-me")
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed


def create_access_token(user_id: int, email: str, expires_in_hours: int = 24) -> tuple[str, int]:
    """Create a JWT access token."""
    from config import settings
    
    expires = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": int(expires.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    
    return token, expires_in_hours * 3600


def verify_token(token: str) -> dict:
    """Verify a JWT token and return the payload."""
    from config import settings
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    Login with email and password to get JWT token.
    
    Example:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword123"
    }
    ```
    """
    db = SessionLocal()
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Generate token
        token, expires_in = create_access_token(user.id, user.email)
        
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user_id=user.id,
            email=user.email
        )
    finally:
        db.close()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new user and get JWT token.
    
    Example:
    ```json
    {
      "email": "newuser@example.com",
      "password": "securepassword123",
      "company_name": "My Company"
    }
    ```
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        from db.models import Company
        
        # Create company
        company = Company(name=request.company_name)
        db.add(company)
        db.flush()  # Get company ID without committing
        
        # Create user
        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            company_id=company.id,
            is_active=True,
            role="admin"  # First user is admin
        )
        db.add(user)
        db.commit()
        
        # Generate token
        token, expires_in = create_access_token(user.id, user.email)
        
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user_id=user.id,
            email=user.email
        )
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}"
        )
    finally:
        db.close()


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = None):
    """
    Get current authenticated user info.
    Requires Authorization header: `Authorization: Bearer <token>`
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Verify token
    payload = verify_token(token)
    user_id = int(payload["sub"])
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    finally:
        db.close()


@router.post("/validate")
async def validate_token(token: str):
    """
    Validate if a token is still valid.
    Returns 200 if valid, 401 if invalid/expired.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )
    
    # This will raise HTTPException if invalid
    payload = verify_token(token)
    
    return {
        "valid": True,
        "user_id": int(payload["sub"]),
        "email": payload["email"]
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion is sufficient).
    Included for API completeness.
    """
    return {
        "message": "Logged out successfully. Please delete the access token on client."
    }
