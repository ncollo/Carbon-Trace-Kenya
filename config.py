from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os


class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore', env_file='.env')
    
    app_name: str = "Carbon Trace Kenya"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./carbon_trace.db")
    database_echo: bool = False
    
    # S3 settings (if using S3 for uploads)
    use_s3: bool = False
    s3_bucket: str = ""
    s3_region: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

    # Redis URL for RQ / background queue
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT settings
    jwt_secret: str = os.getenv("JWT_SECRET", "changeme-dev-only")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = 24
    
    # Supabase credentials (store secrets in env or .env)
    supabase_url: str = ""
    supabase_key: str = ""
    
    # S3 / object storage
    s3_endpoint: str = ""  # optional custom endpoint


settings = Settings()

