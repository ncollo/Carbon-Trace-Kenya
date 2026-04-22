"""
Database Security and Query Protection for Carbon Trace Kenya
SQL injection prevention, query optimization, and database access controls
"""

import re
import hashlib
import time
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import text, event, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

class SQLInjectionDetector:
    """Advanced SQL injection detection and prevention"""
    
    # SQL injection patterns
    INJECTION_PATTERNS = [
        # Basic SQL keywords
        r"(?i)(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(?i)(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(?i)(['\"];?\s*(OR|AND)\s*['\"]?\w+['\"]?\s*=\s*['\"]?\w+)",
        
        # Advanced patterns
        r"(?i)(/\*.*\*/)",
        r"(?i)(--|#)",
        r"(?i)(\bEXEC\s*\(|\bXP_CMDSHELL\b)",
        r"(?i)(\bWAITFOR\s+DELAY\b)",
        r"(?i)(\bBENCHMARK\s*\()",
        r"(?i)(\bSLEEP\s*\()",
        
        # Time-based attacks
        r"(?i)(\bPG_SLEEP\s*\()",
        r"(?i)(\bDBMS_PIPE\s*RECEIVE_MESSAGE\b)",
        
        # Boolean-based attacks
        r"(?i)(\bCAST\s*\()",
        r"(?i)(\bCONVERT\s*\()",
        r"(?i)(\bCHAR\s*\()",
        r"(?i)(\bASCII\s*\()",
        
        # Union-based attacks
        r"(?i)(\bUNION\s+ALL\s+SELECT\b)",
        r"(?i)(\bUNION\s+SELECT\b)",
        
        # Error-based attacks
        r"(?i)(\bEXTRACTVALUE\s*\()",
        r"(?i)(\bUPDATExML\s*\()",
        r"(?i)(\bFLOOR\s*\()",
        r"(?i)(\bRAND\s*\()",
        
        # NoSQL injection (for MongoDB if used)
        r"(?i)(\$where|\$ne|\$gt|\$lt|\$regex|\$expr)",
        r"(?i)(\{\s*\$.*\})",
    ]
    
    @staticmethod
    def detect_injection(input_string: str) -> Dict[str, Any]:
        """Detect SQL injection attempts"""
        if not input_string:
            return {"detected": False, "patterns": [], "risk_score": 0}
        
        detected_patterns = []
        risk_score = 0
        
        for pattern in SQLInjectionDetector.INJECTION_PATTERNS:
            matches = re.findall(pattern, input_string)
            if matches:
                detected_patterns.append({
                    "pattern": pattern,
                    "matches": matches,
                    "severity": SQLInjectionDetector._get_pattern_severity(pattern)
                })
                risk_score += SQLInjectionDetector._get_pattern_severity(pattern)
        
        # Additional heuristic checks
        risk_score += SQLInjectionDetector._heuristic_check(input_string)
        
        return {
            "detected": len(detected_patterns) > 0 or risk_score > 0,
            "patterns": detected_patterns,
            "risk_score": min(risk_score, 100),  # Cap at 100
            "risk_level": SQLInjectionDetector._get_risk_level(risk_score)
        }
    
    @staticmethod
    def _get_pattern_severity(pattern: str) -> int:
        """Get severity score for pattern"""
        high_severity = [
            r"(?i)(\bEXEC\s*\(|\bXP_CMDSHELL\b)",
            r"(?i)(\bWAITFOR\s+DELAY\b)",
            r"(?i)(\bBENCHMARK\s*\()",
            r"(?i)(\bSLEEP\s*\()",
            r"(?i)(\bPG_SLEEP\s*\()"
        ]
        
        medium_severity = [
            r"(?i)(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(?i)(\bUNION\s+ALL\s+SELECT\b)",
            r"(?i)(\bEXTRACTVALUE\s*\()",
            r"(?i)(\bUPDATExML\s*\()"
        ]
        
        if any(re.search(high_pat, pattern) for high_pat in high_severity):
            return 30
        elif any(re.search(med_pat, pattern) for med_pat in medium_severity):
            return 20
        else:
            return 10
    
    @staticmethod
    def _heuristic_check(input_string: str) -> int:
        """Additional heuristic checks"""
        score = 0
        
        # Check for multiple quotes
        if input_string.count("'") > 2 or input_string.count('"') > 2:
            score += 15
        
        # Check for comment markers
        if '--' in input_string or '/*' in input_string:
            score += 20
        
        # Check for logical operators
        if re.search(r'\b(OR|AND)\b.*\b(OR|AND)\b', input_string, re.IGNORECASE):
            score += 15
        
        # Check for encoded content
        if re.search(r'%[0-9A-Fa-f]{2}', input_string):
            score += 10
        
        # Check for suspicious characters sequence
        if re.search(r"[\'\"][\s]*[=+\-*/][\s]*[\'\"]", input_string):
            score += 25
        
        return score
    
    @staticmethod
    def _get_risk_level(score: int) -> str:
        """Get risk level based on score"""
        if score >= 70:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        elif score >= 10:
            return "LOW"
        else:
            return "SAFE"

