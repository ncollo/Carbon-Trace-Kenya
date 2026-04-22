"""
Rate Limiting and DDoS Protection for Carbon Trace Kenya
Advanced rate limiting with multiple strategies and protection mechanisms
"""

import time
import redis
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from functools import wraps
import threading
from collections import defaultdict, deque

class RateLimitStrategy:
    """Rate limiting strategies"""
    
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

class MemoryRateLimiter:
    """In-memory rate limiter for development/small scale"""
    
    def __init__(self):
        self.requests = defaultdict(lambda: deque())
        self.lock = threading.Lock()
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        strategy: str = RateLimitStrategy.SLIDING_WINDOW
    ) -> Dict[str, Any]:
        """Check if request is allowed"""
        now = time.time()
        
        with self.lock:
            if strategy == RateLimitStrategy.SLIDING_WINDOW:
                return self._sliding_window_check(key, limit, window_seconds, now)
            elif strategy == RateLimitStrategy.FIXED_WINDOW:
                return self._fixed_window_check(key, limit, window_seconds, now)
            elif strategy == RateLimitStrategy.TOKEN_BUCKET:
                return self._token_bucket_check(key, limit, window_seconds, now)
            else:
                return self._sliding_window_check(key, limit, window_seconds, now)
    
    def _sliding_window_check(self, key: str, limit: int, window_seconds: int, now: float) -> Dict[str, Any]:
        """Sliding window rate limiting"""
        requests = self.requests[key]
        
        # Remove old requests outside the window
        while requests and requests[0] <= now - window_seconds:
            requests.popleft()
        
        # Check if under limit
        if len(requests) < limit:
            requests.append(now)
            return {
                "allowed": True,
                "remaining": limit - len(requests),
                "reset_time": now + window_seconds,
                "retry_after": None
            }
        else:
            # Calculate retry after
            oldest_request = requests[0]
            retry_after = int(oldest_request + window_seconds - now)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": oldest_request + window_seconds,
                "retry_after": retry_after
            }
    
    def _fixed_window_check(self, key: str, limit: int, window_seconds: int, now: float) -> Dict[str, Any]:
        """Fixed window rate limiting"""
        window_start = int(now // window_seconds) * window_seconds
        window_key = f"{key}:{window_start}"
        
        requests = self.requests[window_key]
        
        # Check if under limit
        if len(requests) < limit:
            requests.append(now)
            return {
                "allowed": True,
                "remaining": limit - len(requests),
                "reset_time": window_start + window_seconds,
                "retry_after": None
            }
        else:
            retry_after = int(window_start + window_seconds - now)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": window_start + window_seconds,
                "retry_after": retry_after
            }
    
    def _token_bucket_check(self, key: str, limit: int, window_seconds: int, now: float) -> Dict[str, Any]:
        """Token bucket rate limiting"""
        bucket_key = f"{key}:bucket"
        
        if bucket_key not in self.requests:
            self.requests[bucket_key] = {
                "tokens": limit,
                "last_refill": now
            }
        
        bucket = self.requests[bucket_key]
        
        # Refill tokens
        time_passed = now - bucket["last_refill"]
        tokens_to_add = (time_passed / window_seconds) * limit
        bucket["tokens"] = min(limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return {
                "allowed": True,
                "remaining": int(bucket["tokens"]),
                "reset_time": now + window_seconds,
                "retry_after": None
            }
        else:
            retry_after = int((1 - bucket["tokens"]) * window_seconds / limit)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": now + retry_after,
                "retry_after": retry_after
            }

