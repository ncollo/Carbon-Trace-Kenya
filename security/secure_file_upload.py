"""
Secure File Upload Handling for Carbon Trace Kenya
Comprehensive file security with virus scanning, validation, and safe storage
"""

import os
import hashlib
import magic
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
import shutil
from PIL import Image
import pdfplumber
import pandas as pd
from fastapi import UploadFile, HTTPException, status
import aiofiles
import asyncio
from datetime import datetime

class FileSecurityConfig:
    """Configuration for secure file uploads"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'data': ['.json', '.xml', '.yaml', '.yml']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'documents': 50 * 1024 * 1024,  # 50MB
        'images': 10 * 1024 * 1024,     # 10MB
        'data': 5 * 1024 * 1024,        # 5MB
        'default': 10 * 1024 * 1024      # 10MB
    }
    
    # MIME type whitelist
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/webp',
        'application/json',
        'text/xml',
        'application/xml',
        'application/x-yaml',
        'text/yaml'
    }
    
    # Dangerous file patterns
    DANGEROUS_PATTERNS = [
        r'\.exe$', r'\.bat$', r'\.cmd$', r'\.scr$', r'\.pif$',
        r'\.com$', r'\.vbs$', r'\.js$', r'\.jar$', r'\.php$',
        r'\.asp$', r'\.jsp$', r'\.sh$', r'\.ps1$', r'\.py$'
    ]

class FileValidator:
    """File validation and security checking"""
    
    @staticmethod
    def validate_filename(filename: str) -> Dict[str, Any]:
        """Validate filename for security"""
        errors = []
        
        if not filename:
            errors.append("Filename is required")
            return {"valid": False, "errors": errors}
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            errors.append("Path traversal detected in filename")
        
        # Check for dangerous extensions
        import re
        for pattern in FileSecurityConfig.DANGEROUS_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                errors.append(f"Dangerous file extension detected: {filename}")
        
        # Check length
        if len(filename) > 255:
            errors.append("Filename too long (max 255 characters)")
        
        # Check for null bytes
        if '\x00' in filename:
            errors.append("Null bytes detected in filename")
        
        # Check for special characters
        if any(char in filename for char in ['<', '>', ':', '"', '|', '?', '*']):
            errors.append("Invalid characters in filename")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized_filename": FileValidator._sanitize_filename(filename)
        }
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Replace dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def validate_file_content(file_path: str, original_filename: str) -> Dict[str, Any]:
        """Validate actual file content"""
        errors = []
        warnings = []
        
        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            
            # Check file size
            max_size = FileValidator._get_max_file_size(original_filename)
            if file_size > max_size:
                errors.append(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
            
            # Get MIME type
            mime_type = magic.from_file(file_path, mime=True)
            
            # Check MIME type
            if mime_type not in FileSecurityConfig.ALLOWED_MIME_TYPES:
                errors.append(f"File type not allowed: {mime_type}")
            
            # Check extension vs MIME type mismatch
            ext = os.path.splitext(original_filename)[1].lower()
            expected_mimes = FileValidator._get_expected_mime_types(ext)
            
            if expected_mimes and mime_type not in expected_mimes:
                warnings.append(f"File extension {ext} doesn't match MIME type {mime_type}")
            
            # Content-specific validation
            if mime_type.startswith('image/'):
                image_validation = FileValidator._validate_image(file_path)
                errors.extend(image_validation['errors'])
                warnings.extend(image_validation['warnings'])
            
            elif mime_type == 'application/pdf':
                pdf_validation = FileValidator._validate_pdf(file_path)
                errors.extend(pdf_validation['errors'])
                warnings.extend(pdf_validation['warnings'])
            
            elif mime_type in ['text/csv', 'application/vnd.ms-excel', 
                              'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                csv_validation = FileValidator._validate_spreadsheet(file_path, mime_type)
                errors.extend(csv_validation['errors'])
                warnings.extend(csv_validation['warnings'])
            
        except Exception as e:
            errors.append(f"Error validating file content: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "mime_type": magic.from_file(file_path, mime=True),
            "file_size": os.path.getsize(file_path)
        }
    
    @staticmethod
    def _get_max_file_size(filename: str) -> int:
        """Get maximum file size for file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        for category, extensions in FileSecurityConfig.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return FileSecurityConfig.MAX_FILE_SIZES.get(category, 
                                                    FileSecurityConfig.MAX_FILE_SIZES['default'])
        
        return FileSecurityConfig.MAX_FILE_SIZES['default']
    
    @staticmethod
    def _get_expected_mime_types(extension: str) -> Optional[List[str]]:
        """Get expected MIME types for extension"""
        mime_mapping = {
            '.pdf': ['application/pdf'],
            '.doc': ['application/msword'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.txt': ['text/plain'],
            '.csv': ['text/csv'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.xls': ['application/vnd.ms-excel'],
            '.jpg': ['image/jpeg'],
            '.jpeg': ['image/jpeg'],
            '.png': ['image/png'],
            '.gif': ['image/gif'],
            '.bmp': ['image/bmp'],
            '.webp': ['image/webp'],
            '.json': ['application/json'],
            '.xml': ['application/xml', 'text/xml'],
            '.yaml': ['application/x-yaml', 'text/yaml'],
            '.yml': ['application/x-yaml', 'text/yaml']
        }
        
        return mime_mapping.get(extension.lower())
    
    @staticmethod
    def _validate_image(file_path: str) -> Dict[str, Any]:
        """Validate image file"""
        errors = []
        warnings = []
        
        try:
            with Image.open(file_path) as img:
                # Check for image bombs (very large dimensions)
                if img.width > 10000 or img.height > 10000:
                    errors.append("Image dimensions too large (potential image bomb)")
                
                # Check for suspicious metadata
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data and len(exif_data) > 1000:
                        warnings.append("Image contains excessive metadata")
                
        except Exception as e:
            errors.append(f"Invalid image file: {str(e)}")
        
        return {"errors": errors, "warnings": warnings}
    
    @staticmethod
    def _validate_pdf(file_path: str) -> Dict[str, Any]:
        """Validate PDF file"""
        errors = []
        warnings = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Check for excessive pages
                if len(pdf.pages) > 1000:
                    warnings.append("PDF has excessive number of pages")
                
                # Check for JavaScript
                if hasattr(pdf, 'js') and pdf.js:
                    errors.append("PDF contains JavaScript (potential security risk)")
                
                # Check file size vs page count ratio
                file_size = os.path.getsize(file_path)
                avg_size_per_page = file_size / len(pdf.pages) if len(pdf.pages) > 0 else 0
                
                if avg_size_per_page > 10 * 1024 * 1024:  # 10MB per page
                    warnings.append("PDF pages are unusually large")
        
        except Exception as e:
            errors.append(f"Invalid PDF file: {str(e)}")
        
        return {"errors": errors, "warnings": warnings}
    
    @staticmethod
    def _validate_spreadsheet(file_path: str, mime_type: str) -> Dict[str, Any]:
        """Validate spreadsheet file"""
        errors = []
        warnings = []
        
        try:
            if mime_type == 'text/csv':
                df = pd.read_csv(file_path, nrows=1000)  # Limit to prevent resource exhaustion
                
                # Check for excessive columns
                if len(df.columns) > 1000:
                    warnings.append("Spreadsheet has excessive number of columns")
                
                # Check for data injection patterns
                for col in df.columns:
                    if any(pattern in str(col).lower() for pattern in ['<script', 'javascript:', 'vbscript:']):
                        errors.append("Potential script injection detected in column names")
                        break
            
            elif 'excel' in mime_type:
                if mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    df = pd.read_excel(file_path, nrows=1000)
                else:
                    df = pd.read_excel(file_path, nrows=1000)
                
                # Similar validation as CSV
                if len(df.columns) > 1000:
                    warnings.append("Spreadsheet has excessive number of columns")
        
        except Exception as e:
            errors.append(f"Invalid spreadsheet file: {str(e)}")
        
        return {"errors": errors, "warnings": warnings}

class SecureFileHandler:
    """Secure file upload and storage handler"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "documents").mkdir(exist_ok=True)
        (self.upload_dir / "images").mkdir(exist_ok=True)
        (self.upload_dir / "data").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
    
    async def handle_upload(
        self,
        file: UploadFile,
        user_id: int,
        category: str = "documents"
    ) -> Dict[str, Any]:
        """Handle secure file upload"""
        
        # Validate filename
        filename_validation = FileValidator.validate_filename(file.filename or "")
        
        if not filename_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid filename",
                    "details": filename_validation["errors"]
                }
            )
        
        sanitized_filename = filename_validation["sanitized_filename"]
        
        # Create temporary file
        temp_path = self.upload_dir / "temp" / f"temp_{user_id}_{int(datetime.now().timestamp())}"
        
        try:
            # Save file temporarily
            async with aiofiles.open(temp_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Validate file content
            content_validation = FileValidator.validate_file_content(
                str(temp_path), 
                sanitized_filename
            )
            
            if not content_validation["valid"]:
                os.remove(temp_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "File validation failed",
                        "details": content_validation["errors"]
                    }
                )
            
            # Generate secure filename
            secure_filename = self._generate_secure_filename(
                sanitized_filename, 
                user_id, 
                category
            )
            
            # Move to permanent location
            final_path = self.upload_dir / category / secure_filename
            
            if final_path.exists():
                # Generate unique filename if exists
                secure_filename = self._generate_unique_filename(
                    secure_filename, 
                    category
                )
                final_path = self.upload_dir / category / secure_filename
            
            shutil.move(str(temp_path), str(final_path))
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(str(final_path))
            
            # Get file metadata
            metadata = self._extract_file_metadata(str(final_path))
            
            return {
                "success": True,
                "filename": secure_filename,
                "original_filename": sanitized_filename,
                "category": category,
                "file_size": content_validation["file_size"],
                "mime_type": content_validation["mime_type"],
                "file_hash": file_hash,
                "metadata": metadata,
                "warnings": content_validation["warnings"],
                "upload_path": str(final_path)
            }
        
        except HTTPException:
            raise
        except Exception as e:
            # Clean up temp file
            if temp_path.exists():
                os.remove(temp_path)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {str(e)}"
            )
    
    def _generate_secure_filename(
        self, 
        filename: str, 
        user_id: int, 
        category: str
    ) -> str:
        """Generate secure filename"""
        timestamp = int(datetime.now().timestamp())
        ext = os.path.splitext(filename)[1]
        
        # Use user ID and timestamp for uniqueness
        secure_name = f"user_{user_id}_{timestamp}{ext}"
        
        return secure_name
    
    def _generate_unique_filename(self, filename: str, category: str) -> str:
        """Generate unique filename if exists"""
        name, ext = os.path.splitext(filename)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}{ext}"
            if not (self.upload_dir / category / new_filename).exists():
                return new_filename
            counter += 1
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract file metadata"""
        metadata = {
            "created_at": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path)
        }
        
        try:
            # Image metadata
            with Image.open(file_path) as img:
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                })
        except:
            pass
        
        try:
            # PDF metadata
            with pdfplumber.open(file_path) as pdf:
                metadata.update({
                    "pages": len(pdf.pages),
                    "pdf_version": getattr(pdf, 'pdf_version', 'unknown')
                })
        except:
            pass
        
        return metadata
    
    def delete_file(self, filename: str, category: str = "documents") -> bool:
        """Securely delete a file"""
        file_path = self.upload_dir / category / filename
        
        if not file_path.exists():
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
    
    def get_file_info(self, filename: str, category: str = "documents") -> Optional[Dict[str, Any]]:
        """Get file information"""
        file_path = self.upload_dir / category / filename
        
        if not file_path.exists():
            return None
        
        return {
            "filename": filename,
            "category": category,
            "file_size": os.path.getsize(file_path),
            "file_hash": self._calculate_file_hash(str(file_path)),
            "metadata": self._extract_file_metadata(str(file_path)),
            "exists": True
        }

# Global file handler instance
def get_secure_file_handler(upload_dir: str = "uploads") -> SecureFileHandler:
    """Get secure file handler instance"""
    return SecureFileHandler(upload_dir)