class QuerySecurity:
    """Query security and optimization"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger("query_security")
    
    def secure_execute(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Any:
        """Execute query with security checks"""
        
        # SQL injection detection
        injection_result = SQLInjectionDetector.detect_injection(query)
        
        if injection_result["detected"]:
            self.logger.warning(
                f"SQL injection attempt detected: {injection_result}"
            )
            raise SecurityException(
                f"Potential SQL injection detected. Risk level: {injection_result['risk_level']}"
            )
        
        # Query complexity check
        complexity_score = self._analyze_query_complexity(query)
        if complexity_score > 100:
            self.logger.warning(f"Complex query detected: {complexity_score}")
            raise SecurityException("Query too complex")
        
        # Execute with timeout
        start_time = time.time()
        
        try:
            result = self.db_session.execute(
                text(query),
                params or {},
                execution_options={"timeout": timeout}
            )
            
            execution_time = time.time() - start_time
            
            # Log slow queries
            if execution_time > 5:  # 5 seconds threshold
                self.logger.warning(
                    f"Slow query detected: {execution_time:.2f}s - {query[:100]}..."
                )
            
            return result
            
        except SQLAlchemyError as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def _analyze_query_complexity(self, query: str) -> int:
        """Analyze query complexity"""
        complexity = 0
        
        # Count JOIN operations
        joins = len(re.findall(r'\bJOIN\b', query, re.IGNORECASE))
        complexity += joins * 10
        
        # Count subqueries
        subqueries = len(re.findall(r'\bSELECT\b.*\bFROM\b.*\bWHERE\b', query, re.IGNORECASE))
        complexity += subqueries * 15
        
        # Count UNION operations
        unions = len(re.findall(r'\bUNION\b', query, re.IGNORECASE))
        complexity += unions * 20
        
        # Check for nested queries
        nesting_level = query.count('(') - query.count(')')
        complexity += abs(nesting_level) * 5
        
        # Check for aggregate functions
        aggregates = len(re.findall(r'\b(COUNT|SUM|AVG|MAX|MIN|GROUP_CONCAT)\b', query, re.IGNORECASE))
        complexity += aggregates * 8
        
        # Check for window functions
        window_functions = len(re.findall(r'\b(ROW_NUMBER|RANK|DENSE_RANK|LAG|LEAD)\b', query, re.IGNORECASE))
        complexity += window_functions * 12
        
        return complexity

class DatabaseAccessControl:
    """Database access control and permissions"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_permissions = {}
    
    def check_table_access(
        self,
        user_id: int,
        table_name: str,
        operation: str  # SELECT, INSERT, UPDATE, DELETE
    ) -> bool:
        """Check if user has access to table"""
        
        # Get user role and permissions
        user_role = self._get_user_role(user_id)
        permissions = self._get_role_permissions(user_role)
        
        # Table-specific permissions
        table_permissions = permissions.get('tables', {}).get(table_name, {})
        
        # Check operation permission
        operation_key = f"can_{operation.lower()}"
        return table_permissions.get(operation_key, False)
    
    def check_column_access(
        self,
        user_id: int,
        table_name: str,
        column_name: str,
        operation: str
    ) -> bool:
        """Check if user has access to specific column"""
        
        if not self.check_table_access(user_id, table_name, operation):
            return False
        
        # Check for sensitive column access
        sensitive_columns = self._get_sensitive_columns(table_name)
        
        if column_name in sensitive_columns:
            user_role = self._get_user_role(user_id)
            return user_role in ['admin', 'analyst']
        
        return True
    
    def _get_user_role(self, user_id: int) -> str:
        """Get user role from database"""
        try:
            from db.models import User
            user = self.db_session.query(User).filter(User.id == user_id).first()
            return user.role if user else 'viewer'
        except:
            return 'viewer'
    
    def _get_role_permissions(self, role: str) -> Dict[str, Any]:
        """Get permissions for role"""
        permissions = {
            'admin': {
                'tables': {
                    'companies': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'users': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'matatu_saccos': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'matatu_vehicles': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'ntsa_inspections': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'emissions': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
                    'audit_logs': {'can_select': True, 'can_insert': True, 'can_update': False, 'can_delete': False}
                }
            },
            'analyst': {
                'tables': {
                    'companies': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'users': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'matatu_saccos': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'matatu_vehicles': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'ntsa_inspections': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'emissions': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
                    'audit_logs': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False}
                }
            },
            'user': {
                'tables': {
                    'companies': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'users': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'matatu_saccos': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
                    'matatu_vehicles': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
                    'ntsa_inspections': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
                    'emissions': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
                    'audit_logs': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False}
                }
            },
            'viewer': {
                'tables': {
                    'companies': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'users': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'matatu_saccos': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'matatu_vehicles': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'ntsa_inspections': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'emissions': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
                    'audit_logs': {'can_select': False, 'can_insert': False, 'can_update': False, 'can_delete': False}
                }
            }
        }
        
        return permissions.get(role, permissions['viewer'])
    
    def _get_sensitive_columns(self, table_name: str) -> List[str]:
        """Get list of sensitive columns for table"""
        sensitive_columns = {
            'users': ['password_hash', 'email', 'phone'],
            'matatu_saccos': ['contact_phone', 'contact_email'],
            'matatu_vehicles': ['registration_number'],
            'companies': [],
            'ntsa_inspections': ['inspector_id'],
            'emissions': [],
            'audit_logs': []
        }
        
        return sensitive_columns.get(table_name, [])