class RedisRateLimiter:
    """Redis-based rate limiter for production scale"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {e}")
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        strategy: str = RateLimitStrategy.SLIDING_WINDOW
    ) -> Dict[str, Any]:
        """Check if request is allowed using Redis"""
        now = time.time()
        
        if strategy == RateLimitStrategy.SLIDING_WINDOW:
            return self._redis_sliding_window(key, limit, window_seconds, now)
        elif strategy == RateLimitStrategy.FIXED_WINDOW:
            return self._redis_fixed_window(key, limit, window_seconds, now)
        else:
            return self._redis_sliding_window(key, limit, window_seconds, now)
    
    def _redis_sliding_window(self, key: str, limit: int, window_seconds: int, now: float) -> Dict[str, Any]:
        """Sliding window using Redis sorted set"""
        pipe = self.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, window_seconds)
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count < limit:
            return {
                "allowed": True,
                "remaining": limit - current_count,
                "reset_time": now + window_seconds,
                "retry_after": None
            }
        else:
            # Get oldest request time
            oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + window_seconds - now)
            else:
                retry_after = window_seconds
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": now + retry_after,
                "retry_after": retry_after
            }
    
    def _redis_fixed_window(self, key: str, limit: int, window_seconds: int, now: float) -> Dict[str, Any]:
        """Fixed window using Redis"""
        window_key = f"{key}:{int(now // window_seconds)}"
        
        current_count = self.redis_client.incr(window_key)
        
        if current_count == 1:
            self.redis_client.expire(window_key, window_seconds)
        
        if current_count <= limit:
            return {
                "allowed": True,
                "remaining": limit - current_count,
                "reset_time": (int(now // window_seconds) + 1) * window_seconds,
                "retry_after": None
            }
        else:
            retry_after = int((int(now // window_seconds) + 1) * window_seconds - now)
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": (int(now // window_seconds) + 1) * window_seconds,
                "retry_after": retry_after
            }

class DDoSProtection:
    """DDoS protection mechanisms"""
    
    def __init__(self, rate_limiter):
        self.rate_limiter = rate_limiter
        self.blocked_ips = {}
        self.suspicious_ips = defaultdict(int)
    
    def check_ip(self, ip_address: str) -> Dict[str, Any]:
        """Check IP for DDoS protection"""
        now = time.time()
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            block_info = self.blocked_ips[ip_address]
            if now < block_info["expires"]:
                return {
                    "blocked": True,
                    "reason": block_info["reason"],
                    "expires": block_info["expires"],
                    "retry_after": int(block_info["expires"] - now)
                }
            else:
                # Unblock expired blocks
                del self.blocked_ips[ip_address]
        
        # Check for suspicious activity
        suspicious_score = self.suspicious_ips[ip_address]
        
        # Very strict rate limiting for suspicious IPs
        if suspicious_score > 5:
            result = self.rate_limiter.is_allowed(
                f"ddos:{ip_address}",
                limit=5,  # Very low limit
                window_seconds=60
            )
        else:
            result = self.rate_limiter.is_allowed(
                f"ddos:{ip_address}",
                limit=100,  # Normal limit
                window_seconds=60
            )
        
        # Update suspicious score
        if not result["allowed"]:
            self.suspicious_ips[ip_address] += 1
            
            # Block if too many violations
            if self.suspicious_ips[ip_address] > 10:
                self.block_ip(ip_address, "Too many rate limit violations", 3600)  # 1 hour block
        
        return {
            "blocked": False,
            "allowed": result["allowed"],
            "remaining": result.get("remaining", 0),
            "retry_after": result.get("retry_after")
        }
    
    def block_ip(self, ip_address: str, reason: str, duration_seconds: int):
        """Block an IP address"""
        self.blocked_ips[ip_address] = {
            "reason": reason,
            "expires": time.time() + duration_seconds,
            "blocked_at": time.time()
        }

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter, ddos_protection=None):
        self.app = app
        self.rate_limiter = rate_limiter
        self.ddos_protection = ddos_protection
        
        # Rate limit rules
        self.rules = {
            # Global limits
            "global": {
                "requests": 1000,
                "window": 3600,  # 1 hour
                "strategy": RateLimitStrategy.SLIDING_WINDOW
            },
            
            # Per IP limits
            "ip": {
                "requests": 100,
                "window": 60,  # 1 minute
                "strategy": RateLimitStrategy.SLIDING_WINDOW
            },
            
            # Authentication endpoints
            "auth": {
                "requests": 5,
                "window": 300,  # 5 minutes
                "strategy": RateLimitStrategy.SLIDING_WINDOW
            },
            
            # File upload limits
            "upload": {
                "requests": 10,
                "window": 3600,  # 1 hour
                "strategy": RateLimitStrategy.SLIDING_WINDOW
            },
            
            # API endpoints
            "api": {
                "requests": 60,
                "window": 60,  # 1 minute
                "strategy": RateLimitStrategy.SLIDING_WINDOW
            }
        }
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware call"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Get request info
        request = Request(scope, receive)
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # DDoS protection check
        if self.ddos_protection:
            ddos_result = self.ddos_protection.check_ip(client_ip)
            
            if ddos_result["blocked"]:
                await self._send_error_response(
                    send, 
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    {
                        "error": "IP blocked",
                        "reason": ddos_result["reason"],
                        "retry_after": ddos_result["retry_after"]
                    }
                )
                return
        
        # Determine which rule to apply
        rule_key = self._get_rule_key(path)
        rule = self.rules.get(rule_key, self.rules["ip"])
        
        # Generate rate limit key
        rate_limit_key = f"{rule_key}:{client_ip}"
        
        # Check rate limit
        result = self.rate_limiter.is_allowed(
            rate_limit_key,
            rule["requests"],
            rule["window"],
            rule["strategy"]
        )
        
        if not result["allowed"]:
            await self._send_error_response(
                send,
                status.HTTP_429_TOO_MANY_REQUESTS,
                {
                    "error": "Rate limit exceeded",
                    "retry_after": result["retry_after"],
                    "limit": rule["requests"],
                    "window": rule["window"]
                }
            )
            return
        
        # Add rate limit headers
        await self._add_rate_limit_headers(send, result, rule)
        
        # Continue to next middleware
        await self.app(scope, receive, send)
    
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
    
    def _get_rule_key(self, path: str) -> str:
        """Determine which rate limit rule to apply"""
        if path.startswith("/auth") or path.startswith("/login") or path.startswith("/token"):
            return "auth"
        elif path.startswith("/upload") or path.startswith("/file"):
            return "upload"
        elif path.startswith("/api"):
            return "api"
        else:
            return "ip"
    
    async def _send_error_response(self, send, status_code: int, error_data: Dict[str, Any]):
        """Send error response"""
        import json
        
        response_body = json.dumps(error_data).encode()
        
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(response_body)).encode()]
            ]
        })
        
        await send({
            "type": "http.response.body",
            "body": response_body
        })
    
    async def _add_rate_limit_headers(self, send, result: Dict[str, Any], rule: Dict[str, Any]):
        """Add rate limit headers to response"""
        headers = [
            [b"X-RateLimit-Limit", str(rule["requests"]).encode()],
            [b"X-RateLimit-Remaining", str(result.get("remaining", 0)).encode()],
            [b"X-RateLimit-Reset", str(int(result.get("reset_time", 0))).encode()]
        ]
        
        if result.get("retry_after"):
            headers.append([b"Retry-After", str(result["retry_after"]).encode()])
        
        # Note: In a real implementation, you'd need to modify the response
        # This is a simplified version for demonstration

# Decorators for rate limiting
def rate_limit(requests: int, window: int, strategy: str = RateLimitStrategy.SLIDING_WINDOW):
    """Decorator for rate limiting specific functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or FastAPI dependency
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)
            
            # Get rate limiter from app state
            rate_limiter = request.app.state.rate_limiter
            
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Check rate limit
            result = rate_limiter.is_allowed(
                f"decorator:{func.__name__}:{client_ip}",
                requests,
                window,
                strategy
            )
            
            if not result["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": result["retry_after"]
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global rate limiter instance
def get_rate_limiter(use_redis: bool = False) -> Union[MemoryRateLimiter, RedisRateLimiter]:
    """Get rate limiter instance"""
    if use_redis:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        return RedisRateLimiter(redis_url)
    else:
        return MemoryRateLimiter()

def get_ddos_protection(rate_limiter) -> DDoSProtection:
    """Get DDoS protection instance"""
    return DDoSProtection(rate_limiter)
