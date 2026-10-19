import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Project root is 2 levels up from backend/app/core
BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BACKEND_DIR.parent

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Autonomous Customer Support Platform"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_SECRET: str = os.getenv("APP_SECRET", "autonomous-support-platform-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Euri LLM Gateway
    EURI_API_KEY: str = os.getenv("EURI_API_KEY", "")
    EURI_BASE_URL: str = os.getenv("EURI_BASE_URL", "https://api.euron.one/api/v1/euri")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-6-luna")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

    # Neon PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./support.db")
    ASYNC_DATABASE_URL: str = os.getenv("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./support.db")

    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "support-knowledge-base")
    PINECONE_HOST: str = os.getenv("PINECONE_HOST", "")

    # Clerk SSO Authentication
    CLERK_PUBLISHABLE_KEY: str = os.getenv("CLERK_PUBLISHABLE_KEY", os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", ""))
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    class Config:
        env_file = ROOT_DIR / ".env"
        extra = "allow"

settings = Settings()