class SecurityException(Exception):
    """Custom security exception"""
    pass

class DatabaseAuditor:
    """Database security auditor"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.logger = logging.getLogger("database_auditor")
    
    def audit_database_security(self) -> Dict[str, Any]:
        """Comprehensive database security audit"""
        audit_results = {
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check for exposed sensitive data
        audit_results["checks"]["sensitive_data_exposure"] = self._check_sensitive_data_exposure()
        
        # Check for weak passwords
        audit_results["checks"]["weak_passwords"] = self._check_weak_passwords()
        
        # Check for excessive permissions
        audit_results["checks"]["excessive_permissions"] = self._check_excessive_permissions()
        
        # Check for orphaned records
        audit_results["checks"]["orphaned_records"] = self._check_orphaned_records()
        
        # Check for data integrity
        audit_results["checks"]["data_integrity"] = self._check_data_integrity()
        
        # Calculate overall security score
        audit_results["security_score"] = self._calculate_security_score(audit_results["checks"])
        
        return audit_results
    
    def _check_sensitive_data_exposure(self) -> Dict[str, Any]:
        """Check for sensitive data exposure"""
        issues = []
        
        # Check for unencrypted sensitive columns
        try:
            result = self.db_session.execute(text("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND column_name LIKE '%password%'
                OR column_name LIKE '%email%'
                OR column_name LIKE '%phone%'
            """))
            
            for row in result:
                issues.append(f"Sensitive column exposed: {row.table_name}.{row.column_name}")
        
        except Exception as e:
            issues.append(f"Failed to check sensitive data: {e}")
        
        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues
        }
    
    def _check_weak_passwords(self) -> Dict[str, Any]:
        """Check for weak passwords"""
        issues = []
        
        try:
            from db.models import User
            
            users = self.db_session.query(User).all()
            
            for user in users:
                # Check for common weak passwords
                weak_passwords = ['password', '123456', 'admin', 'qwerty', 'letmein']
                
                for weak_pwd in weak_passwords:
                    # This is a simplified check - in practice, you'd use password hash verification
                    if user.password_hash and weak_pwd in user.password_hash.lower():
                        issues.append(f"User {user.email} may have weak password")
                        break
        
        except Exception as e:
            issues.append(f"Failed to check passwords: {e}")
        
        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues
        }
    
    def _check_excessive_permissions(self) -> Dict[str, Any]:
        """Check for excessive user permissions"""
        issues = []
        
        try:
            # Check for non-admin users with admin-like permissions
            result = self.db_session.execute(text("""
                SELECT COUNT(*) as count
                FROM users 
                WHERE role != 'admin' 
                AND created_at > NOW() - INTERVAL '7 days'
            """))
            
            count = result.fetchone().count
            if count > 10:  # Threshold for new non-admin users
                issues.append(f"High number of new non-admin users: {count}")
        
        except Exception as e:
            issues.append(f"Failed to check permissions: {e}")
        
        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues
        }
    
    def _check_orphaned_records(self) -> Dict[str, Any]:
        """Check for orphaned records"""
        issues = []
        
        try:
            # Check for vehicles without SACCO
            result = self.db_session.execute(text("""
                SELECT COUNT(*) as count
                FROM matatu_vehicles mv
                LEFT JOIN matatu_saccos ms ON mv.sacco_id = ms.id
                WHERE ms.id IS NULL
            """))
            
            count = result.fetchone().count
            if count > 0:
                issues.append(f"Orphaned vehicles: {count}")
            
            # Check for inspections without vehicles
            result = self.db_session.execute(text("""
                SELECT COUNT(*) as count
                FROM ntsa_inspections ni
                LEFT JOIN matatu_vehicles mv ON ni.vehicle_id = mv.id
                WHERE mv.id IS NULL
            """))
            
            count = result.fetchone().count
            if count > 0:
                issues.append(f"Orphaned inspections: {count}")
        
        except Exception as e:
            issues.append(f"Failed to check orphaned records: {e}")
        
        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues
        }
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity issues"""
        issues = []
        
        try:
            # Check for duplicate registration numbers
            result = self.db_session.execute(text("""
                SELECT registration_number, COUNT(*) as count
                FROM matatu_vehicles
                GROUP BY registration_number
                HAVING COUNT(*) > 1
            """))
            
            for row in result:
                issues.append(f"Duplicate registration number: {row.registration_number}")
            
            # Check for invalid dates
            result = self.db_session.execute(text("""
                SELECT COUNT(*) as count
                FROM ntsa_inspections
                WHERE inspection_date > NOW()
            """))
            
            count = result.fetchone().count
            if count > 0:
                issues.append(f"Future inspection dates: {count}")
        
        except Exception as e:
            issues.append(f"Failed to check data integrity: {e}")
        
        return {
            "status": "PASS" if not issues else "FAIL",
            "issues": issues
        }
    
    def _calculate_security_score(self, checks: Dict[str, Any]) -> int:
        """Calculate overall security score"""
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check["status"] == "PASS")
        
        return int((passed_checks / total_checks) * 100)

# SQLAlchemy event listeners for security
@event.listens_for(engine, "before_execute")
def receive_before_execute(conn, clauseelement, multiparams, params, execution_options):
    """Log all queries before execution"""
    query_str = str(clauseelement)
    
    # Check for SQL injection
    injection_result = SQLInjectionDetector.detect_injection(query_str)
    
    if injection_result["detected"]:
        logging.warning(
            f"SQL injection attempt blocked: {injection_result['risk_level']} - {query_str[:100]}..."
        )
        raise SecurityException("SQL injection detected")
    
    # Log query (in production, you might want to log only sensitive queries)
    logging.debug(f"Executing query: {query_str[:200]}...")

@event.listens_for(engine, "after_execute")
def receive_after_execute(conn, clauseelement, multiparams, params, result, execution_options):
    """Log query execution results"""
    execution_time = execution_options.get('timeout', 0)
    
    if execution_time > 5:  # Log slow queries
        logging.warning(f"Slow query executed: {execution_time}s")

# Global instances
def get_query_security(db_session: Session) -> QuerySecurity:
    """Get query security instance"""
    return QuerySecurity(db_session)

def get_database_access_control(db_session: Session) -> DatabaseAccessControl:
    """Get database access control instance"""
    return DatabaseAccessControl(db_session)

def get_database_auditor(db_session: Session) -> DatabaseAuditor:
    """Get database auditor instance"""
    return DatabaseAuditor(db_session)
