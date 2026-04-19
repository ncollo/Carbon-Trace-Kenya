"""
Security Testing and Vulnerability Scanning for Carbon Trace Kenya
Comprehensive security testing suite with automated vulnerability detection
"""

import asyncio
import aiohttp
import ssl
import hashlib
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import subprocess
import tempfile
import os

class VulnerabilityScanner:
    """Automated vulnerability scanner"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.results = []
        
    async def scan(self) -> Dict[str, Any]:
        """Run comprehensive security scan"""
        print(f"Starting security scan for {self.base_url}")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "target": self.base_url,
                "scans": {}
            }
            
            # Run various security tests
            scan_results["scans"]["sql_injection"] = await self._test_sql_injection()
            scan_results["scans"]["xss"] = await self._test_xss()
            scan_results["scans"]["directory_traversal"] = await self._test_directory_traversal()
            scan_results["scans"]["security_headers"] = await self._test_security_headers()
            scan_results["scans"]["cors"] = await self._test_cors()
            scan_results["scans"]["rate_limiting"] = await self._test_rate_limiting()
            scan_results["scans"]["authentication"] = await self._test_authentication()
            scan_results["scans"]["file_upload"] = await self._test_file_upload()
            scan_results["scans"]["information_disclosure"] = await self._test_information_disclosure()
            
            # Calculate overall security score
            scan_results["security_score"] = self._calculate_security_score(scan_results["scans"])
            scan_results["risk_level"] = self._get_risk_level(scan_results["security_score"])
            
            return scan_results
    
    async def _test_sql_injection(self) -> Dict[str, Any]:
        """Test for SQL injection vulnerabilities"""
        test_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' UNION SELECT NULL --",
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin'--",
            "admin' /*",
            "' OR 'x'='x",
            "1' OR '1'='1' /*"
        ]
        
        vulnerable_endpoints = []
        
        # Test common endpoints
        endpoints = [
            "/api/matatu-saccos",
            "/api/matatu-vehicles", 
            "/api/ntsa-inspections",
            "/api/users",
            "/auth/login"
        ]
        
        for endpoint in endpoints:
            for payload in test_payloads:
                try:
                    # Test GET parameter
                    url = f"{self.base_url}{endpoint}?id={payload}"
                    async with self.session.get(url, timeout=10) as response:
                        if await self._analyze_sql_response(response):
                            vulnerable_endpoints.append({
                                "endpoint": endpoint,
                                "method": "GET",
                                "payload": payload,
                                "response_status": response.status,
                                "vulnerability": "SQL Injection"
                            })
                    
                    # Test POST parameter
                    data = {"id": payload}
                    async with self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=10) as response:
                        if await self._analyze_sql_response(response):
                            vulnerable_endpoints.append({
                                "endpoint": endpoint,
                                "method": "POST", 
                                "payload": payload,
                                "response_status": response.status,
                                "vulnerability": "SQL Injection"
                            })
                
                except Exception as e:
                    continue
        
        return {
            "status": "VULNERABLE" if vulnerable_endpoints else "SAFE",
            "vulnerabilities": vulnerable_endpoints,
            "risk_score": len(vulnerable_endpoints) * 10
        }
    
    async def _test_xss(self) -> Dict[str, Any]:
        """Test for XSS vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "';alert('XSS');",
            "<script>document.location='http://evil.com'</script>"
        ]
        
        vulnerable_endpoints = []
        
        # Test endpoints that might reflect input
        endpoints = [
            "/api/matatu-saccos",
            "/api/matatu-vehicles",
            "/search",
            "/api/users/search"
        ]
        
        for endpoint in endpoints:
            for payload in xss_payloads:
                try:
                    # Test search parameter
                    url = f"{self.base_url}{endpoint}?search={payload}"
                    async with self.session.get(url, timeout=10) as response:
                        text = await response.text()
                        if payload in text and "alert" in text:
                            vulnerable_endpoints.append({
                                "endpoint": endpoint,
                                "method": "GET",
                                "payload": payload,
                                "response_status": response.status,
                                "vulnerability": "Cross-Site Scripting (XSS)"
                            })
                    
                    # Test POST data
                    data = {"name": payload, "description": payload}
                    async with self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=10) as response:
                        text = await response.text()
                        if payload in text and "alert" in text:
                            vulnerable_endpoints.append({
                                "endpoint": endpoint,
                                "method": "POST",
                                "payload": payload, 
                                "response_status": response.status,
                                "vulnerability": "Cross-Site Scripting (XSS)"
                            })
                
                except Exception as e:
                    continue
        
        return {
            "status": "VULNERABLE" if vulnerable_endpoints else "SAFE",
            "vulnerabilities": vulnerable_endpoints,
            "risk_score": len(vulnerable_endpoints) * 15
        }
    
    async def _test_directory_traversal(self) -> Dict[str, Any]:
        """Test for directory traversal vulnerabilities"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "....\\\\....\\\\....\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts"
        ]
        
        vulnerable_endpoints = []
        
        # Test file-related endpoints
        endpoints = [
            "/api/files",
            "/uploads",
            "/download",
            "/static",
            "/api/documents"
        ]
        
        for endpoint in endpoints:
            for payload in traversal_payloads:
                try:
                    url = f"{self.base_url}{endpoint}?file={payload}"
                    async with self.session.get(url, timeout=10) as response:
                        text = await response.text()
                        
                        # Check for system file content
                        if "root:" in text or "localhost" in text or "# Copyright" in text:
                            vulnerable_endpoints.append({
                                "endpoint": endpoint,
                                "payload": payload,
                                "response_status": response.status,
                                "vulnerability": "Directory Traversal",
                                "evidence": "System file content detected"
                            })
                
                except Exception as e:
                    continue
        
        return {
            "status": "VULNERABLE" if vulnerable_endpoints else "SAFE", 
            "vulnerabilities": vulnerable_endpoints,
            "risk_score": len(vulnerable_endpoints) * 20
        }
    
    async def _test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        missing_headers = []
        weak_headers = []
        
        try:
            async with self.session.get(self.base_url, timeout=10) as response:
                headers = response.headers
                
                # Check required security headers
                required_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options", 
                    "X-XSS-Protection",
                    "Strict-Transport-Security",
                    "Content-Security-Policy",
                    "Referrer-Policy"
                ]
                
                for header in required_headers:
                    if header not in headers:
                        missing_headers.append(header)
                
                # Check header values
                if "X-Frame-Options" in headers:
                    if headers["X-Frame-Options"] not in ["DENY", "SAMEORIGIN"]:
                        weak_headers.append({
                            "header": "X-Frame-Options",
                            "value": headers["X-Frame-Options"],
                            "issue": "Should be DENY or SAMEORIGIN"
                        })
                
                if "Content-Security-Policy" in headers:
                    csp = headers["Content-Security-Policy"]
                    if "unsafe-inline" in csp or "unsafe-eval" in csp:
                        weak_headers.append({
                            "header": "Content-Security-Policy",
                            "value": csp,
                            "issue": "Contains unsafe directives"
                        })
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if missing_headers or weak_headers else "SAFE",
            "missing_headers": missing_headers,
            "weak_headers": weak_headers,
            "risk_score": (len(missing_headers) + len(weak_headers)) * 5
        }
    
    async def _test_cors(self) -> Dict[str, Any]:
        """Test CORS configuration"""
        cors_issues = []
        
        try:
            # Test with origin header
            headers = {"Origin": "https://evil.com"}
            async with self.session.get(self.base_url, headers=headers, timeout=10) as response:
                if "Access-Control-Allow-Origin" in response.headers:
                    allowed_origin = response.headers["Access-Control-Allow-Origin"]
                    
                    if allowed_origin == "*" or allowed_origin == "https://evil.com":
                        cors_issues.append({
                            "issue": "Overly permissive CORS",
                            "allowed_origin": allowed_origin,
                            "risk": "Allows any origin"
                        })
                
                # Check for credentials
                if "Access-Control-Allow-Credentials" in response.headers:
                    if response.headers["Access-Control-Allow-Credentials"] == "true":
                        if "Access-Control-Allow-Origin" in response.headers:
                            if response.headers["Access-Control-Allow-Origin"] == "*":
                                cors_issues.append({
                                    "issue": "CORS with credentials and wildcard origin",
                                    "risk": "Allows credentials from any origin"
                                })
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if cors_issues else "SAFE",
            "issues": cors_issues,
            "risk_score": len(cors_issues) * 10
        }
    
    async def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting"""
        rate_limit_issues = []
        
        try:
            # Send rapid requests
            responses = []
            for i in range(50):  # Send 50 requests quickly
                try:
                    async with self.session.get(f"{self.base_url}/api/matatu-saccos", timeout=5) as response:
                        responses.append({
                            "status": response.status,
                            "time": time.time()
                        })
                except:
                    responses.append({"status": "timeout", "time": time.time()})
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            # Analyze responses
            status_200 = sum(1 for r in responses if r["status"] == 200)
            status_429 = sum(1 for r in responses if r["status"] == 429)
            
            if status_429 == 0 and status_200 > 20:
                rate_limit_issues.append({
                    "issue": "No rate limiting detected",
                    "requests_200": status_200,
                    "requests_429": status_429,
                    "risk": "Susceptible to DoS attacks"
                })
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if rate_limit_issues else "SAFE",
            "issues": rate_limit_issues,
            "risk_score": len(rate_limit_issues) * 15
        }
    
    async def _test_authentication(self) -> Dict[str, Any]:
        """Test authentication mechanisms"""
        auth_issues = []
        
        try:
            # Test default credentials
            default_creds = [
                {"email": "admin@admin.com", "password": "admin"},
                {"email": "admin", "password": "password"},
                {"email": "test@test.com", "password": "test"},
                {"email": "root", "password": "root"}
            ]
            
            for creds in default_creds:
                async with self.session.post(
                    f"{self.base_url}/auth/login",
                    json=creds,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        auth_issues.append({
                            "issue": "Default credentials work",
                            "credentials": creds,
                            "risk": "Easy unauthorized access"
                        })
            
            # Test session management
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": "test@test.com", "password": "wrongpassword"},
                timeout=10
            ) as response:
                # Check for session cookies
                set_cookie = response.headers.get("Set-Cookie", "")
                if "HttpOnly" not in set_cookie or "Secure" not in set_cookie:
                    auth_issues.append({
                        "issue": "Insecure session cookies",
                        "missing": [h for h in ["HttpOnly", "Secure"] if h not in set_cookie],
                        "risk": "Session hijacking possible"
                    })
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if auth_issues else "SAFE",
            "issues": auth_issues,
            "risk_score": len(auth_issues) * 20
        }
    
    async def _test_file_upload(self) -> Dict[str, Any]:
        """Test file upload security"""
        upload_issues = []
        
        try:
            # Test malicious file upload
            malicious_files = [
                {"name": "malicious.php", "content": "<?php system($_GET['cmd']); ?>"},
                {"name": "shell.jsp", "content": "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"},
                {"name": "script.js", "content": "<script>alert('XSS')</script>"},
                {"name": "huge.txt", "content": "A" * (10 * 1024 * 1024)}  # 10MB
            ]
            
            for file_data in malicious_files:
                data = aiohttp.FormData()
                data.add_field('file', file_data["content"], filename=file_data["name"])
                
                async with self.session.post(
                    f"{self.base_url}/api/upload",
                    data=data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        upload_issues.append({
                            "issue": "Malicious file upload allowed",
                            "file": file_data["name"],
                            "risk": "Code execution possible"
                        })
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if upload_issues else "SAFE",
            "issues": upload_issues,
            "risk_score": len(upload_issues) * 25
        }
    
    async def _test_information_disclosure(self) -> Dict[str, Any]:
        """Test for information disclosure"""
        disclosure_issues = []
        
        # Test common information disclosure paths
        test_paths = [
            "/.env",
            "/config.php",
            "/web.config",
            "/.git/config",
            "/.svn/entries",
            "/backup.sql",
            "/database.sql",
            "/error.log",
            "/access.log",
            "/phpinfo.php",
            "/info.php",
            "/test.php",
            "/admin",
            "/phpmyadmin",
            "/robots.txt",
            "/sitemap.xml"
        ]
        
        for path in test_paths:
            try:
                url = f"{self.base_url}{path}"
                async with self.session.get(url, timeout=10) as response:
                    text = await response.text()
                    
                    # Check for sensitive information
                    sensitive_patterns = [
                        r"password\s*=\s*['\"][^'\"]+['\"]",
                        r"database\s*=\s*['\"][^'\"]+['\"]",
                        r"secret\s*=\s*['\"][^'\"]+['\"]",
                        r"api_key\s*=\s*['\"][^'\"]+['\"]",
                        r"DB_PASSWORD",
                        r"SECRET_KEY"
                    ]
                    
                    for pattern in sensitive_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            disclosure_issues.append({
                                "path": path,
                                "pattern_matched": pattern,
                                "response_status": response.status,
                                "risk": "Sensitive information disclosure"
                            })
                            break
            
            except Exception as e:
                continue
        
        return {
            "status": "VULNERABLE" if disclosure_issues else "SAFE",
            "issues": disclosure_issues,
            "risk_score": len(disclosure_issues) * 12
        }
    
    async def _analyze_sql_response(self, response) -> bool:
        """Analyze response for SQL injection indicators"""
        if response.status == 500:
            return True
        
        try:
            text = await response.text()
            
            # Check for SQL error messages
            sql_errors = [
                "SQL syntax error",
                "mysql_fetch",
                "ORA-",
                "Microsoft OLE DB Provider",
                "ODBC Microsoft Access",
                "PostgreSQL query failed",
                "Warning: mysql",
                "valid MySQL result",
                "MySqlClient."
            ]
            
            for error in sql_errors:
                if error.lower() in text.lower():
                    return True
            
            # Check for unusual response structure
            if response.status == 200 and len(text) < 50:
                return True
        
        except:
            pass
        
        return False
    
    def _calculate_security_score(self, scans: Dict[str, Any]) -> int:
        """Calculate overall security score"""
        total_risk = sum(scan.get("risk_score", 0) for scan in scans.values())
        
        # Convert to security score (100 - risk_score, minimum 0)
        security_score = max(0, 100 - total_risk)
        
        return security_score
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level from security score"""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"

class SecurityTestRunner:
    """Run comprehensive security tests"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.scanner = VulnerabilityScanner(target_url)
    
    async def run_full_scan(self) -> Dict[str, Any]:
        """Run complete security scan"""
        print(f"Starting comprehensive security scan for {self.target_url}")
        
        # Run vulnerability scan
        vuln_results = await self.scanner.scan()
        
        # Add additional security tests
        additional_tests = await self._run_additional_tests()
        
        # Generate report
        report = {
            "scan_metadata": {
                "timestamp": datetime.now().isoformat(),
                "target": self.target_url,
                "scanner_version": "1.0.0"
            },
            "vulnerability_scan": vuln_results,
            "additional_tests": additional_tests,
            "recommendations": self._generate_recommendations(vuln_results, additional_tests)
        }
        
        # Save report
        await self._save_report(report)
        
        return report
    
    async def _run_additional_tests(self) -> Dict[str, Any]:
        """Run additional security tests"""
        results = {}
        
        # Test SSL/TLS configuration
        results["ssl_test"] = await self._test_ssl_configuration()
        
        # Test for common vulnerabilities
        results["common_vulns"] = await self._test_common_vulnerabilities()
        
        # Test API security
        results["api_security"] = await self._test_api_security()
        
        return results
    
    async def _test_ssl_configuration(self) -> Dict[str, Any]:
        """Test SSL/TLS configuration"""
        try:
            parsed_url = urlparse(self.target_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Test SSL connection
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    ssl_info = {
                        "protocol": ssock.version(),
                        "cipher": ssock.cipher(),
                        "cert_subject": cert.get('subject'),
                        "cert_issuer": cert.get('issuer'),
                        "cert_expiry": cert.get('notAfter')
                    }
                    
                    # Check for SSL issues
                    issues = []
                    
                    if ssock.version() in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                        issues.append(f"Weak SSL/TLS version: {ssock.version()}")
                    
                    return {
                        "status": "SECURE" if not issues else "VULNERABLE",
                        "ssl_info": ssl_info,
                        "issues": issues
                    }
        
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _test_common_vulnerabilities(self) -> Dict[str, Any]:
        """Test for common CVEs"""
        # This would integrate with CVE databases
        # For now, return placeholder
        return {
            "status": "NOT_IMPLEMENTED",
            "message": "CVE database integration required"
        }
    
    async def _test_api_security(self) -> Dict[str, Any]:
        """Test API-specific security"""
        api_issues = []
        
        try:
            # Test API versioning
            version_endpoints = ["/api/v1", "/api/v2", "/api/version"]
            for endpoint in version_endpoints:
                try:
                    async with self.session.get(f"{self.target_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            api_issues.append({
                                "issue": "API version exposed",
                                "endpoint": endpoint,
                                "risk": "Information disclosure"
                            })
                except:
                    continue
            
            # Test API documentation exposure
            doc_endpoints = ["/docs", "/swagger", "/api/docs", "/redoc"]
            for endpoint in doc_endpoints:
                try:
                    async with self.session.get(f"{self.target_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            api_issues.append({
                                "issue": "API documentation exposed",
                                "endpoint": endpoint,
                                "risk": "Information disclosure"
                            })
                except:
                    continue
        
        except Exception as e:
            pass
        
        return {
            "status": "VULNERABLE" if api_issues else "SAFE",
            "issues": api_issues
        }
    
    def _generate_recommendations(
        self, 
        vuln_results: Dict[str, Any], 
        additional_tests: Dict[str, Any]
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Analyze vulnerability results
        for scan_name, scan_result in vuln_results["scans"].items():
            if scan_result["status"] == "VULNERABLE":
                if scan_name == "sql_injection":
                    recommendations.extend([
                        "Implement parameterized queries",
                        "Use ORM instead of raw SQL",
                        "Input validation and sanitization",
                        "Web Application Firewall (WAF)"
                    ])
                elif scan_name == "xss":
                    recommendations.extend([
                        "Implement Content Security Policy",
                        "Output encoding",
                        "Input validation",
                        "Use templating engines with auto-escaping"
                    ])
                elif scan_name == "security_headers":
                    recommendations.extend([
                        "Add missing security headers",
                        "Implement Content Security Policy",
                        "Enable HTTPS with HSTS"
                    ])
                elif scan_name == "authentication":
                    recommendations.extend([
                        "Implement strong password policies",
                        "Multi-factor authentication",
                        "Account lockout mechanisms",
                        "Secure session management"
                    ])
        
        # Add general recommendations
        recommendations.extend([
            "Regular security audits",
            "Keep dependencies updated",
            "Implement logging and monitoring",
            "Security training for developers",
            "Incident response plan"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _save_report(self, report: Dict[str, Any]):
        """Save security scan report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security_report_{timestamp}.json"
        
        try:
            with open(f"security_reports/{filename}", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"Security report saved to: {filename}")
        except Exception as e:
            print(f"Failed to save report: {e}")

# Main execution function
async def run_security_scan(target_url: str) -> Dict[str, Any]:
    """Run complete security scan"""
    runner = SecurityTestRunner(target_url)
    return await runner.run_full_scan()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python security_testing.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # Run scan
    results = asyncio.run(run_security_scan(target_url))
    
    # Print summary
    print("\n" + "="*50)
    print("SECURITY SCAN SUMMARY")
    print("="*50)
    print(f"Target: {results['scan_metadata']['target']}")
    print(f"Security Score: {results['vulnerability_scan']['security_score']}")
    print(f"Risk Level: {results['vulnerability_scan']['risk_level']}")
    print(f"Total Vulnerabilities: {sum(len(scan.get('vulnerabilities', [])) for scan in results['vulnerability_scan']['scans'].values())}")
    print(f"Recommendations: {len(results['recommendations'])}")
    print("="*50)
