"""
Authentication and Authorization System for Carbon Trace Kenya
JWT-based authentication with role-based access control
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token configuration
security = HTTPBearer()

class UserRole:
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"
    
    @classmethod
    def get_all_roles(cls) -> List[str]:
        return [cls.ADMIN, cls.USER, cls.VIEWER, cls.ANALYST]
    
    @classmethod
    def get_role_permissions(cls, role: str) -> Dict[str, bool]:
        """Get permissions for each role"""
        permissions = {
            cls.ADMIN: {
                "read_all": True,
                "write_all": True,
                "delete_all": True,
                "manage_users": True,
                "view_analytics": True,
                "export_data": True,
                "manage_emissions": True,
                "manage_vehicles": True,
                "view_insights": True
            },
            cls.ANALYST: {
                "read_all": True,
                "write_all": False,
                "delete_all": False,
                "manage_users": False,
                "view_analytics": True,
                "export_data": True,
                "manage_emissions": True,
                "manage_vehicles": False,
                "view_insights": True
            },
            cls.USER: {
                "read_all": False,
                "write_all": False,
                "delete_all": False,
                "manage_users": False,
                "view_analytics": True,
                "export_data": False,
                "manage_emissions": True,
                "manage_vehicles": True,
                "view_insights": True
            },
            cls.VIEWER: {
                "read_all": False,
                "write_all": False,
                "delete_all": False,
                "manage_users": False,
                "view_analytics": True,
                "export_data": False,
                "manage_emissions": False,
                "manage_vehicles": False,
                "view_insights": True
            }
        }
        return permissions.get(role, {})

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None
    permissions: Dict[str, bool] = {}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_id: int
    role: str = UserRole.USER
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    company_id: int
    is_active: bool
    created_at: datetime
    full_name: Optional[str] = None
    phone: Optional[str] = None

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength requirements"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        
        # Character variety bonus
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 25
        
        return min(score, 100)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            role: str = payload.get("role")
            company_id: int = payload.get("company_id")
            
            if email is None or role is None:
                return None
            
            permissions = UserRole.get_role_permissions(role)
            
            token_data = TokenData(
                email=email,
                role=role,
                company_id=company_id,
                permissions=permissions
            )
            return token_data
            
        except JWTError:
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[Any]:
        """Authenticate user credentials"""
        from db.models import User
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def create_user_tokens(self, user: Any) -> Token:
        """Create access and refresh tokens for user"""
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        
        access_token = self.create_access_token(
            data={
                "sub": user.email,
                "role": user.role,
                "company_id": user.company_id,
                "user_id": user.id
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(
            data={
                "sub": user.email,
                "role": user.role,
                "company_id": user.company_id,
                "user_id": user.id
            }
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            refresh_token=refresh_token
        )

# Global auth service instance
def get_auth_service() -> AuthService:
    """Get auth service instance"""
    secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
    return AuthService(secret_key=secret_key)

# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db)
) -> Any:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = auth_service.verify_token(token)
        
        if token_data is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    from db.models import User
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if user is None:
        raise credentials_exception
    
    return user

# Role-based access control decorators
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependencies
            pass
        return wrapper
    return decorator

def require_role(required_role: str):
    """Decorator to require specific role"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependencies
            pass
        return wrapper
    return decorator

# Database dependency (to be imported from main app)
def get_db():
    """Database dependency"""
    # This will be imported from the main application
    pass
