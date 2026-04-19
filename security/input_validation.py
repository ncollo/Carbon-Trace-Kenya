"""
Input Validation and Sanitization for Carbon Trace Kenya
Comprehensive validation for all API inputs and user data
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime, date
import bleach

class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class SecurityValidator:
    """Security-focused input validation"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(['\"];?\s*(OR|AND)\s*['\"]?\w+['\"]?\s*=\s*['\"]?\w+)",
        r"(/\*.*\*/)",
        r"(--|#)",
        r"(\bEXEC\s*\(|\bXP_CMDSHELL\b)"
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"vbscript:",
        r"data:text/html"
    ]
    
    @staticmethod
    def validate_sql_injection(input_string: str) -> bool:
        """Check for SQL injection attempts"""
        if not input_string:
            return True
        
        input_upper = input_string.upper()
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                return False
        return True
    
    @staticmethod
    def validate_xss(input_string: str) -> bool:
        """Check for XSS attempts"""
        if not input_string:
            return True
        
        for pattern in SecurityValidator.XSS_PATTERNS:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False
        return True
    
    @staticmethod
    def sanitize_html(input_string: str) -> str:
        """Sanitize HTML input"""
        if not input_string:
            return ""
        
        # Allow basic HTML tags for rich text
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
        allowed_attributes = {}
        
        return bleach.clean(
            input_string,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_file_upload(filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file security"""
        errors = []
        warnings = []
        
        # Check filename
        if not filename:
            errors.append("Filename is required")
        else:
            # Check for dangerous extensions
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', 
                                '.vbs', '.js', '.jar', '.php', '.asp', '.jsp']
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in dangerous_extensions:
                errors.append(f"Dangerous file extension: {file_ext}")
            
            # Check for path traversal
            if '..' in filename or '/' in filename or '\\' in filename:
                errors.append("Invalid filename characters")
        
        # Check content type
        allowed_types = [
            'application/pdf', 'text/csv', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'image/jpeg', 'image/png', 'text/plain'
        ]
        
        if content_type not in allowed_types:
            errors.append(f"Unsupported file type: {content_type}")
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if file_size > max_size:
            errors.append(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

class MatatuValidators:
    """Specific validators for Matatu fleet data"""
    
    @staticmethod
    def validate_registration_number(reg_number: str) -> bool:
        """Validate Kenyan vehicle registration number"""
        if not reg_number:
            return False
        
        # Kenyan registration format: KXX 123X or KXX 123A
        pattern = r'^[K][A-Z]{2}\s*\d{3,4}[A-Z]?$'
        return bool(re.match(pattern, reg_number.upper()))
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Kenyan phone number"""
        if not phone:
            return False
        
        # Remove spaces and special characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Kenyan phone formats: +254XXXXXXXXX, 07XXXXXXXX, 254XXXXXXXXX
        patterns = [
            r'^\+2547\d{8}$',
            r'^2547\d{8}$',
            r'^07\d{8}$'
        ]
        
        return any(re.match(pattern, clean_phone) for pattern in patterns)
    
    @staticmethod
    def validate_sacco_name(name: str) -> bool:
        """Validate SACCO name"""
        if not name or len(name) < 3 or len(name) > 100:
            return False
        
        # Check for valid characters (letters, numbers, spaces, hyphens)
        pattern = r'^[a-zA-Z0-9\s\-&]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_route_number(route: str) -> bool:
        """Validate route number"""
        if not route:
            return True  # Optional field
        
        # Route numbers are typically 2-3 digits
        pattern = r'^\d{2,3}[A-Z]?$'
        return bool(re.match(pattern, route.upper()))

class PydanticModels:
    """Pydantic models with validation"""
    
    class MatatuSaccoCreate(BaseModel):
        name: str
        registration_number: str
        contact_phone: Optional[str] = None
        contact_email: Optional[EmailStr] = None
        office_location: Optional[str] = None
        fleet_size: Optional[int] = None
        established_year: Optional[int] = None
        ntsa_compliance_rating: Optional[float] = None
        
        @validator('name')
        def validate_name(cls, v):
            if not MatatuValidators.validate_sacco_name(v):
                raise ValueError('Invalid SACCO name')
            return v
        
        @validator('contact_phone')
        def validate_phone(cls, v):
            if v and not MatatuValidators.validate_phone_number(v):
                raise ValueError('Invalid Kenyan phone number')
            return v
        
        @validator('fleet_size')
        def validate_fleet_size(cls, v):
            if v is not None and (v < 1 or v > 1000):
                raise ValueError('Fleet size must be between 1 and 1000')
            return v
        
        @validator('established_year')
        def validate_year(cls, v):
            if v is not None and (v < 1950 or v > datetime.now().year):
                raise ValueError(f'Year must be between 1950 and {datetime.now().year}')
            return v
        
        @validator('ntsa_compliance_rating')
        def validate_rating(cls, v):
            if v is not None and (v < 1.0 or v > 5.0):
                raise ValueError('NTSA compliance rating must be between 1.0 and 5.0')
            return v
    
    class MatatuVehicleCreate(BaseModel):
        sacco_id: int
        registration_number: str
        make: str
        model: str
        year_of_manufacture: int
        vehicle_type: str
        engine_capacity: int
        fuel_type: str
        seating_capacity: int
        route_number: Optional[str] = None
        emission_rating: Optional[str] = None
        mileage: Optional[int] = None
        is_active: bool = True
        
        @validator('registration_number')
        def validate_registration(cls, v):
            if not MatatuValidators.validate_registration_number(v):
                raise ValueError('Invalid Kenyan vehicle registration number')
            return v
        
        @validator('make')
        def validate_make(cls, v):
            if not v or len(v) < 2 or len(v) > 50:
                raise ValueError('Vehicle make must be between 2 and 50 characters')
            return v
        
        @validator('year_of_manufacture')
        def validate_year(cls, v):
            if v < 1950 or v > datetime.now().year:
                raise ValueError(f'Year of manufacture must be between 1950 and {datetime.now().year}')
            return v
        
        @validator('vehicle_type')
        def validate_type(cls, v):
            valid_types = ['14-seater', '25-seater', '33-seater', 'bus']
            if v not in valid_types:
                raise ValueError(f'Vehicle type must be one of: {valid_types}')
            return v
        
        @validator('fuel_type')
        def validate_fuel_type(cls, v):
            valid_types = ['petrol', 'diesel', 'electric', 'hybrid']
            if v not in valid_types:
                raise ValueError(f'Fuel type must be one of: {valid_types}')
            return v
        
        @validator('route_number')
        def validate_route(cls, v):
            if v and not MatatuValidators.validate_route_number(v):
                raise ValueError('Invalid route number format')
            return v
    
    class NtsaInspectionCreate(BaseModel):
        vehicle_id: int
        inspection_date: datetime
        inspector_id: str
        inspection_type: str
        roadworthiness_score: float
        safety_score: float
        emissions_score: float
        overall_rating: str
        violations_found: Optional[List[str]] = None
        recommendations: Optional[List[str]] = None
        
        @validator('inspection_type')
        def validate_inspection_type(cls, v):
            valid_types = ['annual', 'quarterly', 'special']
            if v not in valid_types:
                raise ValueError(f'Inspection type must be one of: {valid_types}')
            return v
        
        @validator('roadworthiness_score', 'safety_score', 'emissions_score')
        def validate_scores(cls, v):
            if v < 0 or v > 100:
                raise ValueError('Scores must be between 0 and 100')
            return v
        
        @validator('overall_rating')
        def validate_overall_rating(cls, v):
            valid_ratings = ['Pass', 'Fail', 'Conditional']
            if v not in valid_ratings:
                raise ValueError(f'Overall rating must be one of: {valid_ratings}')
            return v

class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(input_string: str) -> str:
        """Sanitize string input"""
        if not input_string:
            return ""
        
        # HTML entity encode
        sanitized = html.escape(input_string)
        
        # Remove potential script content
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE)
        
        # Remove JavaScript event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_numeric(input_value: Any) -> Optional[float]:
        """Sanitize numeric input"""
        if input_value is None:
            return None
        
        try:
            return float(str(input_value).replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input"""
        if not email:
            return ""
        
        # Convert to lowercase
        email = email.lower().strip()
        
        # Remove potentially dangerous characters
        email = re.sub(r'[<>"\']', '', email)
        
        return email
    
    @staticmethod
    def validate_and_sanitize(input_data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize multiple fields"""
        sanitized_data = {}
        errors = []
        
        for field, rules in validation_rules.items():
            value = input_data.get(field)
            
            # Apply sanitization
            if rules.get('type') == 'string':
                value = InputSanitizer.sanitize_string(value)
            elif rules.get('type') == 'email':
                value = InputSanitizer.sanitize_email(value)
            elif rules.get('type') == 'numeric':
                value = InputSanitizer.sanitize_numeric(value)
            
            # Apply validation
            if 'required' in rules and rules['required'] and not value:
                errors.append(f"{field} is required")
                continue
            
            if 'max_length' in rules and value and len(str(value)) > rules['max_length']:
                errors.append(f"{field} exceeds maximum length")
                continue
            
            if 'min_length' in rules and value and len(str(value)) < rules['min_length']:
                errors.append(f"{field} below minimum length")
                continue
            
            # Security validation
            if isinstance(value, str):
                if not SecurityValidator.validate_sql_injection(value):
                    errors.append(f"{field} contains invalid characters")
                    continue
                
                if not SecurityValidator.validate_xss(value):
                    errors.append(f"{field} contains potentially dangerous content")
                    continue
            
            sanitized_data[field] = value
        
        return {
            "sanitized_data": sanitized_data,
            "errors": errors,
            "is_valid": len(errors) == 0
        }
