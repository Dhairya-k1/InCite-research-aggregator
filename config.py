import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Research Platform API"
    VERSION: str = "1.0.0"
    
    # MySQL Database Connection (falls back to SQLite for instant local runs)
    # MySQL format: mysql+asyncmy://user:password@localhost:3306/research_platform
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./research_platform.db"
    )
    DB_ECHO: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
