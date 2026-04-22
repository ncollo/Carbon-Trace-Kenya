"""
Audit Logging System for Carbon Trace Kenya
Comprehensive logging of all data access and modifications
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
import hashlib

class AuditAction(Enum):
    """Audit action types"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    SEARCH = "SEARCH"
    FAILED_LOGIN = "FAILED_LOGIN"
    PERMISSION_DENIED = "PERMISSION_DENIED"

class AuditResource(Enum):
    """Audit resource types"""
    USER = "USER"
    COMPANY = "COMPANY"
    MATATU_SACCO = "MATATU_SACCO"
    MATATU_VEHICLE = "MATATU_VEHICLE"
    NTSA_INSPECTION = "NTSA_INSPECTION"
    EMISSION_DATA = "EMISSION_DATA"
    UPLOAD_FILE = "UPLOAD_FILE"
    REPORT = "REPORT"
    SYSTEM = "SYSTEM"

class AuditSeverity(Enum):
    """Audit severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# Database models for audit logs
Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    severity = Column(String(20), default=AuditSeverity.LOW.value, nullable=False)
    success = Column(String(10), default="YES", nullable=False)
    error_message = Column(Text, nullable=True)
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class AuditLogEntry(BaseModel):
    """Pydantic model for audit log entries"""
    timestamp: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: str
    user_agent: Optional[str] = None
    details: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    severity: str = AuditSeverity.LOW.value
    success: str = "YES"
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

class AuditLogger:
    """Main audit logging service"""
    
    def __init__(self, db_session, logger_name: str = "audit"):
        self.db_session = db_session
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup audit logger with file handler"""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # File handler for audit logs
        handler = logging.FileHandler("logs/audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_action(
        self,
        action: AuditAction,
        resource: AuditResource,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log an audit action"""
        
        # Create audit log entry
        audit_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action.value,
            resource=resource.value,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            severity=severity.value,
            success="YES" if success else "NO",
            error_message=error_message,
            session_id=session_id,
            request_id=request_id
        )
        
        try:
            # Save to database
            self.db_session.add(audit_entry)
            self.db_session.commit()
            
            # Also log to file
            log_message = self._format_log_message(audit_entry)
            self.logger.info(log_message)
            
        except Exception as e:
            self.logger.error(f"Failed to log audit entry: {e}")
            self.db_session.rollback()
    
    def _format_log_message(self, audit_entry: AuditLog) -> str:
        """Format audit log message"""
        status = "SUCCESS" if audit_entry.success == "YES" else "FAILED"
        
        message = f"[{status}] {audit_entry.action} {audit_entry.resource}"
        
        if audit_entry.user_email:
            message += f" by {audit_entry.user_email}"
        
        if audit_entry.resource_id:
            message += f" ID:{audit_entry.resource_id}"
        
        if audit_entry.details:
            message += f" - {audit_entry.details}"
        
        if audit_entry.error_message:
            message += f" ERROR: {audit_entry.error_message}"
        
        return message
    
    def log_login(
        self,
        user_id: int,
        user_email: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log user login attempt"""
        action = AuditAction.LOGIN if success else AuditAction.FAILED_LOGIN
        severity = AuditSeverity.HIGH if not success else AuditSeverity.LOW
        
        self.log_action(
            action=action,
            resource=AuditResource.USER,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"User login attempt",
            severity=severity,
            success=success,
            error_message=error_message
        )
    
    def log_data_access(
        self,
        resource: AuditResource,
        resource_id: str,
        user_id: int,
        user_email: str,
        ip_address: str,
        access_type: str = "READ",
        details: Optional[str] = None
    ):
        """Log data access"""
        action = AuditAction.READ if access_type == "READ" else AuditAction.UPDATE
        
        self.log_action(
            action=action,
            resource=resource,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details=f"Data {access_type.lower()} on {resource.value.lower()}" + (f": {details}" if details else "")
        )
    
    def log_data_modification(
        self,
        resource: AuditResource,
        resource_id: str,
        user_id: int,
        user_email: str,
        ip_address: str,
        action: AuditAction,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        details: Optional[str] = None
    ):
        """Log data modification"""
        severity = AuditSeverity.MEDIUM
        
        # High severity for critical operations
        if resource in [AuditResource.USER, AuditResource.COMPANY]:
            severity = AuditSeverity.HIGH
        
        self.log_action(
            action=action,
            resource=resource,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            old_values=old_values,
            new_values=new_values,
            details=details,
            severity=severity
        )
    
    def log_file_operation(
        self,
        operation: str,
        filename: str,
        user_id: int,
        user_email: str,
        ip_address: str,
        file_size: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log file operations"""
        action_map = {
            "upload": AuditAction.UPLOAD,
            "download": AuditAction.DOWNLOAD,
            "export": AuditAction.EXPORT
        }
        
        action = action_map.get(operation.lower(), AuditAction.UPLOAD)
        severity = AuditSeverity.MEDIUM if file_size and file_size > 10 * 1024 * 1024 else AuditSeverity.LOW
        
        details = f"File {operation}: {filename}"
        if file_size:
            details += f" ({file_size} bytes)"
        
        self.log_action(
            action=action,
            resource=AuditResource.UPLOAD_FILE,
            resource_id=filename,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details=details,
            severity=severity,
            success=success,
            error_message=error_message
        )
    
    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        ip_address: str = "unknown",
        details: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.HIGH
    ):
        """Log security events"""
        self.log_action(
            action=AuditAction.PERMISSION_DENIED,
            resource=AuditResource.SYSTEM,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details=f"Security event: {event_type}" + (f" - {details}" if details else ""),
            severity=severity,
            success=False
        )
    
    def get_audit_trail(
        self,
        user_id: Optional[int] = None,
        resource: Optional[AuditResource] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail with filters"""
        query = self.db_session.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if resource:
            query = query.filter(AuditLog.resource == resource.value)
        
        if action:
            query = query.filter(AuditLog.action == action.value)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        resource: Optional[AuditResource] = None
    ) -> Dict[str, Any]:
        """Generate audit report"""
        query = self.db_session.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        )
        
        if resource:
            query = query.filter(AuditLog.resource == resource.value)
        
        logs = query.all()
        
        # Generate statistics
        total_actions = len(logs)
        failed_actions = len([log for log in logs if log.success == "NO"])
        unique_users = len(set([log.user_email for log in logs if log.user_email]))
        
        action_counts = {}
        resource_counts = {}
        severity_counts = {}
        
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            resource_counts[log.resource] = resource_counts.get(log.resource, 0) + 1
            severity_counts[log.severity] = severity_counts.get(log.severity, 0) + 1
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "failed_actions": failed_actions,
                "success_rate": ((total_actions - failed_actions) / total_actions * 100) if total_actions > 0 else 0,
                "unique_users": unique_users
            },
            "breakdown": {
                "by_action": action_counts,
                "by_resource": resource_counts,
                "by_severity": severity_counts
            }
        }

# Decorator for automatic audit logging
def audit_action(action: AuditAction, resource: AuditResource):
    """Decorator to automatically audit function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract user info from kwargs or request context
            user_id = kwargs.get('user_id')
            user_email = kwargs.get('user_email')
            ip_address = kwargs.get('ip_address', 'unknown')
            
            # Get audit logger
            from sqlalchemy.orm import sessionmaker
            # This would be injected from the application context
            
            try:
                result = func(*args, **kwargs)
                # Log successful action
                return result
            except Exception as e:
                # Log failed action
                pass
        return wrapper
    return decorator

# Global audit logger instance
def get_audit_logger(db_session) -> AuditLogger:
    """Get audit logger instance"""
    return AuditLogger(db_session)
