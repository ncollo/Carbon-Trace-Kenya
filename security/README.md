# Security Implementation for Carbon Trace Kenya

## Overview

This document outlines the comprehensive security implementation for the Carbon Trace Kenya platform, covering authentication, data protection, input validation, and security monitoring.

## Security Architecture

### 1. Authentication & Authorization (`security/auth.py`)

**Features:**
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password strength validation
- Secure session management
- Multi-factor authentication ready

**Roles & Permissions:**
- **Admin**: Full system access
- **Analyst**: Read/write analytics, manage emissions
- **User**: Manage own company data, vehicles
- **Viewer**: Read-only access to reports

**Usage:**
```python
from security.auth import AuthService, get_current_user

# Create auth service
auth_service = AuthService(secret_key="your-secret-key")

# Authenticate user
user = auth_service.authenticate_user(db, email, password)

# Create tokens
tokens = auth_service.create_user_tokens(user)

# Protect endpoints
@router.get("/protected")
async def protected_endpoint(current_user = Depends(get_current_user)):
    return {"user": current_user.email}
```

### 2. Data Encryption (`security/encryption.py`)

**Features:**
- AES-256 encryption for sensitive data
- PBKDF2 key derivation
- Data masking utilities
- Secure token generation
- Field-level encryption

**Sensitive Fields Protected:**
- User passwords, emails, phone numbers
- SACCO contact information
- Vehicle registration numbers
- NTSA inspector IDs

**Usage:**
```python
from security.encryption import DataEncryption, get_encryption_service

# Get encryption service
encryption = get_encryption_service()

# Encrypt sensitive data
encrypted_data = encryption.encrypt_data("sensitive_info")

# Encrypt specific fields
data = {"name": "John", "phone": "+254712345678"}
encrypted = encryption.encrypt_sensitive_fields(data, ["phone"])
```

### 3. Input Validation (`security/input_validation.py`)

**Features:**
- SQL injection prevention
- XSS protection
- File upload validation
- Kenyan data format validation
- Comprehensive sanitization

**Validation Rules:**
- Kenyan phone numbers: +254XXXXXXXXX, 07XXXXXXXX
- Vehicle registration: KXX 123X format
- SACCO names: Alphanumeric with spaces/hyphens
- Route numbers: 2-3 digits with optional letter

**Usage:**
```python
from security.input_validation import SecurityValidator, PydanticModels

# Validate input
is_safe = SecurityValidator.validate_sql_injection(user_input)

# Use Pydantic models with validation
class MatatuCreate(PydanticModels.MatatuVehicleCreate):
    pass
```

### 4. Audit Logging (`security/audit_logging.py`)

**Features:**
- Comprehensive activity logging
- Data access tracking
- Security event monitoring
- Automated audit reports
- GDPR compliance ready

**Logged Events:**
- Login/logout attempts
- Data CRUD operations
- File uploads/downloads
- Permission changes
- Security violations

**Usage:**
```python
from security.audit_logging import AuditLogger, AuditAction, AuditResource

# Create audit logger
audit = AuditLogger(db_session)

# Log data access
audit.log_data_access(
    resource=AuditResource.MATATU_VEHICLE,
    resource_id="KA123A",
    user_id=user.id,
    user_email=user.email,
    ip_address=request.client.host
)
```

### 5. Rate Limiting & DDoS Protection (`security/rate_limiting.py`)

**Features:**
- Multiple rate limiting strategies
- IP-based blocking
- DDoS detection
- Redis/In-memory backends
- Configurable limits

**Rate Limits:**
- Global: 1000 requests/hour
- Per IP: 100 requests/minute
- Auth endpoints: 5 requests/5 minutes
- File uploads: 10 requests/hour

**Usage:**
```python
from security.rate_limiting import get_rate_limiter, rate_limit

# Get rate limiter
limiter = get_rate_limiter(use_redis=True)

# Check rate limit
result = limiter.is_allowed("user:123", limit=60, window_seconds=60)

# Decorator for endpoints
@rate_limit(requests=30, window_seconds=60)
async def protected_endpoint():
    pass
```

### 6. Secure File Upload (`security/secure_file_upload.py`)

**Features:**
- File type validation
- Content verification
- Size limits
- Virus scanning ready
- Secure storage

**Allowed Files:**
- Documents: PDF, DOC, DOCX, TXT, CSV, XLSX
- Images: JPG, PNG, GIF, BMP, WebP
- Data: JSON, XML, YAML

**Usage:**
```python
from security.secure_file_upload import get_secure_file_handler

# Get file handler
handler = get_secure_file_handler()

# Handle upload
result = await handler.handle_upload(
    file=uploaded_file,
    user_id=user.id,
    category="documents"
)
```

### 7. Database Security (`security/database_security.py`)

**Features:**
- SQL injection detection
- Query complexity analysis
- Access control enforcement
- Database auditing
- Performance monitoring

**Security Measures:**
- Parameterized queries only
- Role-based table access
- Sensitive column protection
- Query timeout enforcement

**Usage:**
```python
from security.database_security import get_query_security

# Get query security
query_sec = get_query_security(db_session)

# Execute secure query
result = query_sec.secure_execute(
    "SELECT * FROM matatu_vehicles WHERE sacco_id = :sacco_id",
    {"sacco_id": user.company_id}
)
```

