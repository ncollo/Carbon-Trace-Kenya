from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Carbon Trace Kenya"
    database_url: str = "postgresql://user:pass@localhost:5432/carbon"
    # S3 settings (if using S3 for uploads)
    use_s3: bool = False
    s3_bucket: str = ""
    s3_region: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""

    # Redis URL for RQ / background queue
    redis_url: str = "redis://localhost:6379/0"
    # JWT settings
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    # Supabase credentials (store secrets in env or .env)
    supabase_url: str = ""
    supabase_key: str = ""
    # S3 / object storage
    use_s3: bool = False
    s3_endpoint: str = ""  # optional custom endpoint
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "carbon-trace-uploads"

    # Redis / RQ
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
