"""
CORS and Security Headers Configuration for Carbon Trace Kenya
Comprehensive security headers and CORS policy management
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import secrets
import hashlib
from datetime import datetime, timedelta

class SecurityHeadersConfig:
    """Security headers configuration"""
    
    # Content Security Policy
    CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "https://cdn.trusted.com"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "connect-src": ["'self'", "https://api.ntsa.go.ke"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-src": ["'none'"],
        "object-src": ["'none'"],
        "media-src": ["'self'"],
        "manifest-src": ["'self'"]
    }
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin"
    }
    
    # CORS configuration
    CORS_CONFIG = {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "https://carbontrace.co.ke",
            "https://www.carbontrace.co.ke"
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Authorization",
            "Content-Type", 
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Client-Version"
        ],
        "allow_credentials": True,
        "expose_headers": [
            "X-Total-Count",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ],
        "max_age": 86400  # 24 hours
    }

class SecurityHeadersMiddleware:
    """Security headers middleware for FastAPI"""
    
    def __init__(self, app: FastAPI, config: Optional[SecurityHeadersConfig] = None):
        self.app = app
        self.config = config or SecurityHeadersConfig()
        
        # Add security headers middleware
        app.middleware("http")(self.add_security_headers)
        
        # Add trusted host middleware
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"] if os.getenv("DEBUG") else ["carbontrace.co.ke", "www.carbontrace.co.ke", "localhost", "127.0.0.1"]
        )
    
    async def add_security_headers(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Add Content Security Policy
        csp_value = self._build_csp_header()
        response.headers["Content-Security-Policy"] = csp_value
        
        # Add other security headers
        for header, value in self.config.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add custom security headers
        response.headers["X-API-Version"] = "1.0.0"
        response.headers["X-Response-Time"] = str(int(datetime.now().timestamp() * 1000))
        
        # Add nonce for inline scripts if needed
        if self._needs_nonce(request):
            nonce = self._generate_nonce()
            response.headers["X-CSP-Nonce"] = nonce
        
        return response
    
    def _build_csp_header(self) -> str:
        """Build Content-Security-Policy header"""
        csp_parts = []
        
        for directive, sources in self.config.CSP_DIRECTIVES.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
            else:
                csp_parts.append(f"{directive}")
        
        return "; ".join(csp_parts)
    
    def _needs_nonce(self, request: Request) -> bool:
        """Check if request needs CSP nonce"""
        # Check if response might contain inline scripts
        return request.url.path in ["/dashboard", "/analytics", "/reports"]
    
    def _generate_nonce(self) -> str:
        """Generate CSP nonce"""
        return secrets.token_urlsafe(16)

class CORSMiddleware:
    """Enhanced CORS middleware with dynamic configuration"""
    
    def __init__(self, app: FastAPI, config: Optional[SecurityHeadersConfig] = None):
        self.app = app
        self.config = config or SecurityHeadersConfig()
        
        # Add CORS middleware with enhanced configuration
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.CORS_CONFIG["allow_origins"],
            allow_credentials=self.config.CORS_CONFIG["allow_credentials"],
            allow_methods=self.config.CORS_CONFIG["allow_methods"],
            allow_headers=self.config.CORS_CONFIG["allow_headers"],
            expose_headers=self.config.CORS_CONFIG["expose_headers"],
            max_age=self.config.CORS_CONFIG["max_age"]
        )
        
        # Add pre-flight handling
        app.middleware("http")(self.handle_cors_preflight)
    
    async def handle_cors_preflight(self, request: Request, call_next):
        """Handle CORS preflight requests"""
        
        # Handle OPTIONS requests
        if request.method == "OPTIONS":
            origin = request.headers.get("origin")
            
            if self._is_origin_allowed(origin):
                response = Response()
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.config.CORS_CONFIG["allow_methods"])
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.config.CORS_CONFIG["allow_headers"])
                response.headers["Access-Control-Max-Age"] = str(self.config.CORS_CONFIG["max_age"])
                response.headers["Access-Control-Allow-Credentials"] = "true"
                
                return response
            else:
                return JSONResponse(
                    {"error": "Origin not allowed"},
                    status_code=403
                )
        
        return await call_next(request)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return False
        
        # Check environment-specific origins
        if os.getenv("DEBUG"):
            return origin.startswith(("http://localhost:", "http://127.0.0.1:"))
        
        return origin in self.config.CORS_CONFIG["allow_origins"]

class CSRFProtection:
    """CSRF protection utilities"""
    
    def __init__(self):
        self.token_length = 32
        self.token_expiry = 3600  # 1 hour
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        timestamp = str(int(datetime.now().timestamp()))
        message = f"{session_id}:{timestamp}"
        
        # Create hash
        hash_value = hashlib.sha256(message.encode()).hexdigest()
        
        # Combine with timestamp
        token = f"{timestamp}:{hash_value}"
        
        return token
    
    def validate_token(self, token: str, session_id: str, max_age: int = None) -> bool:
        """Validate CSRF token"""
        if not token or ':' not in token:
            return False
        
        try:
            timestamp_str, hash_value = token.split(':', 1)
            timestamp = int(timestamp_str)
            
            # Check token age
            max_age = max_age or self.token_expiry
            if datetime.now().timestamp() - timestamp > max_age:
                return False
            
            # Verify hash
            message = f"{session_id}:{timestamp_str}"
            expected_hash = hashlib.sha256(message.encode()).hexdigest()
            
            return hash_value == expected_hash
        
        except (ValueError, IndexError):
            return False
    
    def get_csrf_header_name(self) -> str:
        """Get CSRF header name"""
        return "X-CSRF-Token"
    
    def get_csrf_cookie_name(self) -> str:
        """Get CSRF cookie name"""
        return "csrf_token"

class SecurityPolicyManager:
    """Manage and update security policies"""
    
    def __init__(self):
        self.policies = {}
        self.policy_version = "1.0"
    
    def add_csp_directive(self, directive: str, sources: List[str]):
        """Add CSP directive"""
        self.policies[f"csp_{directive}"] = sources
    
    def remove_csp_directive(self, directive: str):
        """Remove CSP directive"""
        key = f"csp_{directive}"
        if key in self.policies:
            del self.policies[key]
    
    def update_security_header(self, header: str, value: str):
        """Update security header"""
        self.policies[f"header_{header}"] = value
    
    def get_current_policy(self) -> Dict[str, Any]:
        """Get current security policy"""
        return {
            "version": self.policy_version,
            "policies": self.policies,
            "last_updated": datetime.now().isoformat()
        }
    
    def validate_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security policy"""
        issues = []
        
        # Check CSP directives
        csp_directives = {k: v for k, v in policy.items() if k.startswith("csp_")}
        
        for directive, sources in csp_directives.items():
            if not isinstance(sources, list):
                issues.append(f"Invalid CSP directive format: {directive}")
            
            # Check for unsafe sources
            if "*" in sources and directive != "csp_img-src":
                issues.append(f"Unsafe wildcard in CSP directive: {directive}")
        
        # Check security headers
        header_policies = {k: v for k, v in policy.items() if k.startswith("header_")}
        
        for header, value in header_policies.items():
            if not isinstance(value, str):
                issues.append(f"Invalid header format: {header}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

class RateLimitHeaders:
    """Rate limiting headers utilities"""
    
    @staticmethod
    def add_rate_limit_headers(
        response: Response,
        limit: int,
        remaining: int,
        reset_time: int,
        retry_after: Optional[int] = None
    ):
        """Add rate limiting headers to response"""
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        if retry_after:
            response.headers["Retry-After"] = str(retry_after)

class SecurityMonitoring:
    """Security monitoring and alerting"""
    
    def __init__(self):
        self.suspicious_requests = []
        self.blocked_ips = {}
        self.security_events = []
    
    def log_suspicious_request(
        self,
        request: Request,
        reason: str,
        severity: str = "MEDIUM"
    ):
        """Log suspicious request"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "path": request.url.path,
            "method": request.method,
            "reason": reason,
            "severity": severity,
            "headers": dict(request.headers)
        }
        
        self.security_events.append(event)
        
        # Check for repeated violations
        self._check_repeated_violations(event)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_repeated_violations(self, event: Dict[str, Any]):
        """Check for repeated security violations"""
        ip = event["ip"]
        now = datetime.now()
        
        # Clean old violations (older than 1 hour)
        self.suspicious_requests = [
            req for req in self.suspicious_requests
            if now - datetime.fromisoformat(req["timestamp"]) < timedelta(hours=1)
        ]
        
        # Add current violation
        self.suspicious_requests.append(event)
        
        # Count violations from same IP
        ip_violations = [
            req for req in self.suspicious_requests
            if req["ip"] == ip
        ]
        
        # Block IP if too many violations
        if len(ip_violations) > 10:
            self.block_ip(ip, "Too many security violations", 3600)  # 1 hour block
    
    def block_ip(self, ip: str, reason: str, duration_seconds: int):
        """Block an IP address"""
        self.blocked_ips[ip] = {
            "reason": reason,
            "expires": datetime.now() + timedelta(seconds=duration_seconds),
            "blocked_at": datetime.now().isoformat()
        }
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        if ip not in self.blocked_ips:
            return False
        
        block_info = self.blocked_ips[ip]
        return datetime.now() < datetime.fromisoformat(block_info["expires"])
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security monitoring summary"""
        now = datetime.now()
        
        # Count events in last 24 hours
        recent_events = [
            event for event in self.security_events
            if now - datetime.fromisoformat(event["timestamp"]) < timedelta(hours=24)
        ]
        
        return {
            "total_events": len(self.security_events),
            "recent_events_24h": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_requests_1h": len(self.suspicious_requests),
            "severity_breakdown": self._get_severity_breakdown(recent_events)
        }
    
    def _get_severity_breakdown(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of events by severity"""
        breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for event in events:
            severity = event.get("severity", "MEDIUM")
            if severity in breakdown:
                breakdown[severity] += 1
        
        return breakdown

# Global instances
def get_security_headers_config() -> SecurityHeadersConfig:
    """Get security headers configuration"""
    return SecurityHeadersConfig()

def get_csrf_protection() -> CSRFProtection:
    """Get CSRF protection instance"""
    return CSRFProtection()

def get_security_policy_manager() -> SecurityPolicyManager:
    """Get security policy manager"""
    return SecurityPolicyManager()

def get_security_monitoring() -> SecurityMonitoring:
    """Get security monitoring instance"""
    return SecurityMonitoring()