### 8. CORS & Security Headers (`security/cors_security.py`)

**Features:**
- Content Security Policy (CSP)
- Security headers configuration
- CORS policy management
- CSRF protection
- Security monitoring

**Security Headers:**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000
- Content-Security-Policy: strict

**Usage:**
```python
from security.cors_security import SecurityHeadersMiddleware

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
```

### 9. Security Testing (`security/security_testing.py`)

**Features:**
- Automated vulnerability scanning
- SQL injection testing
- XSS detection
- Security header validation
- Comprehensive reporting

**Test Coverage:**
- OWASP Top 10 vulnerabilities
- Common misconfigurations
- Information disclosure
- Authentication bypasses

**Usage:**
```bash
# Run security scan
python security/security_testing.py https://your-app.com
```

## Security Configuration

### Environment Variables

```bash
# Security
JWT_SECRET=your-super-secret-jwt-key
MASTER_ENCRYPTION_KEY=your-encryption-key
DEBUG=false

# Database Security
DATABASE_URL=postgresql://user:pass@localhost:5432/carbon_trace
DATABASE_ECHO=false

# Rate Limiting
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_ENABLED=true

# CORS
ALLOWED_ORIGINS=https://carbontrace.co.ke,https://www.carbontrace.co.ke
CORS_CREDENTIALS=true
```

### Security Headers Configuration

```python
# security/cors_security.py
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'"
}
```

## Security Best Practices

### 1. Development
- Use parameterized queries
- Validate all inputs
- Implement proper error handling
- Use HTTPS in production
- Keep dependencies updated

### 2. Deployment
- Enable security headers
- Configure proper CORS
- Set up monitoring
- Use environment variables for secrets
- Implement backup encryption

### 3. Monitoring
- Monitor failed logins
- Track unusual activity
- Set up alerts for security events
- Regular security audits
- Log retention policies

### 4. Data Protection
- Encrypt sensitive data at rest
- Use TLS in transit
- Implement data masking
- Regular access reviews
- GDPR compliance

## Security Checklist

### ✅ Authentication
- [x] JWT-based authentication
- [x] Role-based access control
- [x] Password strength validation
- [x] Secure session management
- [x] Multi-factor auth ready

### ✅ Data Protection
- [x] Field-level encryption
- [x] Data masking utilities
- [x] Secure key management
- [x] Sensitive data identification
- [x] GDPR compliance

### ✅ Input Validation
- [x] SQL injection prevention
- [x] XSS protection
- [x] File upload validation
- [x] Format validation
- [x] Input sanitization

### ✅ Monitoring & Auditing
- [x] Comprehensive audit logging
- [x] Security event monitoring
- [x] Rate limiting
- [x] DDoS protection
- [x] Automated scanning

### ✅ Infrastructure Security
- [x] Security headers
- [x] CORS configuration
- [x] CSRF protection
- [x] Database security
- [x] Secure file handling

## Security Testing

### Running Security Tests

```bash
# Install dependencies
pip install -r security/requirements.txt

# Run vulnerability scan
python security/security_testing.py http://localhost:8000

# Run specific tests
python -m security.tests.test_sql_injection
python -m security.tests.test_xss
python -m security.tests.test_authentication
```

### Security Reports

Security scan reports are saved to `security_reports/` directory:
- `security_report_YYYYMMDD_HHMMSS.json`
- Includes vulnerability details
- Risk assessment
- Recommendations

## Incident Response

### Security Incident Steps

1. **Detection**: Monitor security alerts
2. **Assessment**: Evaluate impact and scope
3. **Containment**: Block malicious IPs/users
4. **Eradication**: Patch vulnerabilities
5. **Recovery**: Restore services
6. **Lessons Learned**: Update security measures

### Emergency Contacts

- Security Team: security@carbontrace.co.ke
- IT Support: it@carbontrace.co.ke
- Data Protection: dpo@carbontrace.co.ke

## Compliance

### GDPR Compliance
- Data subject rights
- Data minimization
- Consent management
- Breach notification
- Data portability

### Kenyan Data Protection
- Compliance with Data Protection Act 2019
- Local data storage requirements
- Cross-border transfer rules

## Security Dependencies

```bash
# Security packages
pip install pyjwt passlib bcrypt
pip install cryptography fernet
pip install bleach python-magic
pip install redis aiofiles
pip install pillow pdfplumber
pip install aiohttp
```

## Security Monitoring Dashboard

### Key Metrics
- Failed login attempts
- Rate limit violations
- Security events by severity
- Vulnerability scan results
- Data access patterns

### Alerts Configuration
- High severity events: Immediate
- Medium severity: 1 hour
- Low severity: 24 hours
- Weekly security reports

## Security Updates

### Regular Tasks
- Monthly security scans
- Quarterly penetration testing
- Bi-annual security audits
- Annual compliance reviews
- Continuous monitoring

### Update Process
1. Test security updates in staging
2. Review security implications
3. Schedule maintenance window
4. Deploy with rollback plan
5. Monitor for issues

## Security Contacts

For security concerns or vulnerabilities:
- Email: security@carbontrace.co.ke
- Encrypted: PGP key available on request
- Bug Bounty: security@carbontrace.co.ke

---

**Last Updated**: April 2026
**Version**: 1.0.0
**Security Team**: Carbon Trace Kenya Security Team
