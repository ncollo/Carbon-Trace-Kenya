"""
Data Encryption and Security Utilities for Carbon Trace Kenya
Handles sensitive data encryption, hashing, and secure data handling
"""

import os
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Optional, Dict, Any, Union
import json

class DataEncryption:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption with master key"""
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_master_key()
        
        self.fernet = Fernet(self._derive_key(self.master_key))
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master key"""
        return os.urandom(32)
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = b'carbon_trace_salt'  # In production, use random salt per deployment
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_data(self, data: Union[str, Dict, Any]) -> str:
        """Encrypt data and return base64 encoded string"""
        if isinstance(data, dict):
            data = json.dumps(data)
        
        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Encrypt specific fields in a dictionary"""
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_data(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Decrypt specific fields in a dictionary"""
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_data(decrypted_data[field])
                except Exception:
                    # Field might not be encrypted
                    pass
        
        return decrypted_data

class SecureHash:
    """Secure hashing utilities for passwords and sensitive data"""
    
    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive data with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        combined = f"{data}{salt}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()
        return f"{salt}:{hash_value}"
    
    @staticmethod
    def verify_sensitive_hash(data: str, hashed_value: str) -> bool:
        """Verify data against hash"""
        try:
            salt, hash_value = hashed_value.split(':', 1)
            new_hash = SecureHash.hash_sensitive_data(data, salt)
            return new_hash == hashed_value
        except Exception:
            return False
    
    @staticmethod
    def generate_data_fingerprint(data: Union[str, Dict]) -> str:
        """Generate fingerprint for data integrity verification"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        return hashlib.sha256(data.encode()).hexdigest()

class SecureToken:
    """Generate and validate secure tokens"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate API key for external integrations"""
        return f"ctr_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate session token"""
        return f"sess_{secrets.token_urlsafe(24)}"
    
    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate password reset token"""
        return f"reset_{secrets.token_urlsafe(32)}"

class DataMasking:
    """Data masking utilities for sensitive information display"""
    
    @staticmethod
    def mask_email(email: str, show_chars: int = 2) -> str:
        """Mask email address"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= show_chars:
            return f"{'*' * len(local)}@{domain}"
        
        masked_local = local[:show_chars] + '*' * (len(local) - show_chars)
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str, show_last: int = 4) -> str:
        """Mask phone number"""
        if len(phone) <= show_last:
            return '*' * len(phone)
        
        return '*' * (len(phone) - show_last) + phone[-show_last:]
    
    @staticmethod
    def mask_registration_number(reg_number: str, show_chars: int = 3) -> str:
        """Mask vehicle registration number"""
        if len(reg_number) <= show_chars:
            return '*' * len(reg_number)
        
        return reg_number[:show_chars] + '*' * (len(reg_number) - show_chars)

class SecurityUtils:
    """General security utilities"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        return api_key.startswith('ctr_') and len(api_key) > 35
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for secure storage"""
        import re
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove special characters except dots and hyphens
        filename = re.sub(r'[^\w\-\.]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def is_safe_url(url: str, allowed_hosts: list = None) -> bool:
        """Check if URL is safe for redirects"""
        if not url:
            return False
        
        # Check for JavaScript attempts
        if 'javascript:' in url.lower():
            return False
        
        # Check for data URLs
        if url.startswith('data:'):
            return False
        
        # Check against allowed hosts
        if allowed_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc in allowed_hosts
        
        return True

# Global encryption instance
def get_encryption_service() -> DataEncryption:
    """Get encryption service instance"""
    master_key = os.getenv('MASTER_ENCRYPTION_KEY')
    return DataEncryption(master_key=master_key)

# Sensitive fields configuration
SENSITIVE_FIELDS = {
    'user': ['password_hash', 'phone', 'email'],
    'matatu_sacco': ['contact_phone', 'contact_email'],
    'matatu_vehicle': ['registration_number'],
    'ntsa_inspection': ['inspector_id']
}

# Data encryption decorators
def encrypt_sensitive_data(model_name: str):
    """Decorator to encrypt sensitive data before database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Implementation would encrypt sensitive fields
            # before database operations
            pass
        return wrapper
    return decorator

def decrypt_sensitive_data(model_name: str):
    """Decorator to decrypt sensitive data after database operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Implementation would decrypt sensitive fields
            # after database operations
            pass
        return wrapper
    return decorator
